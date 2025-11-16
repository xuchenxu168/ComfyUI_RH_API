# ComfyUI_RH_API Example Workflows

This directory contains professional example workflows that demonstrate how to use the RunningHub API nodes in ComfyUI.

## 📁 Available Workflows

### 1. **workflow_text_to_image.json** - Basic Text-to-Image
**Difficulty:** ⭐ Beginner

A simple workflow that generates images from text prompts.

**Nodes Used:**
- RH_Config
- RH_Param
- RH_Execute
- PreviewImage
- RH_TextDisplay

**What it does:**
1. Configures RunningHub API connection
2. Sets a text prompt parameter
3. Executes the workflow on RunningHub
4. Displays the generated images
5. Automatically saves images to `ComfyUI/output/`

**How to use:**
1. Open the workflow in ComfyUI
2. Replace `your_api_key_here` with your actual API key
3. Replace `your_workflow_id_here` with your workflow ID
4. Modify the prompt in the RH_Param node
5. Click "Queue Prompt"

---

### 2. **workflow_image_to_image.json** - Image-to-Image Transformation
**Difficulty:** ⭐⭐ Intermediate

Upload an image and transform it using RunningHub workflows.

**Nodes Used:**
- RH_Config
- LoadImage
- RH_UploadImage
- RH_Param (x2, chained)
- RH_Execute
- PreviewImage

**What it does:**
1. Loads a local image
2. Uploads it to RunningHub
3. Chains multiple parameters (image hash + text prompt)
4. Executes image-to-image transformation
5. Displays and saves the result

**How to use:**
1. Place an image in ComfyUI's input folder
2. Update the LoadImage node to select your image
3. Configure API key and workflow ID
4. Adjust the transformation prompt
5. Run the workflow

---

### 3. **workflow_ai_app.json** - AI Application Execution
**Difficulty:** ⭐ Beginner

Execute a published AI application on RunningHub.

**Nodes Used:**
- RH_Config (with `is_ai_app: true`)
- RH_Param
- RH_Execute
- PreviewImage
- RH_TextDisplay

**What it does:**
1. Connects to a RunningHub AI App
2. Sends input parameters
3. Receives both image and text outputs
4. Displays results in ComfyUI

**How to use:**
1. Get your AI App ID from RunningHub
2. Set `is_ai_app` to `true` in RH_Config
3. Configure input parameters
4. Execute and view results

---

### 4. **workflow_advanced_batch.json** - Advanced Batch Processing
**Difficulty:** ⭐⭐⭐ Advanced

Generate multiple images with chained parameters and select specific outputs.

**Nodes Used:**
- RH_Config
- RH_Param (x3, chained)
- RH_Execute (with high performance)
- PreviewImage
- RH_ImageSelector
- SaveImage
- RH_TextDisplay

**What it does:**
1. Chains multiple parameters (prompt, seed, steps)
2. Uses high-performance instance (RTX 4090)
3. Generates batch of images
4. Allows selection of specific image from batch
5. Saves selected image separately
6. Displays any text output

**How to use:**
1. Configure all three parameters
2. Enable high-performance mode if needed
3. Run the workflow
4. Use RH_ImageSelector to pick your favorite
5. Selected image is saved with custom prefix

---

### 5. **workflow_video_generation.json** - Video Generation
**Difficulty:** ⭐⭐⭐ Advanced

Generate videos from images using RunningHub's video workflows.

**Nodes Used:**
- RH_Config
- LoadImage
- RH_UploadImage
- RH_Param (x2, chained)
- RH_Execute (extended timeout)
- PreviewImage

**What it does:**
1. Loads a starting frame image
2. Uploads it to RunningHub
3. Adds motion parameters
4. Generates video
5. Extracts and displays video frames
6. Saves video file to local disk

**How to use:**
1. Prepare a starting frame image
2. Configure motion prompts
3. Set longer timeout (900s) for video generation
4. Run and wait for video processing
5. Video saved to `ComfyUI/output/`

---

## 🎯 Quick Start Guide

### Step 1: Get Your API Credentials

1. Visit [RunningHub](https://www.runninghub.cn)
2. Sign up or log in
3. Go to API settings
4. Copy your API key

### Step 2: Find Your Workflow/App ID

**For Workflows:**
1. Open your workflow in RunningHub
2. Look at the URL: `https://www.runninghub.cn/workflow/{workflow_id}`
3. Copy the workflow ID

**For AI Apps:**
1. Publish your workflow as an AI App
2. Find the App ID in the app settings
3. Copy the App ID

### Step 3: Import Workflow

1. Open ComfyUI
2. Click "Load" button
3. Navigate to `custom_nodes/ComfyUI_RH_API/examples/`
4. Select a workflow JSON file
5. Click "Open"

### Step 4: Configure

1. Find the **RH_Config** node
2. Replace `your_api_key_here` with your API key
3. Replace `your_workflow_id_here` with your workflow/app ID
4. Adjust other parameters as needed

### Step 5: Execute

1. Click "Queue Prompt" button
2. Watch the progress in the console
3. View results in PreviewImage nodes
4. Find saved files in `ComfyUI/output/` folder

---

## 📝 Node Parameter Reference

### RH_Config
- **api_key**: Your RunningHub API key
- **workflow_or_app_id**: Workflow ID or AI App ID
- **base_url**: API endpoint (default: https://www.runninghub.cn)
- **is_ai_app**: Set to `true` for AI Apps, `false` for workflows

### RH_Param
- **node_id**: The node ID in your RunningHub workflow
- **field_name**: The parameter name (e.g., "text", "image", "seed")
- **field_value**: The value to set (can be connected from other nodes)
- **previous_params**: (Optional) Chain multiple parameters together by connecting from previous RH_Param node

### RH_Execute
- **timeout**: Maximum wait time in seconds (default: 600)
- **use_high_performance**: Use RTX 4090 instance (costs more credits)
- **save_to_local**: Auto-save outputs to disk (default: true)
- **output_prefix**: Filename prefix for saved files (default: "RH")

---

## 💡 Tips & Best Practices

### 1. **Parameter Chaining**
Chain multiple RH_Param nodes to send multiple parameters:
```
RH_Param (prompt) → RH_Param (seed) → RH_Param (steps) → RH_Execute
```

### 2. **File Naming**
Use descriptive prefixes for different projects:
- `output_prefix: "Portrait"` → `Portrait_20251115_143022_001.png`
- `output_prefix: "Landscape"` → `Landscape_20251115_143022_001.png`

### 3. **Timeout Settings**
- Images: 300-600 seconds
- Videos: 900-1800 seconds
- Complex workflows: 1200+ seconds

### 4. **High Performance Mode**
Enable for:
- Large batch generations
- High-resolution outputs
- Complex workflows
- Faster processing

### 5. **Error Handling**
If execution fails:
1. Check API key is correct
2. Verify workflow/app ID
3. Ensure parameters match your workflow
4. Check console for error messages
5. Try increasing timeout

---

## 🔧 Troubleshooting

### "Invalid API key"
- Double-check your API key
- Ensure no extra spaces
- Regenerate key if needed

### "Workflow not found"
- Verify workflow ID is correct
- Check if workflow is published
- For AI Apps, use App ID not Workflow ID

### "Timeout error"
- Increase timeout value
- Check RunningHub server status
- Try again during off-peak hours

### "No outputs"
- Verify your workflow produces outputs
- Check node IDs match your workflow
- Review RunningHub execution logs

---

## 📚 Additional Resources

- [Main README](../README.md) - Full documentation
- [Quick Start Guide](../QUICKSTART.md) - 5-minute setup
- [File Saving Feature](../FILE_SAVING_FEATURE.md) - Auto-save documentation
- [RunningHub Documentation](https://www.runninghub.cn/docs) - Official API docs

---

## 🎨 Example Use Cases

1. **Batch Portrait Generation**: Use workflow_advanced_batch.json with portrait prompts
2. **Style Transfer**: Use workflow_image_to_image.json with style prompts
3. **Logo Creation**: Use workflow_ai_app.json with logo generation app
4. **Animation**: Use workflow_video_generation.json for image-to-video
5. **Product Mockups**: Chain multiple transformations with parameters

---

**Happy Creating! 🚀**

