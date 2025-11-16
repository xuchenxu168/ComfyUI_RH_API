"""
RH_Download Node - Download results from a RunningHub task
"""

import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
from .rh_utils import _monitor_task, _get_outputs, _create_placeholder_image, _create_placeholder_latent, _create_placeholder_audio

class RH_Download:
    """
    Downloads results from a given RunningHub task ID.
    This allows for separating task execution from result retrieval.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("RH_CONFIG", {
                    "tooltip": "RunningHub configuration from RH_Config node"
                }),
                "task_id": ("STRING", {
                    "multiline": False,
                    "tooltip": "Task ID from RH_Execute node"
                }),
                "timeout": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 3600,
                    "tooltip": "Maximum time to wait for task completion (seconds)"
                }),
            },
            "optional": {
                "save_to_local": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Save images and videos to ComfyUI output directory"
                }),
                "output_prefix": ("STRING", {
                    "default": "RH_DL",
                    "multiline": False,
                    "tooltip": "Prefix for saved files"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "AUDIO", "VIDEO", "LATENT")
    RETURN_NAMES = ("images", "video_frames", "text", "audio", "video", "latent")
    FUNCTION = "download"
    CATEGORY = "Ken-Chen/RH-API"
    OUTPUT_NODE = True

    def _process_single_task(self, task_id, config, timeout, save_to_local, output_prefix):
        """Processes a single task ID: monitors, downloads, and returns results."""
        try:
            print(f"  - Starting processing for task ID: {task_id}...")
            _monitor_task(task_id, config, timeout)
            outputs = _get_outputs(task_id, config, save_to_local, output_prefix)
            if outputs is None:
                raise Exception("Task completed with no output.")
            print(f"    ✓ Task {task_id} processed successfully.")
            return outputs
        except Exception as e:
            print(f"    ❌ Failed to process task {task_id}: {e}")
            return (
                _create_placeholder_image(f"Failed: {task_id}"),
                _create_placeholder_image("Failed"),
                f"ERROR: {e}",
                _create_placeholder_audio(),
                None,
                _create_placeholder_latent()
            )

    def download(self, config, task_id, timeout=600, save_to_local=True, output_prefix="RH_DL"):
        if not task_id or not task_id.strip():
            raise ValueError("Task ID is required.")

        if not isinstance(config, dict):
            raise ValueError("Invalid config: must be a dictionary from RH_Config node")
        required_fields = ["api_key", "base_url"]
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"Missing required config field: {field}")

        task_ids = [tid.strip() for tid in task_id.split(',') if tid.strip()]
        is_batch = len(task_ids) > 1

        print("\n" + "=" * 60)
        if is_batch:
            print(f"🚀 Starting Batch Download for {len(task_ids)} tasks in parallel...")
        else:
            print(f"🚀 Starting Download for Task ID: {task_id}")
        print("=" * 60)

        all_results = [None] * len(task_ids)

        if is_batch:
            with ThreadPoolExecutor(max_workers=min(10, len(task_ids))) as executor:
                future_to_index = {
                    executor.submit(self._process_single_task, tid, config, timeout, save_to_local, f"{output_prefix}_{i+1}"): i
                    for i, tid in enumerate(task_ids)
                }
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        all_results[index] = future.result()
                    except Exception as e:
                        print(f"    ❌ An unexpected exception occurred for task at index {index}: {e}")
                        all_results[index] = (
                            _create_placeholder_image(f"Failed: {task_ids[index]}"),
                            _create_placeholder_image("Failed"),
                            f"ERROR: {e}",
                            _create_placeholder_audio(),
                            None,
                            _create_placeholder_latent()
                        )
        else:
            all_results[0] = self._process_single_task(task_ids[0], config, timeout, save_to_local, output_prefix)

        # Aggregate results
        final_images = torch.cat([res[0] for res in all_results], dim=0)
        final_video_frames = torch.cat([res[1] for res in all_results], dim=0)
        final_text = "\n".join([res[2] for res in all_results])
        first_audio = next((res[3] for res in all_results if res[3] is not None), _create_placeholder_audio())
        first_video = next((res[4] for res in all_results if res[4] is not None), None)
        final_latents = {key: torch.cat([res[5][key] for res in all_results], dim=0) for key in all_results[0][5].keys()}

        print("\n" + "=" * 60)
        print(f"✅ Batch Download completed successfully.")
        print("=" * 60)

        return (final_images, final_video_frames, final_text, first_audio, first_video, final_latents)

