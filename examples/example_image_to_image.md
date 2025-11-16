# Example: Image to Image with RunningHub

This example shows how to upload an image and use it in a RunningHub workflow.

## Workflow Setup

1. **Load Image Node** (ComfyUI built-in)
   - Load your input image

2. **RH_Config Node**
   - `api_key`: Your RunningHub API key
   - `workflow_or_app_id`: Your workflow ID
   - `base_url`: https://www.runninghub.cn
   - `is_ai_app`: False

3. **RH_UploadImage Node**
   - Connect `config` from RH_Config
   - Connect `image` from Load Image
   - Output: `filename` (uploaded image reference)

4. **RH_Param Node**
   - `node_id`: "3" (your image input node ID)
   - `field_name`: "image"
   - Connect `field_value` from RH_UploadImage's `filename` output

5. **RH_Execute Node**
   - Connect `config` from RH_Config
   - Connect `params` from RH_Param
   - Output: processed images

## Node Connection Flow

```
Load Image ──image──> RH_UploadImage ──filename──> RH_Param ──params──┐
                            ↑                                          │
RH_Config ──config──────────┴──────────────────────────────────> RH_Execute ──images──> Preview Image
```

## Tips

- The uploaded image filename is automatically used in the workflow
- You can upload multiple images by using multiple RH_UploadImage nodes
- Each uploaded image gets a unique filename on RunningHub
- The filename format is typically a hash string like "abc123.png"

