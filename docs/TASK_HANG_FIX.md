# 🔧 Task Hang Issue Fix / 任务卡死问题修复

## ✅ 问题已完全解决！

**最终解决方案：禁用 WebSocket，使用 HTTP 轮询**

**根本原因：**
1. ❌ **WebSocket 在某些网络环境下会阻塞监控循环** - 特别是有代理的情况
2. ❌ **API 响应处理顺序错误** - `code=804` 被错误地当作错误处理
3. ❌ **第一次轮询延迟 5 秒** - 导致任务完成检测延迟

**测试结果：**
- ✅ 禁用 WebSocket 后：完美工作，82 秒成功完成
- ❌ 启用 WebSocket 后：监控循环卡死，无法继续轮询
- ✅ HTTP 轮询：稳定可靠，5 秒间隔完全可接受

---

## 问题描述

**症状：**
- RunningHub 上的任务已经完成（图片已生成）
- ComfyUI 这边一直显示 "Task status: RUNNING"
- 控制台不断输出 "Use Proxy: http://127.0.0.1:7897"（来自 ComfyUI 系统，不是我们的代码）
- 任务永远不会完成，直到超时

**影响：**
- 用户需要等待超时（默认 600 秒）
- 无法获取已生成的结果
- 浪费时间和资源

---

## 根本原因分析

### 1. WebSocket 阻塞主循环 ⚠️ **最严重的问题**

**问题：**
- WebSocket 库在连接失败时会阻塞调用线程
- 即使在 daemon 线程中运行，stderr 输出也会影响主线程
- "Use Proxy" 消息来自 websocket 库，表示连接不断重试

**影响：**
- **监控循环完全卡住**，无法执行 HTTP 轮询
- 只能看到第一次轮询 `[0s]`，之后就没有任何输出
- 任务完成了也检测不到

**测试验证：**
禁用 WebSocket 后，HTTP 轮询正常工作：
```
[0s] Checking task status via HTTP...
[5s] Checking task status via HTTP...
[10s] Checking task status via HTTP...
...
[82s] Checking task status via HTTP...
✓ Task completed successfully!
```

### 2. API 响应处理顺序错误

**问题：**
- RunningHub API 返回 `code=804, msg='APIKEY_TASK_IS_RUNNING'`
- 原代码先检查 `code != 0`，将其当作错误
- 应该先检查 `msg`，因为 `msg` 是最可靠的状态指示器

**错误的处理顺序：**
```python
# ❌ 错误：先检查 code
if code == 0 and data:
    return data
if code != 0:  # 804 被当作错误！
    return {"taskStatus": "error"}
if msg == "APIKEY_TASK_IS_RUNNING":  # 永远不会执行到这里
    return {"taskStatus": "RUNNING"}
```

**正确的处理顺序：**
```python
# ✅ 正确：先检查 msg
if msg == "APIKEY_TASK_IS_RUNNING":
    return {"taskStatus": "RUNNING"}
if code == 0 and data:
    return data
if code != 0 and msg not in ["APIKEY_TASK_IS_RUNNING", ...]:
    return {"taskStatus": "error"}
```

### 3. 第一次轮询延迟

**问题：**
- `last_poll = time.time()` 在循环开始时设置
- `if time.time() - last_poll >= poll_interval` 需要等 5 秒
- 第一次轮询延迟 5 秒才执行

**修复：**
```python
last_poll = 0  # 设置为 0，立即触发第一次轮询
```

---

## 修复内容

### 修复 1: 禁用 WebSocket ⭐ **最终解决方案**

**文件：** `nodes/rh_execute.py` - `_create_task` 方法

**核心修复：完全禁用 WebSocket，只使用 HTTP 轮询**

```python
# WebSocket disabled - HTTP polling is more reliable
# WebSocket can cause blocking issues with certain proxy configurations
# HTTP polling works perfectly and is more stable
print("ℹ Using HTTP polling for task monitoring (WebSocket disabled for stability)")
```

**为什么禁用 WebSocket：**

1. **阻塞问题无法完全解决**
   - WebSocket 在有代理的环境下会阻塞监控循环
   - 即使在 daemon 线程中运行，仍然会影响主线程
   - 尝试了多种方法（重定向 stderr、禁用日志）都无法完全解决

2. **HTTP 轮询已经足够好**
   - ✅ 5 秒轮询间隔完全可接受
   - ✅ 稳定可靠，不受网络环境影响
   - ✅ 测试验证：82 秒任务完美完成
   - ✅ 不会有任何阻塞或卡死问题

3. **简单就是最好**
   - 减少复杂性和潜在问题
   - 更容易维护和调试
   - 用户体验更稳定

**效果：**
- ✅ **完全解决卡死问题** - 监控循环永远不会被阻塞
- ✅ **稳定可靠** - 不受网络代理影响
- ✅ **性能可接受** - 5 秒间隔对于云端任务来说完全够用

### 修复 2: 修正 API 响应处理顺序 ⭐ **关键修复**

**文件：** `nodes/rh_execute.py` - `_check_task_status` 方法

**核心修复：优先检查 `msg`，而不是 `code`**

```python
# === Priority 1: Check message first (most reliable indicator) ===

# Task queued
if msg == "APIKEY_TASK_IS_QUEUED":
    return {"taskStatus": "QUEUED"}

# Task running
if msg == "APIKEY_TASK_IS_RUNNING":
    return {"taskStatus": "RUNNING"}

# === Priority 2: Check for success with outputs ===

if code == 0 and isinstance(data, list) and data:
    return data

# === Priority 3: Check for errors ===

# Only treat as error if msg doesn't indicate running/queued
if code != 0 and msg not in ["APIKEY_TASK_IS_QUEUED", "APIKEY_TASK_IS_RUNNING"]:
    return {"taskStatus": "error", "error": msg}
```

**为什么这样修复：**
- ✅ `msg` 是最可靠的状态指示器
- ✅ `code=804` 配合 `msg='APIKEY_TASK_IS_RUNNING'` 表示正在运行，不是错误
- ✅ 避免将运行中的任务误判为错误

**效果：**
- ✅ 正确识别 `code=804` 为 RUNNING 状态
- ✅ 不会将运行中的任务当作错误
- ✅ 提供详细的 DEBUG 输出用于诊断

### 修复 3: 立即执行第一次轮询

**文件：** `nodes/rh_execute.py` - `_monitor_task` 方法

**修复：**
```python
last_poll = 0  # 设置为 0，而不是 time.time()
```

**效果：**
- ✅ 第一次轮询立即执行，不等待 5 秒
- ✅ 更快检测到任务完成

### 修复 4: 添加异常处理和调试信息

**文件：** `nodes/rh_execute.py` - `_monitor_task` 方法

**新增功能：**

1. **完整的异常处理：**
   ```python
   try:
       status = self._check_task_status(...)
   except Exception as check_error:
       print(f"❌ Error checking task status: {check_error}")
       continue
   ```

2. **显示任务详情链接：**
   ```python
   print(f"Task URL: https://www.runninghub.cn/task/detail/{task_id}")
   ```

3. **显示经过时间：**
   ```python
   print(f"[{int(elapsed)}s] Checking task status via HTTP...")
   ```

4. **卡住警告：**
   ```python
   if status_count > 10:
       print(f"⚠ Task has been {task_status} for {status_count * poll_interval}s")
   ```

**效果：**
- ✅ 捕获所有异常，不会导致循环卡死
- ✅ 用户可以手动检查任务状态
- ✅ 清楚看到等待时间和轮询进度
- ✅ 及时发现卡住问题

---

## 使用方法

### 1. 重启 ComfyUI

**重要：** 必须重启 ComfyUI 才能加载修复后的代码！

```bash
# 停止 ComfyUI
# 重新启动 ComfyUI
```

### 2. 运行工作流

正常运行你的工作流，现在你会看到更详细的调试信息：

```
DEBUG: API Response - code=0, msg='APIKEY_TASK_IS_RUNNING', data_type=NoneType
Task still initializing (code 0, no data yet)
[15s] Task status: RUNNING (check #3)
```

### 3. 查看调试信息

如果任务仍然卡住，查看控制台输出：

```
DEBUG: Full API response: {'code': 0, 'msg': '...', 'data': None}
```

将这些信息提供给开发者或 RunningHub 支持。

### 4. 手动检查任务

如果任务卡住超过 50 秒，会显示任务链接：

```
⚠ Task has been RUNNING for 50s
   Check task details: https://www.runninghub.cn/task/detail/1989754960986390529
```

点击链接查看任务实际状态。

---

## 预期效果

### 修复前：
```
✓ Task created: 1989754960986390529
Monitoring task...
Task status: RUNNING
Task status: RUNNING
Task status: RUNNING
[一直重复，直到超时]
Use Proxy: http://127.0.0.1:7897
Use Proxy: http://127.0.0.1:7897
[不断输出]
```

### 修复后：
```
✓ Task created: 1989754960986390529
Task ID: 1989754960986390529
Task URL: https://www.runninghub.cn/task/detail/1989754960986390529
Monitoring task...
DEBUG: API Response - code=0, msg='APIKEY_TASK_IS_RUNNING', data_type=NoneType
[5s] Task status: RUNNING (check #1)
DEBUG: API Response - code=0, msg='SUCCESS', data_type=list, data_len=2
✓ Task outputs received: 2 items
✓ Task completed successfully!
```

---

## 如果问题仍然存在

### 1. 检查 API 响应

查看控制台中的 DEBUG 输出：

```
DEBUG: API Response - code=?, msg='?', data_type=?
DEBUG: Full API response: {...}
```

### 2. 手动检查任务

访问任务详情页面：
```
https://www.runninghub.cn/task/detail/[TASK_ID]
```

查看：
- 任务是否真的完成了？
- 有没有错误信息？
- 输出结果是什么？

### 3. 检查网络

如果 HTTP 轮询也失败：

```bash
# 测试 API 连接
curl -X POST https://api.runninghub.cn/task/openapi/outputs \
  -H "Content-Type: application/json" \
  -d '{"taskId":"YOUR_TASK_ID","apiKey":"YOUR_API_KEY"}'
```

### 4. 联系支持

提供以下信息：
- 完整的控制台日志
- DEBUG 输出
- 任务 ID
- 任务详情页面截图

---

## 技术细节

### WebSocket vs HTTP 轮询

| 方式 | 优点 | 缺点 |
|------|------|------|
| **WebSocket** | 实时更新，低延迟 | 可能被代理阻断 |
| **HTTP 轮询** | 可靠，兼容性好 | 有延迟（5秒间隔） |

**策略：** 同时使用两种方式，任何一种成功都可以检测到任务完成。

### API 响应格式

RunningHub API 可能返回：

1. **任务完成（有输出）：**
   ```json
   {"code": 0, "msg": "SUCCESS", "data": [{...}, {...}]}
   ```

2. **任务运行中：**
   ```json
   {"code": 0, "msg": "APIKEY_TASK_IS_RUNNING", "data": null}
   ```

3. **任务排队：**
   ```json
   {"code": 0, "msg": "APIKEY_TASK_IS_QUEUED", "data": null}
   ```

4. **任务完成（无输出）：**
   ```json
   {"code": 0, "msg": "SUCCESS", "data": []}
   ```

5. **任务错误：**
   ```json
   {"code": 1, "msg": "错误信息", "data": null}
   ```

---

## 总结

✅ **修复了 WebSocket 代理问题**  
✅ **完善了 API 响应处理**  
✅ **添加了详细的调试信息**  
✅ **改进了任务监控和警告**  

**现在任务应该能够正确检测完成状态，不再卡死！** 🚀✨

