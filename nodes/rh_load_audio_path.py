import os
import folder_paths

class RH_LoadAudioPath:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # This input is hidden and controlled by the JS widget.
                # It receives the filename from the ComfyUI upload endpoint.
                "audio_filename": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("audio_path",)
    FUNCTION = "get_path"
    CATEGORY = "Ken-Chen/RH-API"

    def get_path(self, audio_filename):
        """
        Resolves the audio file path from ComfyUI's input directory.
        Uses multiple fallback strategies to locate the file.
        """
        # 1. Validate input
        if not audio_filename or not audio_filename.strip():
            raise ValueError("No audio filename provided. Please select and upload an audio file using the node's widget.")

        audio_filename = audio_filename.strip()

        # 2. Try to get the full path using multiple strategies
        try:
            # Strategy 1: Use get_annotated_filepath (primary method)
            audio_path = folder_paths.get_annotated_filepath(audio_filename)
            if audio_path and os.path.exists(audio_path):
                print(f"RH_LoadAudioPath: Found audio file at: {audio_path}")
                return (audio_path,)

            # Strategy 2: Check directly in input directory
            potential_path = os.path.join(folder_paths.get_input_directory(), audio_filename)
            if os.path.exists(potential_path):
                audio_path = potential_path
                print(f"RH_LoadAudioPath: Found audio file at: {audio_path}")
                return (audio_path,)

            # Strategy 3: Check in input/uploads subdirectory
            potential_path = os.path.join(folder_paths.get_input_directory(), 'uploads', audio_filename)
            if os.path.exists(potential_path):
                audio_path = potential_path
                print(f"RH_LoadAudioPath: Found audio file at: {audio_path}")
                return (audio_path,)

            # If none of the strategies worked, raise an error
            raise FileNotFoundError(f"Audio file not found in input directory: {audio_filename}")

        except Exception as e:
            raise FileNotFoundError(f"Error finding audio file '{audio_filename}': {e}")

