# ⚠️ Mask Upload Limitation / 遮罩上传限制

## 问题确认

经过测试确认：**RunningHub API 不支持直接上传遮罩文件**。

### 测试结果

- ✅ 遮罩文件可以上传到服务器
- ❌ 上传后的遮罩无法在工作流中正确使用
- ❌ 任务执行时卡住，无法完成

## 根本原因

RunningHub 的架构设计：

1. **云端工作流执行** - 工作流在 RunningHub 服务器上运行
2. **参数传递限制** - API 只支持传递简单参数（文本、数字、文件路径）
3. **遮罩生成方式** - 遮罩应该在云端工作流内部生成，而不是从外部上传

## 正确的使用方式

### ❌ 错误方式：从本地上传遮罩

```
本地 ComfyUI:
  LoadImage → 生成遮罩 → 上传遮罩 → RunningHub
                                        ↓
                                    ❌ 无法使用
```

### ✅ 正确方式：在云端工作流中生成遮罩

```
本地 ComfyUI:
  LoadImage → 上传图像 → RunningHub
                            ↓
                        云端工作流:
                          接收图像 → 生成遮罩 → 使用遮罩 → 返回结果
```

## 解决方案

### 方案 1: 在 RunningHub 工作流中生成遮罩（推荐）

**步骤：**

1. **在 RunningHub 上创建工作流**，包含遮罩生成节点：
   ```
   LoadImage → ImageToMask → InpaintModelConditioning → KSampler
   ```

2. **从本地上传原始图像**：
   ```
   本地: RH_UploadImage → RH_Param → RH_Execute
   ```

3. **在云端工作流中处理**：
   - 接收上传的图像
   - 使用 ImageToMask 或其他节点生成遮罩
   - 应用遮罩进行处理
   - 返回结果

**优点：**
- ✅ 完全兼容 RunningHub API
- ✅ 遮罩生成在云端，更灵活
- ✅ 可以使用各种遮罩生成方法

### 方案 2: 使用遮罩编辑器（如果 RunningHub 支持）

某些 RunningHub 工作流可能支持内置的遮罩编辑器：

1. 在 RunningHub 网站上打开工作流
2. 上传图像
3. 使用内置的遮罩编辑器绘制遮罩
4. 执行工作流

**优点：**
- ✅ 可视化编辑遮罩
- ✅ 直接在 RunningHub 上操作

**缺点：**
- ❌ 无法通过 API 自动化
- ❌ 需要手动操作

### 方案 3: 将遮罩嵌入图像的 Alpha 通道

如果云端工作流支持，可以将遮罩作为 Alpha 通道：

1. **在本地合并图像和遮罩**：
   ```python
   # 将遮罩作为 Alpha 通道
   image_rgba = Image.merge('RGBA', [r, g, b, mask])
   ```

2. **上传 RGBA 图像**：
   ```
   RH_UploadImage → RH_Param → RH_Execute
   ```

3. **在云端提取 Alpha 通道**：
   ```
   LoadImage → SplitImageWithAlpha → 使用 Alpha 作为遮罩
   ```

**优点：**
- ✅ 可以通过 API 传递遮罩
- ✅ 标准的图像格式

**缺点：**
- ❌ 需要云端工作流支持 Alpha 通道提取
- ❌ 需要修改本地和云端工作流

## RH_UploadMask 节点的状态

### 当前状态

- ⚠️ **已实现但不可用**
- ⚠️ **API 不支持遮罩上传**
- ⚠️ **建议不要使用此节点**

### 建议

1. **保留节点代码** - 以备将来 API 支持
2. **添加警告** - 在节点中显示警告信息
3. **更新文档** - 说明限制和替代方案

## 替代工作流示例

### 示例 1: 云端生成遮罩的修复工作流

**RunningHub 工作流（云端）：**
```
1. LoadImage (接收上传的图像)
2. ImageToMask (生成遮罩，例如基于颜色)
3. InpaintModelConditioning (使用遮罩)
4. KSampler (生成修复后的图像)
5. SaveImage (返回结果)
```

**本地 ComfyUI 工作流：**
```
1. LoadImage (加载本地图像)
2. RH_UploadImage (上传到 RunningHub)
3. RH_Param (设置图像参数)
4. RH_Param (设置提示词等其他参数)
5. RH_Execute (执行云端工作流)
6. PreviewImage (查看结果)
```

### 示例 2: 使用预定义遮罩区域

如果遮罩区域是固定的（例如总是中心区域）：

**RunningHub 工作流（云端）：**
```
1. LoadImage (接收上传的图像)
2. CreateMask (创建固定区域的遮罩，例如中心 512x512)
3. InpaintModelConditioning (使用遮罩)
4. KSampler (生成修复后的图像)
5. SaveImage (返回结果)
```

## 技术分析

### 为什么 API 不支持遮罩上传？

1. **架构限制**：
   - RunningHub API 设计用于传递参数，而不是复杂的数据结构
   - 遮罩是张量数据，不是简单的文件路径

2. **工作流设计**：
   - ComfyUI 工作流中的遮罩是节点之间传递的张量
   - API 只能设置节点的输入参数，不能直接注入张量

3. **安全性**：
   - 允许上传任意张量数据可能带来安全风险
   - 限制为文件上传更安全

### 对比：图像 vs 遮罩

| 特性 | 图像上传 | 遮罩上传 |
|------|----------|----------|
| 上传方式 | ✅ 文件上传 | ❌ 不支持 |
| 在工作流中使用 | ✅ LoadImage 节点 | ❌ 无法直接使用 |
| API 支持 | ✅ 完全支持 | ❌ 不支持 |
| 替代方案 | - | ✅ 云端生成 |

## 结论

**RH_UploadMask 节点无法在当前的 RunningHub API 架构下工作。**

**推荐做法：**
1. ✅ 在 RunningHub 云端工作流中生成遮罩
2. ✅ 从本地只上传原始图像
3. ✅ 使用云端的遮罩生成节点（ImageToMask、SegmentAnything 等）
4. ❌ 不要尝试从本地上传遮罩

## 下一步

1. **更新文档** - 说明限制
2. **添加警告** - 在 RH_UploadMask 节点中显示警告
3. **提供示例** - 展示如何在云端生成遮罩
4. **联系 RunningHub** - 询问是否有计划支持遮罩上传

---

**如果你需要使用遮罩功能，请在 RunningHub 上创建包含遮罩生成的完整工作流。**

