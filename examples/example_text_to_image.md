# Example: Text to Image with RunningHub

This example shows how to call a RunningHub workflow to generate images from text prompts.

## Workflow Setup

1. **RH_Config Node**
   - `api_key`: Your RunningHub API key
   - `workflow_or_app_id`: Your workflow ID from RunningHub
   - `base_url`: https://www.runninghub.cn
   - `is_ai_app`: False (for workflow)

2. **RH_Param Node** (Optional - for customizing parameters)
   - `node_id`: "3" (example node ID in your workflow)
   - `field_name`: "text" (the prompt field)
   - `field_value`: "a beautiful landscape"

3. **RH_Execute Node**
   - Connect `config` from RH_Config
   - Connect `params` from RH_Param (optional)
   - `timeout`: 600 seconds
   - `use_high_performance`: False

4. **Output**
   - Connect `images` output to Preview Image or Save Image node

## Node Connection Flow

```
RH_Config ──config──┐
                    ├──> RH_Execute ──images──> Preview Image
RH_Param ──params───┘
```

## Tips

- You can chain multiple RH_Param nodes to set multiple parameters
- The `images` output contains all generated images as a batch
- Use RH_ImageSelector to extract specific images from the batch
- Check the console for detailed progress information

