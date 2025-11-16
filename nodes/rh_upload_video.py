"""
RH_UploadVideo Node - Upload videos to RunningHub
Simplified video upload
"""

import os
import folder_paths
from .rh_utils import upload_file_to_rh


class RH_UploadVideo:
    """
    Upload video file to RunningHub and get filename for use in workflows.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Common field names for video inputs
        field_names = [
            "video",          # Video input
            "init_video",     # Initial video
            "reference",      # Reference video
            "custom",         # Custom field name
        ]

        return {
            "required": {
                "config": ("RH_CONFIG", {
                    "tooltip": "RunningHub configuration from RH_Config node"
                }),
                "video": ("VIDEO", {
                    "tooltip": "Video input from Load_AF_Video or other video nodes"
                }),
            },
            "optional": {
                "node_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Node ID to set parameter (leave empty to skip parameter setting)"
                }),
                "field_name": (field_names, {
                    "default": "video",
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
    
    def upload(self, config, video, node_id="", field_name="video", custom_field_name="", previous_params=None):
        """
        Upload video to RunningHub and optionally set parameter

        Args:
            config: Configuration from RH_Config node
            video: VIDEO object from Load_AF_Video or video path string
            node_id: Node ID to set parameter (optional)
            field_name: Field name to set (optional)
            custom_field_name: Custom field name (optional)
            previous_params: Previous parameter list (optional)

        Returns:
            Tuple of (filename, params)
        """
        print("📤 Uploading video to RunningHub...")

        # Validate config
        if not isinstance(config, dict) or "api_key" not in config or "base_url" not in config:
            raise ValueError("Invalid config: must be from RH_Config node")

        if not video:
            raise ValueError("Video input is required")

        api_key = config["api_key"]
        base_url = config["base_url"]

        # Extract video path from VIDEO object or use string directly
        video_path = None

        # Handle different video input types
        if isinstance(video, str):
            # Direct path string (from Load_AF_Video)
            video_path = video
        elif hasattr(video, 'file_path'):
            # Video object with file_path attribute
            video_path = video.file_path
        elif hasattr(video, 'filename'):
            # Video object with filename attribute
            video_path = video.filename
        else:
            # Try to convert to string
            video_path = str(video)

        # Validate video path
        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"📹 Found video: {video_path}")

        # Upload using the utility function
        try:
            with open(video_path, 'rb') as f:
                filename = upload_file_to_rh(
                    api_key=api_key,
                    base_url=base_url,
                    file_buffer=f,
                    file_name=os.path.basename(video_path),
                    content_type='application/octet-stream',  # Generic content type
                    file_type='video'
                )
        except Exception as e:
            raise Exception(f"Failed to upload video: {e}")

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

