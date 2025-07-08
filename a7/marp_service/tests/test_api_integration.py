import os
import tempfile
import unittest
import shutil
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from marp_service.utils import OutputFormat

# 检查marp-cli是否在系统PATH中
MARP_CLI_INSTALLED = shutil.which('marp') is not None

# 如果环境变量中指定跳过集成测试，也会跳过
if os.environ.get('SKIP_MARP_INTEGRATION_TESTS'):
    MARP_CLI_INSTALLED = False


@unittest.skipIf(not MARP_CLI_INSTALLED, "Marp CLI未安装或环境变量设置为跳过，跳过集成测试")
class MarpAPIIntegrationTests(TestCase):
    """测试Marp API端点与实际转换服务的集成"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.url = reverse('marp_service:convert')
        self.test_markdown = """
# Test Presentation

---

## Slide 2

- Bullet 1
- Bullet 2

---

## Slide 3

```python
def hello():
    print("Hello World")
```
"""
    
    def test_pdf_conversion(self):
        """测试PDF转换"""
        data = {
            'content': self.test_markdown,
            'format': 'pdf'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="presentation.pdf"')
        
        # 验证响应确实包含数据
        self.assertTrue(len(response.content) > 0)
        
        # 释放响应资源
        response.close()
    
    def test_html_conversion(self):
        """测试HTML转换"""
        data = {
            'content': self.test_markdown,
            'format': 'html'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="presentation.html"')
        
        # 验证HTML内容
        content = response.content.decode('utf-8')
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('Test Presentation', content)
        
        # 释放响应资源
        response.close()
    
    def test_with_theme(self):
        """测试使用主题"""
        data = {
            'content': self.test_markdown,
            'format': 'html',
            'theme': 'default'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证HTML内容
        content = response.content.decode('utf-8')
        self.assertIn('<!DOCTYPE html>', content)
        # 这里可以添加更多与主题相关的断言
        
        # 释放响应资源
        response.close() 