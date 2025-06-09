"""
pytest配置文件 - 包含全局fixtures和测试配置
"""

import pytest
import pytest_asyncio
import asyncio
from asgiref.sync import sync_to_async

from django.conf import settings


@pytest.fixture(scope='session')
def event_loop():
    """
    创建一个共享的事件循环，供整个测试会话使用
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 配置Django数据库访问
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    为所有测试启用数据库访问，无需单独标记每个测试函数
    """
    pass


# 调整Event Loop策略和配置测试标记
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    在测试开始前进行配置
    """
    # 设置Django时区等配置
    settings.USE_TZ = True
    
    # 注册自定义pytest标记
    config.addinivalue_line(
        "markers", "integration: 标记需要外部服务（如n8n）的集成测试"
    ) 