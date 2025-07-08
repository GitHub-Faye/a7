from django.test import TestCase
from rest_framework.exceptions import ValidationError
from marp_service.serializers import MarpConversionSerializer
from marp_service.utils import OutputFormat, DEFAULT_THEMES


class MarpConversionSerializerTests(TestCase):
    """测试MarpConversionSerializer的功能"""
    
    def test_valid_data(self):
        """测试有效的数据能否成功验证"""
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'pdf',
            'theme': 'default'
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['format'], 'pdf')
    
    def test_valid_data_without_theme(self):
        """测试没有提供theme时验证仍然通过"""
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'pdf',
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_valid_data_with_null_theme(self):
        """测试theme为null时验证仍然通过"""
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'pdf',
            'theme': None
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_valid_data_with_uppercase_format(self):
        """测试大写格式会被转换为小写并通过验证"""
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'PDF',
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['format'], 'pdf')
    
    def test_invalid_format(self):
        """测试无效的格式会被拒绝"""
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'invalid',
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('format', serializer.errors)
    
    def test_missing_required_field(self):
        """测试缺少必填字段时验证失败"""
        # 缺少content
        data = {
            'format': 'pdf',
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
        
        # 缺少format
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('format', serializer.errors)
    
    def test_non_default_theme(self):
        """测试使用非默认主题不会引发验证错误"""
        data = {
            'content': '# Test Markdown\n\nThis is a test slide',
            'format': 'pdf',
            'theme': 'non-existent-theme'
        }
        
        serializer = MarpConversionSerializer(data=data)
        self.assertTrue(serializer.is_valid()) 