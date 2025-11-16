dis# Example: Save Generated Images and Videos to Local

This example shows how to automatically save RunningHub outputs to your local ComfyUI output directory.

## Why Save to Local?

By default, RunningHub outputs are:
1. Downloaded and converted to tensors for use in ComfyUI
2. Automatically saved to your local disk for later use

This is useful for:
- Keeping a permanent copy of generated content
- Sharing files with others
- Using outputs in other applications
- Building a library of generated content

## Basic Setup with Auto-Save

### 1. Configure RH_Execute Node

The `RH_Execute` node has two parameters for controlling file saving:

- **save_to_local** (default: True)
  - Enable/disable automatic saving
  - When enabled, all outputs are saved to ComfyUI's output directory
  
- **output_prefix** (default: "RH")
  - Prefix for saved filenames
  - Helps organize your files

### 2. Example Workflow

```
┌─────────────┐
│  RH_Config  │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────┐
│      RH_Execute             │
│                             │
│  save_to_local: True        │ ← Enable auto-save
│  output_prefix: "MyProject" │ ← Custom prefix
└──────┬──────────────────────┘
       │
       ↓
┌─────────────┐
│Preview Image│
└─────────────┘
```

## File Naming Convention

Files are saved with the following naming pattern:

### Images
```
{prefix}_{timestamp}_{number}.{extension}

Examples:
- RH_20251115_143022_001.png
- RH_20251115_143022_002.jpg
- MyProject_20251115_143022_001.png
```

### Videos
```
{prefix}_{timestamp}_video_{number}.{extension}

Examples:
- RH_20251115_143022_video_001.mp4
- MyProject_20251115_143022_video_001.webm
```

### Text
```
{prefix}_{timestamp}_text.txt

Examples:
- RH_20251115_143022_text.txt
- MyProject_20251115_143022_text.txt
```

### Audio
```
{prefix}_{timestamp}_audio.{extension}

Examples:
- RH_20251115_143022_audio.wav
- MyProject_20251115_143022_audio.mp3
```

## Output Directory

Files are saved to ComfyUI's output directory:

**Default Location:**
```
ComfyUI/output/
```

You can find your saved files in this directory after execution.

## Advanced Usage

### Custom Prefix for Different Projects

Use different prefixes to organize outputs by project:

```python
# For character generation project
output_prefix: "Character"
# Results: Character_20251115_143022_001.png

# For landscape generation project
output_prefix: "Landscape"
# Results: Landscape_20251115_143022_001.png

# For video generation project
output_prefix: "Video_Gen"
# Results: Video_Gen_20251115_143022_video_001.mp4
```

### Disable Auto-Save

If you only want to use outputs in ComfyUI without saving:

```
RH_Execute:
  save_to_local: False
```

This is useful when:
- You're just testing
- You only need the output for further processing in ComfyUI
- You want to save disk space

### Batch Processing

When generating multiple images in one task:

```
Input: Generate 4 images

Output files:
- MyProject_20251115_143022_001.png
- MyProject_20251115_143022_002.png
- MyProject_20251115_143022_003.png
- MyProject_20251115_143022_004.png
```

All images from the same task share the same timestamp.

## Tips

1. **Organize by Date**: The timestamp includes date and time, making it easy to find recent outputs

2. **Use Descriptive Prefixes**: Choose prefixes that describe your project or content type

3. **Check Console Output**: The console will show the exact filename when each file is saved:
   ```
   ✓ Saved image: MyProject_20251115_143022_001.png
   ✓ Saved video: MyProject_20251115_143022_video_001.mp4
   ```

4. **Disk Space**: Remember that videos can be large. Monitor your disk space if generating many videos

5. **File Management**: Periodically clean up old outputs to free disk space

## Troubleshooting

### "Warning: folder_paths not available"
- The plugin will create an `output` folder in the current directory
- This is normal if running outside ComfyUI

### Files Not Saving
- Check that `save_to_local` is set to `True`
- Verify you have write permissions to the output directory
- Check console for error messages

### Can't Find Saved Files
- Check ComfyUI's output directory: `ComfyUI/output/`
- Look for files with your specified prefix
- Check the console output for the exact filename

## Example: Complete Workflow with Custom Prefix

```
1. RH_Config
   - api_key: your_api_key
   - workflow_or_app_id: your_workflow_id

2. RH_Param (optional)
   - node_id: "3"
   - field_name: "text"
   - field_value: "a beautiful sunset"

3. RH_Execute
   - config: from RH_Config
   - params: from RH_Param
   - save_to_local: True
   - output_prefix: "Sunset"
   
4. Preview Image
   - images: from RH_Execute

Result:
- Image displayed in ComfyUI
- File saved: ComfyUI/output/Sunset_20251115_143022_001.png
```

---

With automatic file saving, you never lose your generated content! 🎨💾

