"""
RH_Config Node - Configuration node for RunningHub API
Simplified configuration with clear parameter names
"""

import json
import os

class RH_Config:
    """
    Configuration node for RunningHub API credentials and settings.
    This node stores your API key and workflow/app ID for use by other nodes.
    If api_key or base_url are empty, they will be loaded from config.json file.
    """

    @staticmethod
    def load_config_file():
        """
        Load configuration from config.json file

        Returns:
            dict: Configuration dictionary or empty dict if file not found
        """
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✓ Loaded configuration from {config_path}")
                    return config
            except Exception as e:
                print(f"⚠️ Error loading config.json: {e}")
                return {}
        else:
            print(f"ℹ️ No config.json found at {config_path}")
            return {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Your RunningHub API key (leave empty to load from config.json)"
                }),
                "workflow_or_app_id": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Workflow ID or AI App ID from RunningHub"
                }),
                "base_url": ("STRING", {
                    "default": "https://www.runninghub.cn",
                    "multiline": False,
                    "tooltip": "RunningHub API base URL (leave empty to load from config.json)"
                }),
            },
            "optional": {
                "is_ai_app": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable this if calling an AI App instead of a workflow"
                }),
            }
        }
    
    RETURN_TYPES = ("RH_CONFIG",)
    RETURN_NAMES = ("config",)
    FUNCTION = "create_config"
    CATEGORY = "Ken-Chen/RH-API"
    
    def create_config(self, api_key, workflow_or_app_id, base_url, is_ai_app=False):
        """
        Create configuration dictionary for RunningHub API

        Args:
            api_key: Your RunningHub API key (if empty, loads from config.json)
            workflow_or_app_id: Workflow ID or AI App ID
            base_url: API base URL (if empty, loads from config.json)
            is_ai_app: Whether this is an AI App (True) or workflow (False)

        Returns:
            Configuration dictionary
        """
        # Load configuration from file if needed
        file_config = self.load_config_file()

        # Node inputs have the highest priority. Use file config as a fallback.
        final_api_key = api_key.strip() if api_key and api_key.strip() else file_config.get("api_key", "")
        final_base_url = base_url.strip() if base_url and base_url.strip() else file_config.get("base_url", "https://www.runninghub.cn")
        final_workflow_id = workflow_or_app_id.strip() if workflow_or_app_id and workflow_or_app_id.strip() else file_config.get("workflow_or_app_id", "")

        # Validate required fields
        if not final_api_key:
            raise ValueError("API key is required. Provide it in the node or in config.json.")

        if not final_workflow_id:
            raise ValueError("Workflow ID or AI App ID is required. Provide it in the node or in config.json.")

        config = {
            "api_key": final_api_key,
            "workflow_or_app_id": final_workflow_id,
            "base_url": final_base_url,
            "is_ai_app": is_ai_app,
        }

        # Show where values came from
        api_source = "node input" if (api_key and api_key.strip()) else "config.json"
        base_url_source = "node input" if (base_url and base_url.strip()) else "config.json"
        workflow_id_source = "node input" if (workflow_or_app_id and workflow_or_app_id.strip()) else "config.json"

        print(f"✓ RH Config created: {'AI App' if is_ai_app else 'Workflow'} ID={final_workflow_id}")
        print(f"  API Key: loaded from {api_source}")
        print(f"  Workflow ID: loaded from {workflow_id_source}")
        print(f"  Base URL: {final_base_url} (from {base_url_source})")

        return (config,)

