"""
RH_UploadMask Node - Upload mask images to RunningHub
Supports uploading mask/alpha channel images for inpainting and masking operations
"""

import torch
import numpy as np
from PIL import Image
from io import BytesIO
from .rh_utils import upload_file_to_rh


class RH_UploadMask:
    """
    📤 Upload mask images to RunningHub for inpainting/masking operations.
    Automatically converts images to grayscale masks.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Unified field names for both image and mask inputs
        unified_field_names = [
            "image",
            "mask",
            "input_image",
            "source_image",
            "original_image",
            "inpaint_mask",
            "alpha_mask",
            "control_mask",
            "custom",
        ]

        return {
            "required": {
                "config": ("RH_CONFIG", {
                    "tooltip": "RunningHub configuration from RH_Config node"
                }),
                "mask": ("MASK", {
                    "tooltip": "Mask tensor to upload (will be converted to grayscale)"
                }),
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "Optional: Image to upload along with mask"
                }),
                "node_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Node ID to set parameters (leave empty to skip parameter setting)"
                }),
                "mask_field_name": (unified_field_names, {
                    "default": "mask",
                    "tooltip": "Field name for mask parameter"
                }),
                "custom_mask_field_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Custom mask field name (only used when mask_field_name is 'custom')"
                }),
                "image_field_name": (unified_field_names, {
                    "default": "image",
                    "tooltip": "Field name for image parameter (only used if image is provided)"
                }),
                "custom_image_field_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Custom image field name (only used when image_field_name is 'custom')"
                }),
                "previous_params": ("RH_PARAMS", {
                    "default": None,
                    "tooltip": "Connect previous params to chain parameters"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "RH_PARAMS")
    RETURN_NAMES = ("mask_hash", "image_hash", "params")
    FUNCTION = "upload_mask"
    CATEGORY = "Ken-Chen/RH-API"
    
    def upload_mask(self, config, mask, image=None, node_id="", mask_field_name="mask", custom_mask_field_name="",
                    image_field_name="image", custom_image_field_name="", previous_params=None):
        """
        Upload mask and optionally image to RunningHub and set parameters

        Args:
            config: RH configuration dict
            mask: Mask tensor (B, H, W) or (H, W)
            image: Optional image tensor to upload
            node_id: Node ID to set parameters (optional)
            mask_field_name: Field name for mask (optional)
            custom_mask_field_name: Custom mask field name (optional)
            image_field_name: Field name for image (optional)
            custom_image_field_name: Custom image field name (optional)
            previous_params: Previous parameter list (optional)

        Returns:
            Tuple of (mask_hash, image_hash, params)
        """
        try:
            # Extract config
            api_key = config.get('api_key')
            base_url = config.get('base_url', 'https://www.runninghub.cn')
            
            if not api_key:
                raise ValueError("API key is required")
            
            # ========== Upload Mask ==========
            # Convert mask tensor to numpy
            if isinstance(mask, torch.Tensor):
                mask_np = mask.detach().cpu().numpy()
            else:
                mask_np = np.array(mask)
            
            print(f"📤 Original mask shape: {mask_np.shape}")
            
            # Handle batch dimension
            if mask_np.ndim == 3:
                # Take first mask from batch [B, H, W]
                mask_np = mask_np[0]
                print(f"📤 Removed batch dimension: {mask_np.shape}")
            
            # Ensure mask is 2D [H, W]
            if mask_np.ndim != 2:
                raise ValueError(f"Mask must be 2D after batch removal, got shape: {mask_np.shape}")
            
            # Convert to 0-255 range
            if mask_np.max() <= 1.0:
                mask_np = (mask_np * 255).astype(np.uint8)
            else:
                mask_np = mask_np.astype(np.uint8)
            
            # Create PIL Image from mask (grayscale - single channel)
            mask_pil = Image.fromarray(mask_np, mode='L')
            print(f"📤 Created PIL mask image: {mask_pil.size} (width x height), mode: {mask_pil.mode}")
            print(f"📤 Mask is single-channel grayscale (required by Qwen Edit nodes)")
            
            # Save mask to BytesIO buffer
            mask_buffer = BytesIO()
            mask_pil.save(mask_buffer, format='PNG')
            mask_buffer_size = mask_buffer.tell()
            mask_buffer.seek(0)
            
            # Print size
            mask_size_mb = mask_buffer_size / (1024 * 1024)
            print(f"📤 Mask size: {mask_size_mb:.2f} MB")
            
            # Check size limit (10MB)
            max_size_bytes = 10 * 1024 * 1024
            if mask_buffer_size > max_size_bytes:
                raise Exception(f"Mask size {mask_size_mb:.2f}MB exceeds 10MB limit")
            
            # Upload mask
            try:
                mask_hash = upload_file_to_rh(
                    api_key=api_key,
                    base_url=base_url,
                    file_buffer=mask_buffer,
                    file_name="mask.png",
                    content_type="image/png",
                    file_type="image"
                )
                print(f"✅ Mask uploaded successfully: {mask_hash}")
            except Exception as e:
                raise Exception(f"Failed to upload mask: {e}")

            # ========== Upload Image (if provided) ==========
            image_hash = ""
            if image is not None:
                print(f"📤 Uploading image...")
                
                # Convert image tensor to numpy
                if isinstance(image, torch.Tensor):
                    image_np = image.detach().cpu().numpy()
                else:
                    image_np = np.array(image)
                
                print(f"📤 Original image shape: {image_np.shape}")
                
                # Handle batch dimension [B, H, W, C]
                if image_np.ndim == 4:
                    image_np = image_np[0]
                    print(f"📤 Removed batch dimension: {image_np.shape}")
                
                # Ensure image is 3D [H, W, C]
                if image_np.ndim != 3:
                    raise ValueError(f"Image must be 3D after batch removal, got shape: {image_np.shape}")
                
                # Convert to 0-255 range
                if image_np.max() <= 1.0:
                    image_np = (image_np * 255).astype(np.uint8)
                else:
                    image_np = image_np.astype(np.uint8)
                
                # Create PIL Image
                image_pil = Image.fromarray(image_np, mode='RGB')
                print(f"📤 Created PIL image: {image_pil.size} (width x height), mode: {image_pil.mode}")
                
                # Save image to BytesIO buffer
                image_buffer = BytesIO()
                image_pil.save(image_buffer, format='PNG')
                image_buffer_size = image_buffer.tell()
                image_buffer.seek(0)
                
                # Print size
                image_size_mb = image_buffer_size / (1024 * 1024)
                print(f"📤 Image size: {image_size_mb:.2f} MB")
                
                # Check size limit (10MB)
                if image_buffer_size > max_size_bytes:
                    raise Exception(f"Image size {image_size_mb:.2f}MB exceeds 10MB limit")
                
                # Upload image
                try:
                    image_hash = upload_file_to_rh(
                        api_key=api_key,
                        base_url=base_url,
                        file_buffer=image_buffer,
                        file_name="image.png",
                        content_type="image/png",
                        file_type="image"
                    )
                    print(f"✅ Image uploaded successfully: {image_hash}")
                except Exception as e:
                    raise Exception(f"Failed to upload image: {e}")

            # ========== Create Parameters ==========
            params = previous_params if previous_params else []

            if node_id and node_id.strip():
                node_id_str = str(node_id).strip()
                
                # Add mask parameter
                actual_mask_field = mask_field_name
                if mask_field_name == "custom" and custom_mask_field_name.strip():
                    actual_mask_field = custom_mask_field_name.strip()
                elif mask_field_name == "custom" and not custom_mask_field_name.strip():
                    print("⚠ Warning: mask_field_name is 'custom' but custom_mask_field_name is empty. Using 'custom' as field name.")

                mask_param = {
                    "nodeId": node_id_str,
                    "fieldName": actual_mask_field,
                    "fieldValue": mask_hash
                }
                params.append(mask_param)
                print(f"✓ RH Param added: Node {node_id_str}.{actual_mask_field} = {mask_hash}")
                
                # Add image parameter if image was uploaded
                if image_hash:
                    actual_image_field = image_field_name
                    if image_field_name == "custom" and custom_image_field_name.strip():
                        actual_image_field = custom_image_field_name.strip()
                    elif image_field_name == "custom" and not custom_image_field_name.strip():
                        print("⚠ Warning: image_field_name is 'custom' but custom_image_field_name is empty. Using 'custom' as field name.")
                    
                    image_param = {
                        "nodeId": node_id_str,
                        "fieldName": actual_image_field,
                        "fieldValue": image_hash
                    }
                    params.append(image_param)
                    print(f"✓ RH Param added: Node {node_id_str}.{actual_image_field} = {image_hash}")

            return (mask_hash, image_hash, params)

        except Exception as e:
            print(f"❌ Error uploading mask: {str(e)}")
            raise


NODE_CLASS_MAPPINGS = {
    "RH_UploadMask": RH_UploadMask
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RH_UploadMask": "📤 RH Upload Mask"
}

