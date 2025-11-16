# Quick Start Guide

Get started with ComfyUI_RH_API in 5 minutes!

## Prerequisites

1. ComfyUI installed and running
2. RunningHub account with API key
3. A workflow or AI app on RunningHub

## Step 1: Install the Plugin

### Option A: ComfyUI Manager
1. Open ComfyUI Manager
2. Search "ComfyUI_RH_API"
3. Click Install
4. Restart ComfyUI

### Option B: Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/YOUR_USERNAME/ComfyUI_RH_API.git
cd ComfyUI_RH_API
pip install -r requirements.txt
```
Restart ComfyUI.

## Step 2: Get Your API Key

1. Go to https://www.runninghub.cn
2. Login to your account
3. Navigate to Settings → API Keys
4. Copy your API key (keep it secret!)

## Step 3: Find Your Workflow ID

### For Workflows:
1. Open your workflow on RunningHub
2. Look at the URL or workflow settings
3. Copy the workflow ID (alphanumeric string)

### For AI Apps:
1. Open your AI app on RunningHub
2. Look at the URL
3. Copy the app ID (numeric, e.g., 1941952386518904834)

## Step 4: Create Your First Workflow

### Simple Text-to-Image Example

1. **Add RH_Config Node**
   - Right-click → Add Node → RunningHub → 🌐 RH Config
   - Fill in:
     - `api_key`: Your API key from Step 2
     - `workflow_or_app_id`: Your workflow ID from Step 3
     - `base_url`: https://www.runninghub.cn (default)
     - `is_ai_app`: False (for workflow) or True (for AI app)

2. **Add RH_Execute Node**
   - Right-click → Add Node → RunningHub → ▶️ RH Execute
   - Connect `config` output from RH_Config to `config` input

3. **Add Preview Image Node**
   - Right-click → Add Node → image → Preview Image
   - Connect `images` output from RH_Execute to `images` input

4. **Run!**
   - Click "Queue Prompt"
   - Watch the console for progress
   - See your generated images!

### Visual Workflow:
```
┌─────────────┐
│  RH_Config  │
│             │
│ api_key: ***│
│ workflow_id │
└──────┬──────┘
       │ config
       ↓
┌─────────────┐
│ RH_Execute  │
└──────┬──────┘
       │ images
       ↓
┌─────────────┐
│Preview Image│
└─────────────┘
```

## Step 5: Customize Parameters (Optional)

Want to change the prompt or other parameters?

1. **Add RH_Param Node**
   - Right-click → Add Node → RunningHub → ⚙️ RH Param
   - Fill in:
     - `node_id`: "3" (example - check your workflow)
     - `field_name`: "text" (the parameter name)
     - `field_value`: "a beautiful sunset over mountains"

2. **Connect to RH_Execute**
   - Connect `params` output from RH_Param to `params` input of RH_Execute

### Updated Workflow:
```
┌─────────────┐
│  RH_Config  │
└──────┬──────┘
       │ config
       ↓
┌─────────────┐     ┌─────────────┐
│  RH_Param   │────→│ RH_Execute  │
│             │params└──────┬──────┘
│ node_id: 3  │            │ images
│ field: text │            ↓
│ value: ...  │     ┌─────────────┐
└─────────────┘     │Preview Image│
                    └─────────────┘
```

## Step 6: Upload Images (Optional)

Need to upload an image to your workflow?

1. **Add Load Image Node** (ComfyUI built-in)
   - Load your input image

2. **Add RH_UploadImage Node**
   - Right-click → Add Node → RunningHub → 📤 RH Upload Image
   - Connect `config` from RH_Config
   - Connect `image` from Load Image

3. **Add RH_Param Node**
   - Set `node_id` to your image input node
   - Set `field_name` to "image"
   - Connect `filename` from RH_UploadImage to `field_value`

4. **Connect to RH_Execute**
   - Connect `params` to RH_Execute

## Common Issues

### "API key is required"
→ Make sure you entered your API key in RH_Config

### "Task timeout"
→ Increase `timeout` in RH_Execute (default: 600 seconds)

### "No output"
→ Check if your workflow has output nodes enabled

### WebSocket warnings
→ Normal! The plugin will use HTTP polling instead

## Next Steps

- Check out the [examples](examples/) directory for more workflows
- Read the full [README](README.md) for detailed documentation
- Explore advanced features like parameter chaining
- Try using AI Apps with `is_ai_app=True`

## Need Help?

- GitHub Issues: Report bugs or ask questions
- RunningHub Docs: https://www.runninghub.cn/docs
- Check the console output for detailed error messages

---

Happy creating! 🎨✨

