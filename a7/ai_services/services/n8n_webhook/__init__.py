"""
n8n Webhook服务包

提供与n8n工作流平台集成的服务
"""

from .client import N8nWebhookClient
from .exceptions import (
    N8nWebhookError,
    N8nConnectionError,
    N8nTimeoutError,
    N8nResponseError,
)
from .formats import (
    format_student_dialogue_response,
    format_question_generation_response,
    format_exercise_generation_response,
    format_answer_correction_response,
    format_course_generation_response,
    format_knowledge_to_markdown_response,
)
from . import prompt_templates

__all__ = [
    'N8nWebhookClient',
    'N8nWebhookError',
    'N8nConnectionError',
    'N8nTimeoutError',
    'N8nResponseError',
    'format_student_dialogue_response',
    'format_question_generation_response',
    'format_exercise_generation_response',
    'format_answer_correction_response',
    'format_course_generation_response',
    'format_knowledge_to_markdown_response',
    'prompt_templates',
] 