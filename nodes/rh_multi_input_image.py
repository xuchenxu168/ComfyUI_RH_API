"""
RH_MultiInputImage Node - Upload multiple images for a single run.
"""

import torch
import numpy as np
from PIL import Image
import io

from .rh_utils import upload_file_to_rh

class RH_MultiInputImage:
    """
    A node to upload up to 8 images to RunningHub for a single execution.
    Each image can have a different node_id and field_name.
    """

    MAX_UPLOADS = 8

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "config": ("RH_CONFIG",),
            },
            "optional": {
                "previous_params": ("RH_PARAMS",)
            }
        }
        for i in range(1, cls.MAX_UPLOADS + 1):
            inputs["optional"][f"image_{i}"] = ("IMAGE",)
            inputs["optional"][f"node_id_{i}"] = ("STRING", {"multiline": False, "default": ""})
            inputs["optional"][f"field_name_{i}"] = (["image", "control_image", "mask"],)
        
        return inputs

    RETURN_TYPES = ("RH_PARAMS",)
    FUNCTION = "upload_single_run"
    CATEGORY = "Ken-Chen/RH-API"

    def upload_single_run(self, config, previous_params=None, **kwargs):
        api_key = config.get("api_key")
        base_url = config.get("base_url")

        # Initialize with previous params if they exist
        params_list = []
        if previous_params:
            params_list.extend(previous_params)

        new_params_count = 0
        for i in range(1, self.MAX_UPLOADS + 1):
            image_tensor = kwargs.get(f"image_{i}")
            node_id = kwargs.get(f"node_id_{i}")
            field_name = kwargs.get(f"field_name_{i}")

            if image_tensor is not None:
                if not node_id or not str(node_id).strip():
                    print(f"[Error] RH_MultiInputImage: Image_{i} is connected, but its node_id_{i} is missing. This input will be skipped.")
                    continue

                img_np = image_tensor.cpu().numpy()
                img_pil = Image.fromarray((img_np.squeeze(0) * 255).astype(np.uint8))
                buffer = io.BytesIO()
                img_pil.save(buffer, format='PNG')

                rh_file_path = upload_file_to_rh(
                    api_key=api_key, base_url=base_url, file_buffer=buffer,
                    file_name=f"multi_input_{i}.png", content_type='image/png', file_type='image'
                )

                if rh_file_path:
                    param = {"nodeId": str(node_id).strip(), "fieldName": field_name, "fieldValue": rh_file_path}
                    params_list.append(param)
                    new_params_count += 1
                    print(f"[Info] RH_MultiInputImage: Prepared image_{i} for node_id: {node_id}")
                else:
                    print(f"[Error] RH_MultiInputImage: Failed to upload image {i} for node {node_id}. Skipping.")

        if new_params_count == 0 and not previous_params:
            print("[Warning] RH_MultiInputImage: No new images were processed and no previous params were provided.")
            return ([],)

        print(f"[Info] RH_MultiInputImage: Bundled {len(params_list)} total parameters ({new_params_count} from this node). ")
        return (params_list,)
