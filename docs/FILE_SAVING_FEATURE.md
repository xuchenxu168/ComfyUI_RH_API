# 🎉 New Feature: Automatic File Saving

## Overview

The RH_Execute node now automatically saves all generated images, videos, text, and audio files to your local disk!

## What's New

### Version 1.0.1 - File Saving Feature

**Two new parameters in RH_Execute:**

1. **save_to_local** (Boolean, default: True)
   - Automatically save all outputs to ComfyUI's output directory
   - Can be disabled if you only need outputs in ComfyUI

2. **output_prefix** (String, default: "RH")
   - Customize the prefix for saved filenames
   - Helps organize files by project or content type

## How It Works

### Automatic Saving

When `save_to_local` is enabled (default), the plugin will:

1. **Download** outputs from RunningHub
2. **Convert** them to ComfyUI tensors for use in your workflow
3. **Save** them to disk with organized filenames
4. **Report** the exact filename in the console

### File Naming

Files are saved with a clear, organized naming pattern:

```
{prefix}_{timestamp}_{number}.{extension}
```

**Examples:**
- `RH_20251115_143022_001.png` - First image
- `RH_20251115_143022_002.png` - Second image
- `RH_20251115_143022_video_001.mp4` - First video
- `RH_20251115_143022_text.txt` - Text output
- `RH_20251115_143022_audio.wav` - Audio output

### Output Location

Files are saved to ComfyUI's output directory:

```
ComfyUI/output/
```

If running outside ComfyUI, files are saved to:

```
./output/
```

## Usage Examples

### Basic Usage (Auto-save enabled)

```
RH_Execute:
  config: from RH_Config
  params: from RH_Param
  save_to_local: True  ← Default, auto-save enabled
  output_prefix: "RH"  ← Default prefix
```

**Result:**
- Images displayed in ComfyUI
- Files saved: `ComfyUI/output/RH_20251115_143022_001.png`

### Custom Prefix

```
RH_Execute:
  config: from RH_Config
  params: from RH_Param
  save_to_local: True
  output_prefix: "MyProject"  ← Custom prefix
```

**Result:**
- Files saved: `ComfyUI/output/MyProject_20251115_143022_001.png`

### Disable Auto-save

```
RH_Execute:
  config: from RH_Config
  params: from RH_Param
  save_to_local: False  ← Disable auto-save
```

**Result:**
- Images only available in ComfyUI
- No files saved to disk

## Benefits

### 1. Never Lose Your Work
All generated content is automatically saved, so you never lose your creations.

### 2. Easy Organization
Files are organized by timestamp and prefix, making it easy to find what you need.

### 3. Batch Processing
When generating multiple images, all are saved with sequential numbering.

### 4. Project Management
Use different prefixes for different projects to keep files organized.

### 5. Sharing Made Easy
Files are saved in standard formats (PNG, MP4, TXT, WAV) that can be easily shared.

## Console Output

The plugin provides clear feedback when saving files:

```
Processing 3 output files...
✓ Output directory: D:\ComfyUI\output
✓ Saved image: MyProject_20251115_143022_001.png
✓ Saved image: MyProject_20251115_143022_002.png
✓ Saved video: MyProject_20251115_143022_video_001.mp4
✓ Outputs processed
```

## Technical Details

### Supported File Types

- **Images**: PNG, JPG, JPEG, WebP, BMP
- **Videos**: MP4, AVI, MOV, WebM
- **Text**: TXT
- **Audio**: WAV, MP3, FLAC, OGG

### File Formats

- Images are saved in their original format
- Videos are saved in their original format
- Text is saved as UTF-8 encoded TXT
- Audio is saved in its original format

### Timestamp Format

```
YYYYMMDD_HHMMSS

Example: 20251115_143022
- Year: 2025
- Month: 11
- Day: 15
- Hour: 14
- Minute: 30
- Second: 22
```

### Sequential Numbering

Files from the same task share the same timestamp but have different numbers:

```
RH_20251115_143022_001.png  ← First image
RH_20251115_143022_002.png  ← Second image
RH_20251115_143022_003.png  ← Third image
```

## Testing

The feature has been thoroughly tested:

```bash
python test_file_saving.py
```

**Test Results:**
```
✓ PASS: Filename Generation
✓ PASS: Output Directory
✓ PASS: Parameter Defaults
✓ PASS: Image Saving

✅ ALL TESTS PASSED (4/4)
```

## Documentation

For more details, see:
- [README.md](README.md) - Main documentation
- [README_CN.md](README_CN.md) - Chinese documentation
- [examples/example_save_to_local.md](examples/example_save_to_local.md) - Detailed examples
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

**Enjoy automatic file saving! 🎨💾**

