"""
RH_Param Node - Parameter configuration for RunningHub workflows
Simplified parameter setting with chainable design
"""

class RH_Param:
    """
    Parameter configuration node for RunningHub workflows.
    Set node parameters to customize workflow execution.
    Can be chained together to set multiple parameters.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Common field names for RunningHub workflows
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

        return {
            "required": {
                "node_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Node ID in the workflow (e.g., '3', '47')"
                }),
                "field_name": (field_names, {
                    "default": "text",
                    "tooltip": "Field name to modify - select from common types or use 'custom'"
                }),
                "field_value": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Value to set for the field"
                }),
            },
            "optional": {
                "previous_params": ("RH_PARAMS", {
                    "default": None,
                    "tooltip": "Connect previous RH_Param node to chain parameters"
                }),
                "custom_field_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Custom field name (only used when field_name is 'custom')"
                }),
            }
        }
    
    RETURN_TYPES = ("RH_PARAMS",)
    RETURN_NAMES = ("params",)
    FUNCTION = "add_param"
    CATEGORY = "Ken-Chen/RH-API"
    
    def add_param(self, node_id, field_name, field_value, previous_params=None, custom_field_name=""):
        """
        Add a parameter to the parameter list

        Args:
            node_id: Node ID in the workflow
            field_name: Field name to modify (from dropdown)
            field_value: Value to set
            previous_params: Previous parameter list (for chaining)
            custom_field_name: Custom field name (when field_name is 'custom')

        Returns:
            Updated parameter list
        """
        # Start with previous params or empty list
        params = previous_params if previous_params else []

        # Use custom field name if field_name is 'custom' and custom_field_name is provided
        actual_field_name = field_name
        if field_name == "custom" and custom_field_name.strip():
            actual_field_name = custom_field_name.strip()
        elif field_name == "custom" and not custom_field_name.strip():
            print("⚠ Warning: field_name is 'custom' but custom_field_name is empty. Using 'custom' as field name.")

        # Add new parameter
        new_param = {
            "nodeId": str(node_id).strip(),
            "fieldName": actual_field_name.strip(),
            "fieldValue": str(field_value)
        }

        params.append(new_param)

        print(f"✓ RH Param added: Node {node_id}.{actual_field_name} = {field_value[:50]}{'...' if len(str(field_value)) > 50 else ''}")

        return (params,)

