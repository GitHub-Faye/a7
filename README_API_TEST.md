# 知识点到PPT API端到端测试工具

这个测试工具用于验证知识点到PPT的直接下载功能，确保API在真实环境中正常工作。

## 功能特点

- 测试知识点到PPT的直接下载功能
- 测试Base64编码文件内容返回功能
- 支持多种格式测试(PPTX/PDF/HTML)
- 生成详细的HTML测试报告
- 保存下载的文件以供检查

## 使用方法

### 前提条件

确保已安装以下依赖：
```bash
pip install requests
```

### 运行测试

基本用法：
```bash
python api_test_runner.py --knowledge-ids "1,2,3"
```

完整参数：
```bash
python api_test_runner.py --url "http://localhost:8000" --knowledge-ids "1,2,3" --token "可选的认证令牌"
```

### 参数说明

- `--url`: API基础URL，默认为 http://localhost:8000
- `--knowledge-ids`: 要测试的知识点ID列表，用逗号分隔，例如 "1,2,3"
- `--token`: 可选的认证令牌，用于需要认证的API

### 测试流程

1. 测试工具会依次测试：
   - 直接下载PPTX格式
   - 直接下载PDF格式
   - 直接下载HTML格式
   - Base64编码返回PPTX格式
   - Base64编码返回PDF格式

2. 每个测试会：
   - 发送API请求
   - 测量响应时间
   - 保存下载的文件
   - 记录文件大小和其他信息

3. 所有测试完成后：
   - 生成HTML格式的测试报告
   - 在控制台显示测试结果摘要

## 输出文件

所有输出文件保存在 `api_test_output` 目录：
- 下载的演示文稿文件
- HTML测试报告

## 示例

测试本地服务器上的知识点：
```bash
python api_test_runner.py --knowledge-ids "1,2,3"
```

测试远程服务器上的知识点：
```bash
python api_test_runner.py --url "https://example.com" --knowledge-ids "5,6,7" --token "your_auth_token"
```

## 测试报告

测试完成后，会在 `api_test_output` 目录中生成一个HTML测试报告，包含：
- 测试摘要（成功率、总测试数等）
- 每个测试的详细结果
- 响应时间和文件大小统计
- 错误信息（如果有）

## 故障排除

如果测试失败，请检查：
1. API服务器是否正常运行
2. 知识点ID是否存在
3. 认证令牌是否有效（如果需要）
4. 网络连接是否正常

## 注意事项

- 确保提供的知识点ID在系统中存在
- 大型演示文稿可能需要较长的处理时间
- 测试会生成多个文件，请确保有足够的磁盘空间 