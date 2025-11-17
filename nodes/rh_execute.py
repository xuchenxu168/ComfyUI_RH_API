"""
RH_Execute Node - Execute RunningHub workflows and AI apps
Simplified execution with automatic progress tracking and output handling
"""

import requests
import time
import json

# Import shared logic from rh_utils
from .rh_utils import _monitor_task, _get_outputs, _create_placeholder_image

try:
    import comfy.utils
    COMFY_AVAILABLE = True
except ImportError:
    COMFY_AVAILABLE = False


class RH_Execute:
    """
    Execute RunningHub workflows or AI apps.
    Handles task creation, monitoring, and output processing automatically.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("RH_CONFIG", {
                    "tooltip": "RunningHub configuration from RH_Config node"
                }),
                "timeout": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 3600,
                    "tooltip": "Maximum time to wait for task completion (seconds)"
                }),
            },
            "optional": {
                "params": ("RH_PARAMS", {
                    "default": None,
                    "tooltip": "Parameters from RH_Param nodes (optional)"
                }),
                "use_high_performance": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Use RTX 4090 48GB instance (costs more credits)"
                }),
                "save_to_local": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Save images and videos to ComfyUI output directory"
                }),
                "output_prefix": ("STRING", {
                    "default": "RH",
                    "multiline": False,
                    "tooltip": "Prefix for saved files (e.g., 'RH' -> 'RH_001.png')"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "AUDIO", "VIDEO", "LATENT", "STRING")
    RETURN_NAMES = ("images", "video_frames", "text", "audio", "video", "latent", "task_id")
    FUNCTION = "execute"
    CATEGORY = "Ken-Chen/RH-API"
    OUTPUT_NODE = True
    
    def execute(self, config, params=None, timeout=600, use_high_performance=False,
                save_to_local=True, output_prefix="RH"):
        """
        Execute RunningHub workflow or AI app

        Args:
            config: Configuration from RH_Config node
            params: Parameters from RH_Param nodes
            timeout: Maximum execution time
            use_high_performance: Use high-performance instance
            save_to_local: Save outputs to local directory
            output_prefix: Prefix for saved files

        Returns:
            Tuple of (images, video_frames, text, audio, video)
        """
        print("=" * 60)
        print("🚀 Starting RunningHub Execution")
        print("=" * 60)

        # Validate config
        self._validate_config(config)
        
        # Create task
        task_id = self._create_task(config, params or [], use_high_performance)
        print(f"✓ Task created: {task_id}")
        
        # Monitor task using shared utility function
        _monitor_task(task_id, config, timeout)
        print("✓ Task completed")

        # Get and process outputs using shared utility function
        outputs = _get_outputs(task_id, config, save_to_local, output_prefix)
        print("✓ Outputs processed")

        # Handle case where task completes with no output
        if outputs is None:
            outputs = (
                _create_placeholder_image("No image output"),
                _create_placeholder_image("No video output"),
                "",
                None,
                None
            )

        print("=" * 60)
        print("✅ Execution completed successfully")
        print("=" * 60)

        return outputs + (task_id,)



    def _validate_config(self, config):
        """Validate configuration"""
        if not isinstance(config, dict):
            raise ValueError("Invalid config: must be a dictionary from RH_Config node")

        required_fields = ["api_key", "workflow_or_app_id", "base_url"]
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"Missing required config field: {field}")

    def _create_task(self, config, params, use_high_performance):
        """Create task on RunningHub"""
        api_key = config["api_key"]
        base_url = config["base_url"]
        workflow_or_app_id = config["workflow_or_app_id"]
        is_ai_app = config.get("is_ai_app", False)

        # Choose endpoint based on task type
        if is_ai_app:
            url = f"{base_url}/task/openapi/ai-app/run"
            payload = {
                "webappId": int(workflow_or_app_id),
                "apiKey": api_key,
                "nodeInfoList": params,
            }
        else:
            url = f"{base_url}/task/openapi/create"
            payload = {
                "workflowId": workflow_or_app_id,
                "apiKey": api_key,
                "nodeInfoList": params,
            }

        # Add instance type if high performance requested
        if use_high_performance:
            payload["instanceType"] = "plus"


        # Send request with retry
        max_retries = 5
        for attempt in range(max_retries):
            try:
                print(f"Creating task (attempt {attempt + 1}/{max_retries})...")
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
                response.raise_for_status()

                result = response.json()

                if result.get("code") == 0:
                    data = result.get("data", {})
                    task_id = data.get("taskId")

                    if not task_id:
                        raise ValueError("No taskId in response")

                    # WebSocket disabled - HTTP polling is more reliable
                    # WebSocket can cause blocking issues with certain proxy configurations
                    # HTTP polling works perfectly and is more stable
                    print("ℹ Using HTTP polling for task monitoring (WebSocket disabled for stability)")

                    return task_id
                else:
                    error_msg = result.get('msg', 'Unknown error')

                    # Check for business errors that should not be retried
                    non_retryable_errors = [
                        "WORKFLOW_NOT_SAVED_OR_NOT_RUNNING",
                        "WORKFLOW_NOT_FOUND",
                        "INVALID_WORKFLOW_ID",
                        "INVALID_API_KEY",
                        "INSUFFICIENT_BALANCE",
                    ]

                    if any(err in error_msg for err in non_retryable_errors):
                        # These are business errors, not network errors - don't retry
                        print(f"❌ Business error (not retrying): {error_msg}")

                        # Provide helpful error messages
                        if "WORKFLOW_NOT_SAVED_OR_NOT_RUNNING" in error_msg:
                            raise Exception(
                                f"Workflow error: {error_msg}\n"
                                f"Please check:\n"
                                f"1. Workflow ID '{workflow_or_app_id}' exists on RunningHub\n"
                                f"2. Workflow is saved\n"
                                f"3. Workflow status is set to 'Running' (not Draft)\n"
                                f"4. You have access to this workflow"
                            )
                        elif "INVALID_API_KEY" in error_msg:
                            raise Exception(f"Invalid API key. Please check your RH_Config node.")
                        elif "INSUFFICIENT_BALANCE" in error_msg:
                            raise Exception(f"Insufficient balance. Please top up your RunningHub account.")
                        else:
                            raise Exception(f"API error: {error_msg}")

                    # For other errors, allow retry
                    raise Exception(f"API error: {error_msg}")

            except Exception as e:
                error_str = str(e)

                # Don't retry business errors
                if "Workflow error:" in error_str or "Invalid API key" in error_str or "Insufficient balance" in error_str:
                    raise

                # Retry network errors
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to create task: {e}")
                print(f"Retry in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)

        raise Exception("Failed to create task after all retries")











