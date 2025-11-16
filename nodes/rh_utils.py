"""
RH Utility Nodes - Helper nodes for working with RunningHub outputs
"""

import torch
import requests
import time
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Dependency checks
try:
    import comfy.utils
    COMFY_AVAILABLE = True
except ImportError:
    COMFY_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import torchaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    from safetensors.torch import load
    SAFETENSORS_AVAILABLE = True
except ImportError:
    SAFETENSORS_AVAILABLE = False

def upload_file_to_rh(api_key, base_url, file_buffer, file_name, content_type, file_type):
    """
    Uploads a file to RunningHub with retry logic.

    Args:
        api_key (str): The API key for authentication.
        base_url (str): The base URL of the RunningHub API.
        file_buffer (BytesIO): The file content in a byte buffer.
        file_name (str): The name of the file to be sent.
        content_type (str): The MIME type of the file (e.g., 'image/png').
        file_type (str): The type of file for RunningHub API ('image', 'video', etc.).

    Returns:
        str: The filename returned by the API upon successful upload.

    Raises:
        Exception: If the upload fails after all retries.
    """
    url = f"{base_url}/task/openapi/upload"
    files = {'file': (file_name, file_buffer, content_type)}
    data = {
        'apiKey': api_key,
        'fileType': file_type,
    }

    max_retries = 5
    filename = None
    for attempt in range(max_retries):
        try:
            print(f"Upload attempt {attempt + 1}/{max_retries}...")
            # Rewind buffer before each attempt
            file_buffer.seek(0)
            response = requests.post(url, data=data, files=files, timeout=60)
            response.raise_for_status()

            result = response.json()

            if result.get('code') == 0:
                filename = result.get('data', {}).get('fileName')
                if filename:
                    print(f"✓ File uploaded successfully: {filename}")
                    return filename
                else:
                    raise ValueError("API response did not contain a fileName.")
            else:
                raise Exception(f"API returned an error: {result.get('msg')}")

        except Exception as e:
            print(f"Upload attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise Exception(f"Failed to upload file after {max_retries} attempts: {e}")

            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    # This line should not be reached if logic is correct, but as a safeguard:
    raise Exception("Failed to upload file and exhausted all retries.")


# --- Task Monitoring and Output Processing Logic ---
# These functions are moved from rh_execute.py to be shared with rh_download.py

def _check_task_status(task_id, api_key, base_url):
    """Check task status via HTTP"""
    url = f"{base_url}/task/openapi/outputs"
    payload = {
        "taskId": task_id,
        "apiKey": api_key
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()

        code = result.get("code")
        msg = result.get("msg", "")
        data = result.get("data")

        if msg == "APIKEY_TASK_IS_QUEUED":
            return {"taskStatus": "QUEUED"}

        if msg == "APIKEY_TASK_IS_RUNNING":
            return {"taskStatus": "RUNNING"}

        if code == 0 and isinstance(data, list) and data:
            return data

        if code == 0 and isinstance(data, list) and not data:
            return {"taskStatus": "completed_no_output"}

        if code == 0 and data is None:
            return {"taskStatus": "RUNNING"}

        if code != 0:
            error_details = msg
            if isinstance(data, dict):
                error_details = f"{msg}: {data.get('error', data)}"
            return {"taskStatus": "error", "error": error_details, "error_data": data}

        return {"taskStatus": "RUNNING"}

    except requests.exceptions.Timeout:
        return {"taskStatus": "RUNNING"} # Treat timeout as still running
    except requests.exceptions.RequestException as e:
        return {"taskStatus": "RUNNING"} # Treat network error as still running


def _monitor_task(task_id, config, timeout):
    """Monitor task until completion"""
    api_key = config["api_key"]
    base_url = config["base_url"]

    start_time = time.time()
    poll_interval = 5
    last_poll = 0
    last_status = None
    last_log_time = 0
    log_interval = 15

    print("Monitoring task...")
    print(f"Task URL: https://www.runninghub.cn/task/detail/{task_id}")

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Task timeout after {timeout} seconds")

        if time.time() - last_poll >= poll_interval:
            last_poll = time.time()
            status = _check_task_status(task_id, api_key, base_url)

            if isinstance(status, list):
                print(f"✓ Task completed successfully!")
                break
            elif isinstance(status, dict):
                task_status = status.get("taskStatus")

                if task_status != last_status:
                    print(f"[{int(elapsed)}s] Task status changed to: {task_status}")
                    last_status = task_status
                    last_log_time = time.time()
                elif time.time() - last_log_time > log_interval:
                    print(f"[{int(elapsed)}s] Task is still {task_status}...")
                    last_log_time = time.time()

                if task_status == "error":
                    error_msg = status.get('error', 'Unknown error')
                    raise Exception(f"Task failed on RunningHub server: {error_msg}")
            else:
                if time.time() - last_log_time > log_interval:
                    print(f"[{int(elapsed)}s] Unexpected status response. Retrying...")
                    last_log_time = time.time()

        time.sleep(0.5)


def _get_outputs(task_id, config, save_to_local, output_prefix):
    """Get and process task outputs"""
    api_key = config["api_key"]
    base_url = config["base_url"]

    max_retries = 30
    for attempt in range(max_retries):
        status = _check_task_status(task_id, api_key, base_url)

        if isinstance(status, list):
            return _process_outputs(status, save_to_local, output_prefix)

        if isinstance(status, dict):
            task_status = status.get("taskStatus")
            if task_status == "error":
                raise Exception(f"Task failed: {status.get('error')}")
            elif task_status == "completed_no_output":
                print("Task completed but produced no output.")
                return None # Return None for no output

        time.sleep(2)

    raise Exception("Timeout waiting for outputs")

def _download_and_process_file(output):
    """Downloads and processes a single file, returning the data and type."""
    file_url = output.get("fileUrl")
    file_type = output.get("fileType", "").lower()
    if not file_url:
        return None

    try:
        if file_type in ["png", "jpg", "jpeg", "webp", "bmp"]:
            data = _download_image(file_url)
            return {"type": "image", "data": data, "original_type": file_type} if data is not None else None
        elif file_type in ["mp4", "avi", "mov", "webm"]:
            frames = _extract_video_frames(file_url) if CV2_AVAILABLE else []
            # Also return the original URL for direct saving
            return {"type": "video", "frames": frames, "url": file_url, "original_type": file_type}
        elif file_type == "txt":
            data = _download_text(file_url)
            return {"type": "text", "data": data} if data is not None else None
        elif file_type in ["wav", "mp3", "flac", "ogg"] and AUDIO_AVAILABLE:
            data = _download_audio(file_url)
            return {"type": "audio", "data": data} if data is not None else None
        elif file_type == "safetensors" and SAFETENSORS_AVAILABLE:
            data = _download_latent(file_url)
            return {"type": "latent", "data": data} if data is not None else None
    except Exception as e:
        print(f"Warning: Failed to download or process {file_type} file from {file_url}: {e}")
    return None

def _process_outputs(outputs, save_to_local, output_prefix):
    """Process task outputs into ComfyUI format using parallel downloads."""
    if not outputs:
        outputs = []
    print(f"Processing {len(outputs)} output files in parallel...")

    # --- Parallel Download Step ---
    results = []
    with ThreadPoolExecutor(max_workers=min(10, len(outputs) or 1)) as executor:
        future_to_output = {executor.submit(_download_and_process_file, o): o for o in outputs}
        for future in as_completed(future_to_output):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"An exception occurred during file processing: {e}")

    # --- Sequential Processing and Saving Step ---
    images, video_frames = [], []
    text_content, audio_data, video_data, latent_data = None, None, None, None
    image_counter, video_counter = 0, 0
    output_dir = None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if save_to_local:
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except ImportError:
            output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Saving outputs to: {output_dir}")

    for res in sorted(results, key=lambda r: r.get('type')):
        res_type = res.get("type")
        if res_type == "image":
            images.append(res["data"])
            if save_to_local and output_dir:
                image_counter += 1
                filename = f"{output_prefix}_{timestamp}_{image_counter:03d}.{res['original_type']}"
                _save_image_to_file(res["data"], os.path.join(output_dir, filename))
                print(f"✓ Saved image: {filename}")
        elif res_type == "video":
            if res.get("frames") and not video_frames:
                video_frames.extend(res["frames"])
            if save_to_local and output_dir:
                video_counter += 1
                filename = f"{output_prefix}_{timestamp}_video_{video_counter:03d}.{res['original_type']}"
                _download_and_save_video(res["url"], os.path.join(output_dir, filename))
                print(f"✓ Saved video: {filename}")
        elif res_type == "text" and not text_content:
            text_content = res["data"]
            if save_to_local and output_dir:
                filename = f"{output_prefix}_{timestamp}_text.txt"
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(text_content)
                print(f"✓ Saved text: {filename}")
        elif res_type == "audio" and not audio_data:
            audio_data = res["data"]
            if save_to_local and output_dir and audio_data:
                filename = f"{output_prefix}_{timestamp}_audio.wav" # Default to wav for saving
                _save_audio_to_file(audio_data, os.path.join(output_dir, filename))
                print(f"✓ Saved audio: {filename}")
        elif res_type == "latent" and not latent_data:
            latent_data = res["data"]

    # --- Final Aggregation Step ---
    if not images: images.append(_create_placeholder_image("No images"))
    if not video_frames: video_frames.append(_create_placeholder_image("No video frames"))
    if not text_content: text_content = ""
    if not audio_data: audio_data = _create_placeholder_audio()
    if not latent_data: latent_data = _create_placeholder_latent()

    return (torch.cat(images, dim=0), torch.cat(video_frames, dim=0), text_content, audio_data, video_data, latent_data)


def _download_image(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def _extract_video_frames(url):
    if not CV2_AVAILABLE: return []
    try:
        import tempfile
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        cap = cv2.VideoCapture(tmp_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(torch.from_numpy(frame_rgb.astype(np.float32) / 255.0).unsqueeze(0))
        cap.release()
        os.unlink(tmp_path)
        return frames
    except Exception as e:
        print(f"Error extracting video frames: {e}")
        return []

def _download_text(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error downloading text: {e}")
        return ""

def _download_audio(url):
    if not AUDIO_AVAILABLE: return None
    try:
        import tempfile
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        waveform, sample_rate = torchaudio.load(tmp_path)

        if waveform.shape[0] == 1: waveform = waveform.repeat(2, 1)
        os.unlink(tmp_path)
        return {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def _download_latent(url):
    if not SAFETENSORS_AVAILABLE: return None
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        # safetensors.torch.load expects a file path, so we use a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".safetensors") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        latent = load(tmp_path)
        os.unlink(tmp_path)
        return latent
    except Exception as e:
        print(f"Error downloading latent: {e}")
        return None

def _create_placeholder_image(text):
    img = Image.new('RGB', (512, 128), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.text((10, 50), text, fill=(200, 200, 200), font=font)
    return torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

def _create_placeholder_audio():
    if not AUDIO_AVAILABLE: return None
    sample_rate = 44100
    waveform = torch.zeros(1, 2, sample_rate, dtype=torch.float32)
    return {"waveform": waveform, "sample_rate": sample_rate}

def _save_image_to_file(img_tensor, filepath):
    try:
        img_np = (img_tensor.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
        Image.fromarray(img_np, 'RGB').save(filepath)
    except Exception as e:
        print(f"Error saving image to {filepath}: {e}")


def _create_placeholder_latent():
    # Create an empty latent structure
    return {"samples": torch.zeros(1, 4, 64, 64)}
def _download_and_save_video(url, filepath):
    try:
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
    except Exception as e:
        print(f"Error saving video to {filepath}: {e}")

def _save_audio_to_file(audio_data, filepath):
    if not AUDIO_AVAILABLE or not audio_data: return
    try:
        waveform = audio_data.get("waveform").squeeze(0)
        sample_rate = audio_data.get("sample_rate", 44100)
        torchaudio.save(filepath, waveform, sample_rate)
    except Exception as e:
        print(f"Error saving audio to {filepath}: {e}")



class RH_ImageSelector:
    """
    Select specific image(s) from a batch of images.
    Useful for extracting individual images from RunningHub output.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "Batch of images"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "tooltip": "Index of image to select (0-based)"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "select"
    CATEGORY = "Ken-Chen/RH-API"

    def select(self, images, index):
        """
        Select image at specified index

        Args:
            images: Batch of images
            index: Index to select

        Returns:
            Selected image
        """
        if index >= images.shape[0]:
            raise ValueError(f"Index {index} out of range (batch size: {images.shape[0]})")

        selected = images[index].unsqueeze(0)
        print(f"✓ Selected image {index} from batch of {images.shape[0]}")

        return (selected,)


class RH_TextDisplay:
    """
    Display text output from RunningHub.
    Useful for viewing text results.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Text to display"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "display"
    CATEGORY = "Ken-Chen/RH-API"
    OUTPUT_NODE = True

    def display(self, text):
        """
        Display text

        Args:
            text: Text to display

        Returns:
            Same text (pass-through)
        """
        print("=" * 60)
        print("📝 Text Output:")
        print("-" * 60)
        print(text)
        print("=" * 60)

        return (text,)



def _validate_config(config):
    """Validate the config dictionary"""
    if not isinstance(config, dict):
        raise ValueError("Invalid config: must be a dictionary from RH_Config node")

    required_fields = ["api_key", "base_url"]
    for field in required_fields:
        if field not in config or not config[field]:
            raise ValueError(f"Missing required config field: {field}")

def get_task_status(config, task_id):
    """
    Gets the current status of a single task without waiting.
    """
    api_key = config["api_key"]
    base_url = config["base_url"]
    return _check_task_status(task_id, api_key, base_url)

def cancel_task(config, task_id):
    """
    Requests to cancel a task on RunningHub.
    """
    api_key = config["api_key"]
    base_url = config["base_url"]
    url = f"{base_url}/task/openapi/cancel"
    payload = {
        "taskId": task_id,
        "apiKey": api_key
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        if result.get("code") == 0:
            return True
        else:
            print(f"API Error when cancelling task: {result.get('msg', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Exception when cancelling task: {e}")
        return False
