"""
RH_UploadFile Node - A generic file uploader for RunningHub
"""

import os
import mimetypes
import json
from .rh_utils import upload_file_to_rh

class RH_UploadFile:
    """
    A node to upload any file to RunningHub.
    It returns a parameter string that can be used in RH_Execute.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("RH_CONFIG", ),
                "node_id": ("STRING", {"multiline": False, "default": ""}),
                "field_name": (["text", "image", "audio", "video", "latent", "mask", "file"],),
                "file_path": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("RH_PARAM",)
    FUNCTION = "upload"
    CATEGORY = "Ken-Chen/RH-API"

    def upload(self, config, node_id, field_name, file_path):
        """
        Uploads the specified file and returns a parameter string.
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        api_key = config.get("api_key")
        base_url = config.get("base_url")

        # Get file details
        file_name = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream" # Generic binary type

        # Read file into buffer
        with open(file_path, 'rb') as f:
            file_buffer = f.read()

        # Upload using the utility function
        rh_file_path = upload_file_to_rh(
            api_key=api_key,
            base_url=base_url,
            file_buffer=file_buffer,
            file_name=file_name,
            content_type=content_type,
            file_type='file' # Generic file type for logging
        )

        if not rh_file_path:
            raise Exception("File upload failed. Check logs for details.")

        # Create the parameter dictionary
        param = [{
            "nodeId": node_id,
            "fieldName": field_name,
            "fieldValue": rh_file_path
        }]

        print(f"✓ RH Param added: Node {node_id}.{field_name} = {rh_file_path}")
        return (param,)

