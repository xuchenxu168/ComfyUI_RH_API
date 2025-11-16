# ComfyUI_RH_API 示例工作流

本目录包含专业的示例工作流，演示如何在 ComfyUI 中使用 RunningHub API 节点。

## 📁 可用工作流

### 1. **workflow_text_to_image.json** - 基础文本生成图像
**难度：** ⭐ 初学者

一个简单的工作流，从文本提示生成图像。

**使用的节点：**
- RH_Config
- RH_Param
- RH_Execute
- PreviewImage
- RH_TextDisplay

**功能：**
1. 配置 RunningHub API 连接
2. 设置文本提示参数
3. 在 RunningHub 上执行工作流
4. 显示生成的图像
5. 自动保存图像到 `ComfyUI/output/`

**使用方法：**
1. 在 ComfyUI 中打开工作流
2. 将 `your_api_key_here` 替换为你的实际 API 密钥
3. 将 `your_workflow_id_here` 替换为你的工作流 ID
4. 在 RH_Param 节点中修改提示词
5. 点击 "Queue Prompt"

---

### 2. **workflow_image_to_image.json** - 图像到图像转换
**难度：** ⭐⭐ 中级

上传图像并使用 RunningHub 工作流进行转换。

**使用的节点：**
- RH_Config
- LoadImage
- RH_UploadImage
- RH_Param (x2, 链式)
- RH_Execute
- PreviewImage

**功能：**
1. 加载本地图像
2. 上传到 RunningHub
3. 链接多个参数（图像哈希 + 文本提示）
4. 执行图像到图像转换
5. 显示并保存结果

**使用方法：**
1. 将图像放入 ComfyUI 的输入文件夹
2. 更新 LoadImage 节点选择你的图像
3. 配置 API 密钥和工作流 ID
4. 调整转换提示词
5. 运行工作流

---

### 3. **workflow_ai_app.json** - AI 应用执行
**难度：** ⭐ 初学者

执行 RunningHub 上发布的 AI 应用。

**使用的节点：**
- RH_Config (设置 `is_ai_app: true`)
- RH_Param
- RH_Execute
- PreviewImage
- RH_TextDisplay

**功能：**
1. 连接到 RunningHub AI 应用
2. 发送输入参数
3. 接收图像和文本输出
4. 在 ComfyUI 中显示结果

**使用方法：**
1. 从 RunningHub 获取你的 AI 应用 ID
2. 在 RH_Config 中将 `is_ai_app` 设置为 `true`
3. 配置输入参数
4. 执行并查看结果

---

### 4. **workflow_advanced_batch.json** - 高级批量处理
**难度：** ⭐⭐⭐ 高级

使用链式参数生成多张图像并选择特定输出。

**使用的节点：**
- RH_Config
- RH_Param (x3, 链式)
- RH_Execute (高性能模式)
- PreviewImage
- RH_ImageSelector
- SaveImage
- RH_TextDisplay

**功能：**
1. 链接多个参数（提示词、种子、步数）
2. 使用高性能实例（RTX 4090）
3. 生成批量图像
4. 从批次中选择特定图像
5. 单独保存选中的图像
6. 显示任何文本输出

**使用方法：**
1. 配置所有三个参数
2. 根据需要启用高性能模式
3. 运行工作流
4. 使用 RH_ImageSelector 选择你喜欢的图像
5. 选中的图像会以自定义前缀保存

---

### 5. **workflow_video_generation.json** - 视频生成
**难度：** ⭐⭐⭐ 高级

使用 RunningHub 的视频工作流从图像生成视频。

**使用的节点：**
- RH_Config
- LoadImage
- RH_UploadImage
- RH_Param (x2, 链式)
- RH_Execute (延长超时)
- PreviewImage

**功能：**
1. 加载起始帧图像
2. 上传到 RunningHub
3. 添加运动参数
4. 生成视频
5. 提取并显示视频帧
6. 保存视频文件到本地磁盘

**使用方法：**
1. 准备起始帧图像
2. 配置运动提示词
3. 设置更长的超时时间（900秒）用于视频生成
4. 运行并等待视频处理
5. 视频保存到 `ComfyUI/output/`

---

## 🎯 快速开始指南

### 步骤 1：获取 API 凭证

1. 访问 [RunningHub](https://www.runninghub.cn)
2. 注册或登录
3. 进入 API 设置
4. 复制你的 API 密钥

### 步骤 2：查找工作流/应用 ID

**对于工作流：**
1. 在 RunningHub 中打开你的工作流
2. 查看 URL：`https://www.runninghub.cn/workflow/{workflow_id}`
3. 复制工作流 ID

**对于 AI 应用：**
1. 将工作流发布为 AI 应用
2. 在应用设置中找到应用 ID
3. 复制应用 ID

### 步骤 3：导入工作流

1. 打开 ComfyUI
2. 点击 "Load" 按钮
3. 导航到 `custom_nodes/ComfyUI_RH_API/examples/`
4. 选择一个工作流 JSON 文件
5. 点击 "Open"

### 步骤 4：配置

1. 找到 **RH_Config** 节点
2. 将 `your_api_key_here` 替换为你的 API 密钥
3. 将 `your_workflow_id_here` 替换为你的工作流/应用 ID
4. 根据需要调整其他参数

### 步骤 5：执行

1. 点击 "Queue Prompt" 按钮
2. 在控制台中观察进度
3. 在 PreviewImage 节点中查看结果
4. 在 `ComfyUI/output/` 文件夹中找到保存的文件

---

## 📝 节点参数参考

### RH_Config
- **api_key**: 你的 RunningHub API 密钥
- **workflow_or_app_id**: 工作流 ID 或 AI 应用 ID
- **base_url**: API 端点（默认：https://www.runninghub.cn）
- **is_ai_app**: AI 应用设置为 `true`，工作流设置为 `false`

### RH_Param
- **node_id**: RunningHub 工作流中的节点 ID
- **field_name**: 参数名称（例如 "text"、"image"、"seed"）
- **field_value**: 要设置的值（可以从其他节点连接）
- **previous_params**: （可选）通过连接前一个 RH_Param 节点来链接多个参数

### RH_Execute
- **timeout**: 最大等待时间（秒）（默认：600）
- **use_high_performance**: 使用 RTX 4090 实例（消耗更多积分）
- **save_to_local**: 自动保存输出到磁盘（默认：true）
- **output_prefix**: 保存文件的文件名前缀（默认："RH"）

---

## 💡 提示和最佳实践

### 1. **参数链接**
链接多个 RH_Param 节点以发送多个参数：
```
RH_Param (提示词) → RH_Param (种子) → RH_Param (步数) → RH_Execute
```

### 2. **文件命名**
为不同项目使用描述性前缀：
- `output_prefix: "人像"` → `人像_20251115_143022_001.png`
- `output_prefix: "风景"` → `风景_20251115_143022_001.png`

### 3. **超时设置**
- 图像：300-600 秒
- 视频：900-1800 秒
- 复杂工作流：1200+ 秒

### 4. **高性能模式**
适用于：
- 大批量生成
- 高分辨率输出
- 复杂工作流
- 更快的处理速度

### 5. **错误处理**
如果执行失败：
1. 检查 API 密钥是否正确
2. 验证工作流/应用 ID
3. 确保参数与你的工作流匹配
4. 查看控制台的错误消息
5. 尝试增加超时时间

---

## 🔧 故障排除

### "Invalid API key"（无效的 API 密钥）
- 仔细检查你的 API 密钥
- 确保没有多余的空格
- 如需要可重新生成密钥

### "Workflow not found"（找不到工作流）
- 验证工作流 ID 是否正确
- 检查工作流是否已发布
- 对于 AI 应用，使用应用 ID 而不是工作流 ID

### "Timeout error"（超时错误）
- 增加超时值
- 检查 RunningHub 服务器状态
- 在非高峰时段重试

### "No outputs"（无输出）
- 验证你的工作流是否产生输出
- 检查节点 ID 是否与你的工作流匹配
- 查看 RunningHub 执行日志

---

## 📚 其他资源

- [主 README](../README_CN.md) - 完整文档
- [快速开始指南](../QUICKSTART.md) - 5分钟设置
- [文件保存功能](../FILE_SAVING_FEATURE.md) - 自动保存文档
- [RunningHub 文档](https://www.runninghub.cn/docs) - 官方 API 文档

---

## 🎨 示例用例

1. **批量人像生成**：使用 workflow_advanced_batch.json 配合人像提示词
2. **风格迁移**：使用 workflow_image_to_image.json 配合风格提示词
3. **Logo 创建**：使用 workflow_ai_app.json 配合 logo 生成应用
4. **动画制作**：使用 workflow_video_generation.json 进行图像到视频
5. **产品样机**：使用参数链接多个转换

---

**祝创作愉快！🚀**

