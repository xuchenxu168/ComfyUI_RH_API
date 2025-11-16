# 🐛 Bug Fix: Parameter Name Correction

## Issue Description

**Date:** 2025-11-15  
**Severity:** Medium  
**Status:** ✅ Fixed

### Problem

The workflow JSON files were using an incorrect parameter name for chaining RH_Param nodes:
- ❌ **Incorrect:** `next_param`
- ✅ **Correct:** `previous_params`

This caused confusion when users tried to chain parameters together, as the displayed input name didn't match the documentation.

### Root Cause

When creating the example workflow JSON files, I mistakenly used `next_param` as the input name instead of the actual parameter name defined in the code: `previous_params`.

The code in `nodes/rh_param.py` correctly defines:
```python
"optional": {
    "previous_params": ("RH_PARAMS", {
        "default": None,
        "tooltip": "Connect previous RH_Param node to chain parameters"
    }),
}
```

But the workflow JSON files incorrectly used:
```json
{
  "name": "next_param",  // ❌ Wrong!
  "type": "RH_PARAMS",
  "link": 4
}
```

### Impact

**Affected Files:**
- ✅ `examples/workflow_image_to_image.json` - Fixed
- ✅ `examples/workflow_video_generation.json` - Fixed
- ✅ `examples/workflow_advanced_batch.json` - Fixed (2 occurrences)

**Not Affected:**
- ✅ `examples/workflow_text_to_image.json` - No chaining
- ✅ `examples/workflow_ai_app.json` - No chaining

**User Impact:**
- Users saw `previous_params` in ComfyUI instead of the documented `next_param`
- This caused confusion but didn't break functionality
- The workflows still worked correctly

### Fix Applied

**Changed in all affected workflow files:**
```json
// Before (incorrect)
{
  "name": "next_param",
  "type": "RH_PARAMS",
  "link": X
}

// After (correct)
{
  "name": "previous_params",
  "type": "RH_PARAMS",
  "link": X
}
```

**Documentation Updated:**
- ✅ `examples/README.md` - Updated parameter description
- ✅ `examples/README_CN.md` - Updated parameter description

### Verification

**Test Results:**
```
============================================================
📊 Test Summary
============================================================
✅ PASS - workflow_advanced_batch.json
✅ PASS - workflow_ai_app.json
✅ PASS - workflow_image_to_image.json
✅ PASS - workflow_text_to_image.json
✅ PASS - workflow_video_generation.json

5/5 workflows passed all tests
🎉 ALL WORKFLOWS VALID!
```

**Manual Verification:**
```bash
# Confirm no more "next_param" in workflow files
findstr /s /i "next_param" examples\*.json
# Result: No matches found ✅
```

### Correct Usage

**Parameter Name:** `previous_params` (not `next_param`)

**Example - Chaining Two Parameters:**

```
RH_Param #1
  node_id: "5"
  field_name: "image"
  field_value: "hash123"
  ↓ params output
RH_Param #2
  previous_params: ← Connect here (not "next_param")
  node_id: "3"
  field_name: "text"
  field_value: "enhance the image"
  ↓ params output
RH_Execute
```

### Why "previous_params" Makes Sense

The name `previous_params` is actually more logical because:

1. **Direction:** It receives parameters from the **previous** node
2. **Accumulation:** It accumulates all **previous** parameters
3. **Flow:** Data flows forward, but we reference what came **before**

Think of it like a linked list:
```
Node 1 (params: [A]) 
  → Node 2 (previous_params: [A], adds B, outputs: [A, B])
    → Node 3 (previous_params: [A, B], adds C, outputs: [A, B, C])
```

### Lessons Learned

1. **Always verify parameter names** match between code and JSON
2. **Test workflows in actual ComfyUI** before documentation
3. **Use consistent naming** across all files
4. **Automated tests** caught the JSON structure but not the semantic error

### Migration Guide

**For Users:**

If you created workflows based on the old documentation:

1. **No action needed** - The workflows still work
2. **For clarity** - You can update your custom workflows:
   - Find any `"name": "next_param"` in your workflow JSON
   - Replace with `"name": "previous_params"`
3. **Visual change** - The input will now correctly show as `previous_params`

**For Developers:**

If you're extending this plugin:

1. Use `previous_params` for the optional input parameter
2. The parameter accumulates from previous nodes
3. Return the updated list as `params` output

### Status

✅ **Fixed and Verified**
- All workflow files corrected
- All tests passing
- Documentation updated
- No breaking changes for users

---

**Thank you for reporting this issue! The fix improves clarity and consistency.** 🎉

