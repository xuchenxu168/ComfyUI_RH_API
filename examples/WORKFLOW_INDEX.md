# 🎨 Workflow Quick Reference

A quick reference guide to help you choose the right workflow for your needs.

## 📊 Workflow Comparison Table

| Workflow | Difficulty | Use Case | Key Features | Estimated Time |
|----------|-----------|----------|--------------|----------------|
| [workflow_text_to_image.json](#1-workflow_text_to_imagejson) | ⭐ Beginner | Generate images from text | Simple setup, auto-save | 30-60s |
| [workflow_image_to_image.json](#2-workflow_image_to_imagejson) | ⭐⭐ Intermediate | Transform existing images | Upload + transform | 45-90s |
| [workflow_ai_app.json](#3-workflow_ai_appjson) | ⭐ Beginner | Use published AI apps | Multi-output support | 30-60s |
| [workflow_advanced_batch.json](#4-workflow_advanced_batchjson) | ⭐⭐⭐ Advanced | Batch generation + selection | Multiple params, high-perf | 60-120s |
| [workflow_video_generation.json](#5-workflow_video_generationjson) | ⭐⭐⭐ Advanced | Create videos from images | Video output, long timeout | 120-300s |

---

## 🎯 Choose by Your Goal

### I want to...

#### 🖼️ Generate Images
- **From text only** → Use `workflow_text_to_image.json`
- **From existing image** → Use `workflow_image_to_image.json`
- **Multiple variations** → Use `workflow_advanced_batch.json`

#### 🎬 Generate Videos
- **From a starting frame** → Use `workflow_video_generation.json`

#### 🤖 Use AI Apps
- **Run a published app** → Use `workflow_ai_app.json`

#### 🔧 Learn Advanced Features
- **Parameter chaining** → Use `workflow_advanced_batch.json`
- **Image selection** → Use `workflow_advanced_batch.json`
- **High-performance mode** → Use `workflow_advanced_batch.json`

---

## 📋 Workflow Details

### 1. workflow_text_to_image.json
**Perfect for:** First-time users, simple image generation

**Nodes:** 5 nodes
- RH_Config
- RH_Param
- RH_Execute
- PreviewImage
- RH_TextDisplay

**What you need:**
- API key
- Workflow ID
- Text prompt

**Output:**
- Images (PNG/JPG)
- Saved to `ComfyUI/output/`

---

### 2. workflow_image_to_image.json
**Perfect for:** Style transfer, image enhancement, variations

**Nodes:** 7 nodes
- RH_Config
- LoadImage
- RH_UploadImage
- RH_Param (x2, chained)
- RH_Execute
- PreviewImage

**What you need:**
- API key
- Workflow ID
- Source image
- Transformation prompt

**Output:**
- Transformed images
- Saved to `ComfyUI/output/`

---

### 3. workflow_ai_app.json
**Perfect for:** Using pre-built AI applications

**Nodes:** 5 nodes
- RH_Config (with `is_ai_app: true`)
- RH_Param
- RH_Execute
- PreviewImage
- RH_TextDisplay

**What you need:**
- API key
- AI App ID (not workflow ID!)
- Input parameters

**Output:**
- Images
- Text output
- Saved to `ComfyUI/output/`

---

### 4. workflow_advanced_batch.json
**Perfect for:** Power users, batch processing, experimentation

**Nodes:** 9 nodes
- RH_Config
- RH_Param (x3, chained)
- RH_Execute (high-performance)
- PreviewImage
- RH_ImageSelector
- SaveImage
- RH_TextDisplay

**What you need:**
- API key
- Workflow ID
- Multiple parameters (prompt, seed, steps)

**Output:**
- Batch of images
- Selected image saved separately
- Text output

**Special features:**
- Parameter chaining
- High-performance mode
- Image selection from batch

---

### 5. workflow_video_generation.json
**Perfect for:** Animation, video creation, motion graphics

**Nodes:** 7 nodes
- RH_Config
- LoadImage
- RH_UploadImage
- RH_Param (x2, chained)
- RH_Execute (extended timeout)
- PreviewImage

**What you need:**
- API key
- Video workflow ID
- Starting frame image
- Motion parameters

**Output:**
- Video file (MP4/WebM)
- Video frames as images
- Saved to `ComfyUI/output/`

**Note:** Requires longer timeout (900s+)

---

## 🚀 Getting Started Checklist

Before using any workflow:

- [ ] Install ComfyUI_RH_API plugin
- [ ] Get RunningHub API key
- [ ] Find your workflow/app ID
- [ ] Restart ComfyUI
- [ ] Load example workflow
- [ ] Update API credentials
- [ ] Test with simple prompt

---

## 💡 Tips for Success

### For Beginners
1. Start with `workflow_text_to_image.json`
2. Use simple, clear prompts
3. Keep default timeout (600s)
4. Check console for progress

### For Intermediate Users
1. Try `workflow_image_to_image.json`
2. Experiment with parameter chaining
3. Use descriptive output prefixes
4. Monitor file sizes

### For Advanced Users
1. Use `workflow_advanced_batch.json`
2. Enable high-performance mode
3. Chain multiple parameters
4. Optimize timeout values

---

## 🔗 Related Documentation

- [Main README](../README.md) - Full plugin documentation
- [Examples README](README.md) - Detailed workflow guides
- [Quick Start](../QUICKSTART.md) - 5-minute setup
- [File Saving](../FILE_SAVING_FEATURE.md) - Auto-save feature

---

**Need help? Check the [Troubleshooting section](README.md#-troubleshooting) in the Examples README!**

