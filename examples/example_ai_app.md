# Example: Calling RunningHub AI App

This example shows how to call a published AI App on RunningHub.

## What's the Difference?

- **Workflow**: Direct workflow execution (requires workflow ID)
- **AI App**: Published app with simplified interface (requires app ID)

AI Apps are easier to use as they have predefined parameters and are optimized for end users.

## Workflow Setup

1. **RH_Config Node**
   - `api_key`: Your RunningHub API key
   - `workflow_or_app_id`: Your AI App ID (numeric, e.g., "1941952386518904834")
   - `base_url`: https://www.runninghub.cn
   - `is_ai_app`: **True** (important!)

2. **RH_Param Node** (Optional)
   - Set any parameters exposed by the AI App
   - Check the AI App documentation for available parameters

3. **RH_Execute Node**
   - Connect `config` from RH_Config
   - Connect `params` from RH_Param (if any)
   - Execute and get results

## Node Connection Flow

```
RH_Config (is_ai_app=True) ──config──┐
                                     ├──> RH_Execute ──images──> Preview Image
RH_Param ──params────────────────────┘
```

## Tips

- AI App IDs are numeric (e.g., 1941952386518904834)
- Workflow IDs are alphanumeric strings
- Make sure to set `is_ai_app` to True in RH_Config
- AI Apps may have different parameter structures than workflows
- Check the AI App page on RunningHub for parameter documentation

