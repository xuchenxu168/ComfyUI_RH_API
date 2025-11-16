"""
RH_UploadImage Node - Upload images to RunningHub
Simplified image upload with automatic format handling
"""

import torch
import numpy as np
from PIL import Image
from io import BytesIO
from .rh_utils import upload_file_to_rh


class RH_UploadImage:
    """
    Upload image to RunningHub and get filename for use in workflows.
    Automatically handles image format conversion and size limits.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Common field names for image inputs
        field_names = [
            "image",          # Image input
            "init_image",     # Initial image
            "control_image",  # ControlNet image
            "mask",           # Mask (if uploading as image)
            "reference",      # Reference image
            "custom",         # Custom field name
        ]

        return {
            "required": {
                "config": ("RH_CONFIG", {
                    "tooltip": "RunningHub configuration from RH_Config node"
                }),
                "image": ("IMAGE", {
                    "tooltip": "Image to upload"
                }),
            },
            "optional": {
                "node_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Node ID to set parameter (leave empty to skip parameter setting)"
                }),
                "field_name": (field_names, {
                    "default": "image",
                    "tooltip": "Field name to set (only used if node_id is provided)"
                }),
                "custom_field_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Custom field name (only used when field_name is 'custom')"
                }),
                "previous_params": ("RH_PARAMS", {
                    "default": None,
                    "tooltip": "Connect previous params to chain parameters"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "RH_PARAMS")
    RETURN_NAMES = ("filename", "params")
    FUNCTION = "upload"
    CATEGORY = "Ken-Chen/RH-API"
    
    def upload(self, config, image, node_id="", field_name="image", custom_field_name="", previous_params=None):
        """
        Upload image to RunningHub and optionally set parameter

        Args:
            config: Configuration from RH_Config node
            image: Image tensor to upload
            node_id: Node ID to set parameter (optional)
            field_name: Field name to set (optional)
            custom_field_name: Custom field name (optional)
            previous_params: Previous parameter list (optional)

        Returns:
            Tuple of (filename, params)
        """
        print("📤 Uploading image to RunningHub...")

        # Validate config
        if not isinstance(config, dict) or "api_key" not in config or "base_url" not in config:
            raise ValueError("Invalid config: must be from RH_Config node")

        api_key = config["api_key"]
        base_url = config["base_url"]

        # Convert tensor to PIL Image
        pil_image = self._tensor_to_pil(image)
        print(f"📤 Image dimensions: {pil_image.width}W x {pil_image.height}H")

        # Convert to bytes
        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer_size = buffer.tell()
        buffer.seek(0)

        # Check size limit (10MB)
        max_size = 10 * 1024 * 1024
        if buffer_size > max_size:
            raise ValueError(f"Image size {buffer_size / 1024 / 1024:.2f}MB exceeds 10MB limit")

        print(f"📤 Image file size: {buffer_size / 1024 / 1024:.2f}MB")

        # Upload using the utility function
        try:
            filename = upload_file_to_rh(
                api_key=api_key,
                base_url=base_url,
                file_buffer=buffer,
                file_name="image.png",
                content_type="image/png",
                file_type="image"
            )
        except Exception as e:
            # Re-raise with a more specific context
            raise Exception(f"Failed to upload image: {e}")

        # Create parameter if node_id is provided
        params = previous_params if previous_params else []

        if node_id and node_id.strip():
            # Determine actual field name
            actual_field_name = field_name
            if field_name == "custom" and custom_field_name.strip():
                actual_field_name = custom_field_name.strip()
            elif field_name == "custom" and not custom_field_name.strip():
                print("⚠ Warning: field_name is 'custom' but custom_field_name is empty. Using 'custom' as field name.")

            # Add parameter
            new_param = {
                "nodeId": str(node_id).strip(),
                "fieldName": actual_field_name.strip(),
                "fieldValue": filename
            }
            params.append(new_param)
            print(f"✓ RH Param added: Node {node_id}.{actual_field_name} = {filename}")

        return (filename, params)
    
    def _tensor_to_pil(self, tensor):
        """Convert ComfyUI image tensor to PIL Image"""
        # Handle batch dimension
        if tensor.ndim == 4:
            tensor = tensor[0]
        
        # Convert to numpy
        img_np = tensor.cpu().numpy()
        
        # Ensure [H, W, C] format
        if img_np.shape[0] in [1, 3, 4]:
            img_np = np.transpose(img_np, (1, 2, 0))
        
        # Convert to uint8
        if img_np.dtype == np.float32 or img_np.dtype == np.float64:
            img_np = (img_np * 255).astype(np.uint8)
        
        # Determine mode
        if img_np.shape[2] == 1:
            img_np = img_np.squeeze(-1)
            mode = 'L'
        elif img_np.shape[2] == 3:
            mode = 'RGB'
        elif img_np.shape[2] == 4:
            mode = 'RGBA'
        else:
            raise ValueError(f"Unsupported channel count: {img_np.shape[2]}")
        
        return Image.fromarray(img_np, mode)

