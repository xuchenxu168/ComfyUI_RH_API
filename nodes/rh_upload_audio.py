"""
RH_UploadAudio Node - Upload audio files to RunningHub
"""

import os
import folder_paths
from .rh_utils import upload_file_to_rh

class RH_UploadAudio:
    """
    Accepts an audio file path, uploads it to RunningHub, and returns the server filename.
    """

    @classmethod
    def INPUT_TYPES(cls):
        field_names = [
            "audio", "init_audio", "reference", "custom",
        ]
        return {
            "required": {
                "config": ("RH_CONFIG", {}),
                "audio_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "node_id": ("STRING", {"default": ""}),
                "field_name": (field_names, {"default": "audio"}),
                "custom_field_name": ("STRING", {"default": ""}),
                "previous_params": ("RH_PARAMS", {"default": None}),
            }
        }

    RETURN_TYPES = ("STRING", "RH_PARAMS")
    RETURN_NAMES = ("filename", "params")
    FUNCTION = "upload"
    CATEGORY = "Ken-Chen/RH-API"

    def upload(self, config, audio_path, node_id="", field_name="audio", custom_field_name="", previous_params=None):
        if not audio_path or not isinstance(audio_path, str) or not os.path.exists(audio_path):
            print("RH_UploadAudio: No valid audio path provided. Skipping upload.")
            return ("", previous_params if previous_params else [])

        if not isinstance(config, dict) or "api_key" not in config or "base_url" not in config:
            raise ValueError("Invalid config: must be from RH_Config node")

        print(f"📤 Uploading audio from path: {audio_path}")
        api_key = config["api_key"]
        base_url = config["base_url"]

        try:
            with open(audio_path, 'rb') as f:
                filename = upload_file_to_rh(
                    api_key=api_key,
                    base_url=base_url,
                    file_buffer=f,
                    file_name=os.path.basename(audio_path),
                    content_type='application/octet-stream',
                    file_type='audio'
                )
        except Exception as e:
            raise Exception(f"Failed to upload audio: {e}")

        params = previous_params if previous_params else []
        if node_id and node_id.strip():
            actual_field_name = custom_field_name.strip() if field_name == "custom" else field_name
            if not actual_field_name:
                 print("⚠ Warning: field_name is 'custom' but custom_field_name is empty. Skipping param.")
            else:
                new_param = {
                    "nodeId": str(node_id).strip(),
                    "fieldName": actual_field_name.strip(),
                    "fieldValue": filename
                }
                params.append(new_param)
                print(f"✓ RH Param added: Node {node_id}.{actual_field_name} = {filename}")

        return (filename, params)
