"""
RH_TaskManager Node - Manage RunningHub tasks
"""

from .rh_utils import get_task_status, cancel_task, _validate_config

class RH_TaskManager:
    """
    A node to manage tasks on RunningHub, such as checking status or cancelling.
    """

    ACTION_GET_STATUS = "Get Status"
    ACTION_CANCEL = "Cancel Task"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("RH_CONFIG", ),
                "task_id": ("STRING", {"multiline": False, "default": ""}),
                "action": ([cls.ACTION_GET_STATUS, cls.ACTION_CANCEL], ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "manage_task"
    CATEGORY = "Ken-Chen/RH-API"
    OUTPUT_NODE = True

    def manage_task(self, config, task_id, action):
        """
        Performs the selected action on the given task ID.
        """
        _validate_config(config)
        if not task_id or not task_id.strip():
            raise ValueError("Task ID is required.")

        print(f"Performing action '{action}' on task '{task_id}'...")
        result_message = ""

        try:
            if action == self.ACTION_GET_STATUS:
                status_info = get_task_status(config, task_id)
                result_message = f"Status for {task_id}: {status_info.get('taskStatus', 'Unknown')}"
                if 'error' in status_info:
                    result_message += f" - Error: {status_info['error']}"
                print(result_message)

            elif action == self.ACTION_CANCEL:
                success = cancel_task(config, task_id)
                if success:
                    result_message = f"Successfully requested cancellation for task {task_id}."
                else:
                    result_message = f"Failed to cancel task {task_id}. It may have already completed or failed."
                print(result_message)

        except Exception as e:
            result_message = f"An error occurred: {e}"
            print(f"❌ {result_message}")
            raise e

        return (result_message,)

