# Marp转换服务REST API端点实施计划 (任务15.3)

## 任务概述
根据任务15.3的要求，我们需要设计和实现REST API端点，用于接收Markdown内容，并将其转换为各种演示格式（PDF、PPTX、HTML、PNG）。

## 当前状态分析
1. marp_service应用已实现服务层功能，包括：
   - convert_markdown_to_format 方法：将Markdown内容转换为指定格式
   - convert_file_to_format 方法：将Markdown文件转换为指定格式
   - 支持的格式：PDF、PPTX、HTML、PNG
   - 支持可选主题应用
   - 提供完善的异常处理和临时文件管理

2. 尚未实现的部分：
   - RESTful API端点
   - 输入验证
   - 文件下载响应
   - 错误处理和HTTP状态码映射
   - 大文件上传处理

## API设计

### 1. `/api/marp/convert` 端点设计

#### HTTP方法: POST

#### 请求体格式 (JSON):
```json
{
  "content": "# Markdown内容\n\n幻灯片内容...",
  "format": "pdf", // 可选值: "pdf", "pptx", "html", "png"
  "theme": "default" // 可选参数，默认为null
}
```

#### 响应格式:
- 成功: 返回转换后的文件（适当的Content-Type和Content-Disposition头）
- 错误: 返回JSON格式错误信息
```json
{
  "success": false,
  "error": "不支持的输出格式: xyz。支持的格式有: pdf, pptx, html, png"
}
```

#### HTTP状态码:
- 200 OK: 成功转换并返回文件
- 400 Bad Request: 请求参数无效
- 415 Unsupported Media Type: 不支持的格式
- 500 Internal Server Error: 服务器内部错误

### 2. 文件上传端点 (可选扩展功能)

#### HTTP方法: POST

#### 端点: `/api/marp/convert-file`

#### 请求格式: multipart/form-data
- file: Markdown文件
- format: 输出格式
- theme: 可选主题

#### 响应格式:
- 与上一个端点相同

## 实施步骤

### 1. 创建序列化器
创建 `MarpConversionSerializer` 用于验证和反序列化输入数据。

### 2. 创建API视图
实现 `MarpConversionView` 类，处理POST请求，使用service层函数进行转换，并返回适当的响应。

### 3. 定义URL配置
添加API路由到 `marp_service/urls.py` 并确保在主URLs配置中包含。

### 4. 增强错误处理
确保API端点能够适当处理和报告所有可能的错误情况。

### 5. 添加文件上传支持
实现文件上传和处理逻辑，处理大型文件上传。

### 6. 配置权限
根据项目权限策略配置API端点的访问权限。

## 测试策略

### 1. 单元测试
- 测试序列化器验证
- 测试视图逻辑
- 测试错误处理路径

### 2. 集成测试
- 测试实际Markdown转换和文件下载
- 测试不同格式和主题组合
- 测试边缘情况（空内容、非常大的内容）



## 实现注意事项
1. 使用 `FileResponse` 返回生成的文件
2. 正确设置Content-Type和Content-Disposition头部
3. 确保临时文件在请求结束后被清理
4. 添加适当的日志记录，特别是错误情况


## 时间估算
- 序列化器和视图实现: 1小时
- URL配置和基础功能测试: 30分钟
- 文件上传支持: 1小时
- 完整测试套件: 1.5小时
- 总计: 约4小时