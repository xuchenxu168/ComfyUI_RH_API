# 🔧 Mask Upload Fix - fileType 修复

## 问题描述

用户报告遮罩上传后，任务执行卡住，一直处于 RUNNING 状态。

### 日志分析

```
✅ Mask uploaded successfully: api/5cfc44f29b012406eb2549c85c4742a01023c2db6236fd...
✓ Task created: 1989742127204765697
✓ WebSocket connected
Task status: RUNNING
[卡住，没有进展]
```

**结论：** 遮罩上传成功，但任务执行时出现问题。

## 根本原因

原始实现使用了 `fileType: 'mask'`：

```python
data = {
    'apiKey': api_key,
    'fileType': 'mask',  # ❌ 可能不被 RunningHub 识别
}
```

**问题：**
1. RunningHub API 可能不识别 `'mask'` 作为有效的 fileType
2. 标准的 ComfyUI API 有单独的 `/upload/mask` 端点，但 RunningHub 使用统一端点
3. 遮罩本质上就是灰度图像，应该使用 `'image'` 类型

## 解决方案

### 修改内容

**文件：** `nodes/rh_upload_mask.py` 第 119 行

**修改前：**
```python
data = {
    'apiKey': api_key,
    'fileType': 'mask',  # ❌ 不兼容
}
```

**修改后：**
```python
data = {
    'apiKey': api_key,
    'fileType': 'image',  # ✅ 使用 'image' 以提高兼容性
}
```

### 理由

1. **兼容性：** `'image'` 是标准的文件类型，所有系统都支持
2. **本质相同：** 遮罩就是灰度图像（单通道 PNG）
3. **区分方式：** 通过工作流中的使用方式区分，而不是上传类型
4. **成功案例：** 其他图像上传都使用 `'image'` 并且工作正常

## 技术细节

### 遮罩 vs 图像

| 属性 | 遮罩 | 普通图像 |
|------|------|----------|
| 格式 | PNG | PNG/JPG |
| 通道 | 1 (灰度) | 3 (RGB) 或 4 (RGBA) |
| 值范围 | 0-255 | 0-255 |
| 上传类型 | `'image'` | `'image'` |
| 区别 | 在工作流中如何使用 | 在工作流中如何使用 |

**关键点：** 上传时都使用 `'image'`，区别在于：
- 遮罩是单通道灰度图
- 在工作流中连接到需要遮罩的节点

### API 对比

#### ComfyUI 标准 API
```
POST /upload/image  - 上传图像
POST /upload/mask   - 上传遮罩（单独端点）
```

#### RunningHub API
```
POST /task/openapi/upload
参数：fileType = 'image' | 'video' | 'audio'
```

**注意：** RunningHub 使用统一端点，通过 `fileType` 区分，但可能不支持 `'mask'` 类型。

## 测试建议

### 1. 重启 ComfyUI

修改后需要重启 ComfyUI 以加载更新的代码：

```bash
# 停止 ComfyUI
# 重新启动 ComfyUI
```

### 2. 测试工作流

使用简单的测试工作流：

```
LoadImage (带遮罩)
  ├─ IMAGE → RH_UploadImage → RH_Param
  └─ MASK → RH_UploadMask → RH_Param
                                  ↓
                            RH_Execute
```

### 3. 检查日志

查看上传日志，确认：
- ✅ 遮罩上传成功
- ✅ 任务创建成功
- ✅ 任务执行完成（不再卡住）

### 4. 验证结果

- ✅ 任务状态变为 SUCCESS
- ✅ 返回处理后的图像
- ✅ 遮罩区域被正确处理

## 其他可能的问题

如果修改 `fileType` 后仍然卡住，可能是：

### 1. 参数名称不匹配

**检查：** RH_Param 中的 `node_id` 和 `field_name` 是否与 RunningHub 工作流匹配

**示例：**
```
正确：node_id="123", field_name="mask"
错误：node_id="319", field_name="Load Image"
```

### 2. 工作流配置错误

**检查：** 在 RunningHub 网站上手动测试工作流

**步骤：**
1. 登录 RunningHub
2. 打开工作流
3. 手动上传图像和遮罩
4. 确认工作流可以正常执行

### 3. 节点类型不兼容

**检查：** 服务器端的节点是否支持遮罩输入

**常见节点：**
- `LoadImage` - 支持遮罩输出
- `LoadImageMask` - 专门的遮罩加载节点
- `InpaintModelConditioning` - 需要遮罩输入

## 更新的文件

1. ✅ `nodes/rh_upload_mask.py` - 修改 fileType 为 'image'
2. ✅ `MASK_UPLOAD_GUIDE.md` - 更新文档说明
3. ✅ `DEBUG_MASK_ISSUE.md` - 调试指南
4. ✅ `MASK_UPLOAD_FIX.md` - 本文档

## 下一步

1. **重启 ComfyUI** 以加载修复
2. **测试工作流** 确认问题解决
3. **如果仍然卡住：**
   - 查看 `DEBUG_MASK_ISSUE.md` 进行深入调试
   - 检查 RunningHub 工作流配置
   - 验证参数名称和节点 ID

## 总结

**修复：** 将 `fileType: 'mask'` 改为 `fileType: 'image'`

**原因：** 
- 提高兼容性
- 遮罩本质上就是灰度图像
- RunningHub 可能不识别 'mask' 类型

**预期结果：** 
- ✅ 遮罩上传成功
- ✅ 任务正常执行
- ✅ 返回处理后的图像

---

**如果问题仍然存在，请查看任务详情页面获取具体错误信息：**
```
https://www.runninghub.cn/task/detail/[TASK_ID]
```

