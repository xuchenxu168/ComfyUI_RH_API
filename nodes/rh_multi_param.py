"""
RH_MultiParams Node - Set multiple parameters for a single run.
"""

class RH_MultiParams:
    """
    A node to set up to 4 different parameters for a single RunningHub execution.
    This helps to reduce the number of RH_Param nodes in complex workflows.
    """

    MAX_PARAMS = 4

    @classmethod
    def INPUT_TYPES(cls):
        # Common field names for RunningHub workflows (same as RH_Param)
        field_names = [
            "text",           # Text prompts
            "image",          # Image inputs
            "video",          # Video inputs
            "mask",           # Mask inputs
            "seed",           # Random seed
            "steps",          # Sampling steps
            "cfg",            # CFG scale
            "sampler_name",   # Sampler name
            "scheduler",      # Scheduler
            "denoise",        # Denoise strength
            "width",          # Image width
            "height",         # Image height
            "batch_size",     # Batch size
            "model",          # Model name
            "vae",            # VAE name
            "lora",           # LoRA name
            "control_net",    # ControlNet
            "strength",       # Strength parameter
            "scale",          # Scale parameter
            "custom",         # Custom field (user input)
        ]

        inputs = {
            "required": {},
            "optional": {
                "previous_params": ("RH_PARAMS", {
                    "tooltip": "Connect previous RH_Param or RH_MultiParams node to chain parameters"
                })
            }
        }

        # Dynamically create 4 sets of inputs with dropdown for field_name
        for i in range(1, cls.MAX_PARAMS + 1):
            inputs["optional"][f"node_id_{i}"] = ("STRING", {
                "multiline": False,
                "default": "",
                "tooltip": f"Node ID in the workflow for parameter {i}"
            })
            inputs["optional"][f"field_name_{i}"] = (field_names, {
                "default": "text",
                "tooltip": f"Field name to modify for parameter {i} - select from common types or use 'custom'"
            })
            inputs["optional"][f"field_value_{i}"] = ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": f"Value to set for parameter {i}"
            })
            inputs["optional"][f"custom_field_name_{i}"] = ("STRING", {
                "multiline": False,
                "default": "",
                "tooltip": f"Custom field name for parameter {i} (only used when field_name_{i} is 'custom')"
            })

        return inputs

    RETURN_TYPES = ("RH_PARAMS",)
    FUNCTION = "bundle_params"
    CATEGORY = "Ken-Chen/RH-API"

    def bundle_params(self, previous_params=None, **kwargs):
        """
        Bundle multiple parameters into a single list.

        Args:
            previous_params: Previous parameter list (for chaining)
            **kwargs: Dynamic keyword arguments containing node_id, field_name, field_value,
                     and custom_field_name for each parameter slot

        Returns:
            Updated parameter list
        """
        # Initialize with previous params if they exist
        params_list = []
        if previous_params:
            params_list.extend(previous_params)

        new_params_count = 0
        for i in range(1, self.MAX_PARAMS + 1):
            node_id = kwargs.get(f"node_id_{i}", "")
            field_name = kwargs.get(f"field_name_{i}", "")
            field_value = kwargs.get(f"field_value_{i}", "")
            custom_field_name = kwargs.get(f"custom_field_name_{i}", "")

            # Only create a parameter if both node_id and field_name are provided
            if node_id and field_name:
                # Use custom field name if field_name is 'custom' and custom_field_name is provided
                actual_field_name = field_name
                if field_name == "custom" and custom_field_name.strip():
                    actual_field_name = custom_field_name.strip()
                elif field_name == "custom" and not custom_field_name.strip():
                    print(f"⚠ Warning: Slot {i} field_name is 'custom' but custom_field_name_{i} is empty. Using 'custom' as field name.")

                param = {
                    "nodeId": str(node_id).strip(),
                    "fieldName": actual_field_name.strip(),
                    "fieldValue": field_value
                }
                params_list.append(param)
                new_params_count += 1

                # Show truncated value in log
                value_preview = str(field_value)[:50] + ('...' if len(str(field_value)) > 50 else '')
                print(f"✓ RH MultiParams: Added param {i} - Node {node_id}.{actual_field_name} = {value_preview}")
            elif node_id or field_name or field_value:
                # Warn the user if some fields are filled but not enough to create a param
                if not (node_id == "" and field_name == "" and field_value == ""):
                    print(f"⚠ Warning: Slot {i} has incomplete data and will be skipped.")

        if new_params_count == 0 and not previous_params:
            print("⚠ Warning: RH_MultiParams - No new parameters were set and no previous params were provided.")
            return ([],)

        print(f"✓ RH MultiParams: Bundled {len(params_list)} total parameters ({new_params_count} from this node).")
        return (params_list,)

