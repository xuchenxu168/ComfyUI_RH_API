# Configuration File Usage

## Overview

The ComfyUI_RH_API plugin now supports loading API credentials from a configuration file. This allows you to:

1. Keep your API key secure and separate from your workflows
2. Avoid repeatedly entering the same API key and base URL
3. Share workflows without exposing your credentials

## Setup Instructions

### 1. Create Configuration File

1. Copy the example configuration file:
   ```bash
   cp config.json.example config.json
   ```

2. Edit `config.json` with your credentials:
   ```json
   {
       "api_key": "your_actual_api_key_here",
       "base_url": "https://www.runninghub.cn"
   }
   ```

### 2. Usage in Nodes

#### Option A: Use Configuration File Only
- Leave `api_key` field **empty** in the RH_Config node
- Leave `base_url` field **empty** in the RH_Config node
- The plugin will automatically load values from `config.json`

#### Option B: Override Configuration File
- Fill in `api_key` and/or `base_url` in the RH_Config node
- Node values will take priority over configuration file values

## Security Notes

- **Never commit `config.json` to version control**
- Add `config.json` to your `.gitignore` file
- The `config.json.example` file is safe to commit (it contains no real credentials)

## Troubleshooting

### Error: "API key is required"
- Check that `config.json` exists in the plugin directory
- Verify that `config.json` contains a valid `api_key` field
- Ensure the JSON syntax is correct

### Configuration Not Loading
- Check the ComfyUI console for loading messages:
  - `✓ Loaded configuration from config.json` (success)
  - `⚠️ Error loading config.json` (file exists but invalid)
  - `ℹ️ No config.json found` (file missing)

## Example Workflow

1. Create `config.json` with your API key
2. In ComfyUI, add an RH_Config node
3. Leave `api_key` and `base_url` empty
4. Fill in only the `workflow_or_app_id`
5. The plugin will automatically use your saved credentials

This makes sharing workflows much easier - others just need to create their own `config.json` file!
