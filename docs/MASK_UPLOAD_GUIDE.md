# 🎭 Mask Upload Guide / 遮罩上传指南

## English

### Overview

The `RH_UploadMask` node allows you to upload mask images to RunningHub for inpainting, masking, and other image editing operations that require masks.

### What is a Mask?

A **mask** is a grayscale image that defines which areas of an image should be affected by an operation:
- **White areas (255)**: Fully affected
- **Black areas (0)**: Not affected
- **Gray areas (1-254)**: Partially affected

### Node: RH_UploadMask

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `config` | RH_CONFIG | ✅ Yes | RunningHub configuration from RH_Config node |
| `mask` | MASK | ✅ Yes | Mask tensor to upload (will be converted to grayscale) |
| `original_image` | IMAGE | ❌ Optional | Original image for reference (not uploaded, just for visualization) |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `file_hash` | STRING | Unique identifier for the uploaded mask file |

### How to Use

#### Method 1: Load Image with Mask

ComfyUI's `LoadImage` node outputs both IMAGE and MASK:

```
LoadImage
  ├─ IMAGE output → RH_UploadImage
  └─ MASK output → RH_UploadMask
```

#### Method 2: Create Mask from Image

Use mask creation nodes:

```
LoadImage → ImageToMask → RH_UploadMask
```

#### Method 3: Draw Mask Manually

Use mask drawing nodes:

```
MaskEditor → RH_UploadMask
```

### Complete Inpainting Workflow

1. **Load Image**: Use `LoadImage` to load your image
2. **Upload Image**: Connect IMAGE output to `RH_UploadImage`
3. **Upload Mask**: Connect MASK output to `RH_UploadMask`
4. **Set Parameters**: 
   - Use `RH_Param` to set image hash (from step 2)
   - Use `RH_Param` to set mask hash (from step 3)
   - Use `RH_Param` to set prompt or other parameters
5. **Execute**: Use `RH_Execute` to run the workflow
6. **Preview**: View the inpainted result

### Example Workflow

See `examples/workflow_inpainting_with_mask.json` for a complete example.

### Technical Details

#### Mask Format

- **Input**: ComfyUI MASK tensor (B, H, W) or (H, W)
- **Processing**: Automatically converts to grayscale PNG
- **Output**: Single-channel grayscale image (mode 'L')
- **Value Range**: 0-255 (automatically scaled if input is 0-1)

#### Upload Endpoint

The node uploads to:
```
POST {base_url}/task/openapi/upload
```

With parameters:
- `apiKey`: Your RunningHub API key
- `fileType`: "image" (masks are uploaded as images)
- `file`: PNG image data

**Note:** Masks are uploaded using `fileType: 'image'` because they are grayscale images. The distinction is made by how you use them in the workflow, not by the upload type.

#### Size Limits

- **Maximum file size**: 10 MB
- **Recommended resolution**: Match your original image
- **Format**: PNG (automatically converted)

### Common Use Cases

#### 1. Inpainting

Remove objects or fill in missing areas:
```
Original Image + Mask (white = remove) → Inpainting → Result
```

#### 2. Selective Editing

Apply effects only to masked areas:
```
Original Image + Mask (white = edit) → Style Transfer → Result
```

#### 3. Background Removal

Mask the subject to remove background:
```
Original Image + Mask (white = keep) → Background Removal → Result
```

### Troubleshooting

#### Issue: "Mask must be 2D"

**Solution**: Ensure your mask is a proper MASK type, not IMAGE. Use `ImageToMask` if needed.

#### Issue: "Upload failed"

**Solution**: 
1. Check your API key in RH_Config
2. Verify network connection
3. Check mask file size (< 10MB)

#### Issue: "No file identifier found"

**Solution**: The upload succeeded but the response format is unexpected. Check RunningHub API documentation for the correct response format.

---

## 中文

### 概述

`RH_UploadMask` 节点允许您将遮罩图像上传到 RunningHub，用于修复、遮罩和其他需要遮罩的图像编辑操作。

### 什么是遮罩？

**遮罩**是一个灰度图像，定义了图像的哪些区域应该受到操作的影响：
- **白色区域 (255)**：完全受影响
- **黑色区域 (0)**：不受影响
- **灰色区域 (1-254)**：部分受影响

### 节点：RH_UploadMask

#### 输入

| 输入 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `config` | RH_CONFIG | ✅ 是 | 来自 RH_Config 节点的 RunningHub 配置 |
| `mask` | MASK | ✅ 是 | 要上传的遮罩张量（将转换为灰度图） |
| `original_image` | IMAGE | ❌ 否 | 原始图像参考（不上传，仅用于可视化） |

#### 输出

| 输出 | 类型 | 描述 |
|------|------|------|
| `file_hash` | STRING | 上传的遮罩文件的唯一标识符 |

### 使用方法

#### 方法 1：加载带遮罩的图像

ComfyUI 的 `LoadImage` 节点同时输出 IMAGE 和 MASK：

```
LoadImage
  ├─ IMAGE 输出 → RH_UploadImage
  └─ MASK 输出 → RH_UploadMask
```

#### 方法 2：从图像创建遮罩

使用遮罩创建节点：

```
LoadImage → ImageToMask → RH_UploadMask
```

#### 方法 3：手动绘制遮罩

使用遮罩绘制节点：

```
MaskEditor → RH_UploadMask
```

### 完整的修复工作流

1. **加载图像**：使用 `LoadImage` 加载您的图像
2. **上传图像**：将 IMAGE 输出连接到 `RH_UploadImage`
3. **上传遮罩**：将 MASK 输出连接到 `RH_UploadMask`
4. **设置参数**：
   - 使用 `RH_Param` 设置图像哈希（来自步骤 2）
   - 使用 `RH_Param` 设置遮罩哈希（来自步骤 3）
   - 使用 `RH_Param` 设置提示词或其他参数
5. **执行**：使用 `RH_Execute` 运行工作流
6. **预览**：查看修复结果

### 示例工作流

查看 `examples/workflow_inpainting_with_mask.json` 获取完整示例。

### 技术细节

#### 遮罩格式

- **输入**：ComfyUI MASK 张量 (B, H, W) 或 (H, W)
- **处理**：自动转换为灰度 PNG
- **输出**：单通道灰度图像（模式 'L'）
- **值范围**：0-255（如果输入是 0-1 则自动缩放）

#### 上传端点

节点上传到：
```
POST {base_url}/task/openapi/upload
```

参数：
- `apiKey`：您的 RunningHub API 密钥
- `fileType`："image"（遮罩作为图像上传）
- `file`：PNG 图像数据

**注意：** 遮罩使用 `fileType: 'image'` 上传，因为它们本质上是灰度图像。区别在于您如何在工作流中使用它们，而不是上传类型。

#### 大小限制

- **最大文件大小**：10 MB
- **推荐分辨率**：与原始图像匹配
- **格式**：PNG（自动转换）

### 常见用例

#### 1. 图像修复

移除对象或填充缺失区域：
```
原始图像 + 遮罩（白色 = 移除）→ 修复 → 结果
```

#### 2. 选择性编辑

仅对遮罩区域应用效果：
```
原始图像 + 遮罩（白色 = 编辑）→ 风格转换 → 结果
```

#### 3. 背景移除

遮罩主体以移除背景：
```
原始图像 + 遮罩（白色 = 保留）→ 背景移除 → 结果
```

### 故障排除

#### 问题："Mask must be 2D"

**解决方案**：确保您的遮罩是正确的 MASK 类型，而不是 IMAGE。如需要，使用 `ImageToMask`。

#### 问题："Upload failed"

**解决方案**：
1. 检查 RH_Config 中的 API 密钥
2. 验证网络连接
3. 检查遮罩文件大小（< 10MB）

#### 问题："No file identifier found"

**解决方案**：上传成功但响应格式不符合预期。检查 RunningHub API 文档以获取正确的响应格式。

