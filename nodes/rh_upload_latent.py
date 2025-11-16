"""
RH_UploadLatent Node - Upload a latent tensor as a .safetensors file
"""

import os
import torch
import tempfile
import json
from .rh_utils import upload_file_to_rh

# Safetensors is a core dependency of ComfyUI, so it should be available
from safetensors.torch import save_file

class RH_UploadLatent:
    """
    A node to upload a latent tensor to RunningHub by saving it as a temporary
    .safetensors file.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("RH_CONFIG", ),
                "latent": ("LATENT", ),
                "node_id": ("STRING", {"multiline": False, "default": ""}),
                "field_name": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("RH_PARAM",)
    FUNCTION = "upload"
    CATEGORY = "Ken-Chen/RH-API"

    def upload(self, config, latent, node_id, field_name):
        """
        Saves the latent to a temporary file, uploads it, and returns a parameter string.
        """
        api_key = config.get("api_key")
        base_url = config.get("base_url")

        # Create a temporary file to save the latent tensor
        with tempfile.NamedTemporaryFile(delete=False, suffix=".safetensors") as tmp:
            tmp_path = tmp.name
            # The `latent` object is a dictionary, e.g., {'samples': tensor}
            save_file(latent, tmp_path)

        try:
            # Read the file content into a buffer
            with open(tmp_path, 'rb') as f:
                file_buffer = f.read()

            # Upload the file using the shared utility function
            rh_file_path = upload_file_to_rh(
                api_key=api_key,
                base_url=base_url,
                file_buffer=file_buffer,
                file_name="latent.safetensors",
                content_type="application/octet-stream",
                file_type='latent'
            )

            if not rh_file_path:
                raise Exception("Latent upload failed. Check logs for details.")

        finally:
            # Ensure the temporary file is deleted
            os.unlink(tmp_path)

        # Create the parameter dictionary
        param = [{
            "nodeId": node_id,
            "fieldName": field_name,
            "fieldValue": rh_file_path
        }]

        print(f"✓ RH Param added: Node {node_id}.{field_name} = {rh_file_path}")
        return (param,)

