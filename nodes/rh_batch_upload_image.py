"""
RH_MultiUploadImage Node - Upload multiple images for batch execution.
"""

import torch
import numpy as np
from PIL import Image
import io

from .rh_utils import upload_file_to_rh

class RH_BatchUploadImage:
    """
    A node to upload up to 8 images to RunningHub for batch execution.
    Each image will be treated as a separate run.
    """

    MAX_UPLOADS = 8

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "config": ("RH_CONFIG",),
                "node_id": ("STRING", {"multiline": False, "default": ""}),
                "field_name": (["image", "control_image", "mask"],),
            },
            "optional": {}
        }
        for i in range(1, cls.MAX_UPLOADS + 1):
            inputs["optional"][f"image_{i}"] = ("IMAGE",)

        return inputs

    RETURN_TYPES = ("RH_PARAM_BUNDLE",)
    FUNCTION = "upload_batch"
    CATEGORY = "Ken-Chen/RH-API"

    def upload_batch(self, config, node_id, field_name, **kwargs):
        api_key = config.get("api_key")
        base_url = config.get("base_url")
        batch_bundle = []

        if not node_id:
            print("[Error] RH_BatchUploadImage: 'node_id' is required.")
            return ([],)

        for i in range(1, self.MAX_UPLOADS + 1):
            image_tensor = kwargs.get(f"image_{i}")
            if image_tensor is not None:
                # Convert tensor to PIL Image
                img_np = image_tensor.cpu().numpy()
                img_pil = Image.fromarray((img_np.squeeze(0) * 255).astype(np.uint8))

                buffer = io.BytesIO()
                img_pil.save(buffer, format='PNG')

                rh_file_path = upload_file_to_rh(
                    api_key=api_key, base_url=base_url, file_buffer=buffer, # Pass the buffer object directly
                    file_name=f"batch_upload_{i}.png", content_type='image/png', file_type='image'
                )

                if rh_file_path:
                    param = {"nodeId": node_id, "fieldName": field_name, "fieldValue": rh_file_path}
                    # Each param set is a list of dicts for one run. Here, it's just one param.
                    batch_bundle.append([param])
                else:
                    print(f"[Error] Failed to upload image {i}. Skipping this run.")

        if not batch_bundle:
            print("[Warning] RH_BatchUploadImage: No images were processed.")
            return ([],)

        print(f"[Info] Bundled {len(batch_bundle)} runs for batch execution.")
        return (batch_bundle,)
