"""
问题格式验证和格式化模块

为AI生成的问题提供格式验证和标准化服务，确保生成的问题
符合系统定义的格式规范和教育标准。
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Union, Optional

logger = logging.getLogger(__name__)

class QuestionFormatValidator:
    """问题格式验证器，负责验证AI生成的问题是否符合规范"""
    
    # 题型定义
    SUPPORTED_TYPES = {
        'single_choice': '单选题',
        'multiple_choice': '多选题',
        'fill_blank': '填空题', 
        'short_answer': '简答题',
        'coding': '编程题',
        'other': '其他'
    }
    
    @staticmethod
    def validate_questions(questions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        验证问题列表格式
        
        Args:
            questions: 问题列表
            
        Returns:
            Tuple[List[Dict], List[str]]: 验证通过的问题列表和错误信息列表
        """
        validated_questions = []
        errors = []
        
        for i, question in enumerate(questions):
            try:
                validated = QuestionFormatValidator.validate_question(question)
                validated_questions.append(validated)
            except ValueError as e:
                errors.append(f"问题{i+1}格式错误: {str(e)}")
        
        return validated_questions, errors
    
    @staticmethod
    def validate_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单个问题格式
        
        Args:
            question: 问题数据
            
        Returns:
            Dict[str, Any]: 验证后的问题数据
            
        Raises:
            ValueError: 如果问题格式不符合规范
        """
        # 基本字段验证
        required_fields = ['title', 'content', 'type', 'difficulty', 'knowledge_point_id']
        for field in required_fields:
            if field not in question:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 验证标题不能为空
        if not question.get('title', '').strip():
            raise ValueError("问题标题不能为空")
            
        # 验证内容不能为空
        if not question.get('content', '').strip():
            raise ValueError("问题内容不能为空")
            
        # 验证知识点ID必须是整数
        try:
            kp_id = int(question.get('knowledge_point_id'))
            question['knowledge_point_id'] = kp_id
        except (TypeError, ValueError):
            raise ValueError("知识点ID必须是整数")
            
        # 验证难度级别
        try:
            difficulty = int(question.get('difficulty'))
            if not (1 <= difficulty <= 5):
                raise ValueError("难度级别必须在1-5之间")
            question['difficulty'] = difficulty
        except (TypeError, ValueError):
            raise ValueError("难度级别必须是1-5之间的整数")
        
        # 验证题型
        question_type = question.get('type')
        if question_type not in QuestionFormatValidator.SUPPORTED_TYPES:
            raise ValueError(f"不支持的题型: {question_type}，支持的题型: {', '.join(QuestionFormatValidator.SUPPORTED_TYPES.keys())}")
        
        # 调用对应题型的验证方法
        validator_method = getattr(
            QuestionFormatValidator, 
            f"validate_{question_type}_format", 
            QuestionFormatValidator.validate_default_format
        )
        
        return validator_method(question)
    
    @staticmethod
    def validate_single_choice_format(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单选题格式
        
        Args:
            question: 单选题数据
            
        Returns:
            Dict[str, Any]: 验证后的单选题数据
            
        Raises:
            ValueError: 如果单选题格式不符合规范
        """
        # 验证答案模板
        answer_template = question.get('answer_template')
        if not answer_template:
            raise ValueError("单选题必须包含答案模板(answer_template)")
            
        # 如果不是列表，尝试解析
        if isinstance(answer_template, str):
            try:
                # 尝试解析为JSON
                parsed = json.loads(answer_template)
                if isinstance(parsed, list):
                    question['answer_template'] = parsed
                else:
                    question['answer_template'] = [answer_template]
            except json.JSONDecodeError:
                # 如果无法解析为JSON，则作为单个选项
                question['answer_template'] = [answer_template]
        
        # 最终确保是列表
        if not isinstance(question.get('answer_template'), list):
            question['answer_template'] = [str(answer_template)]
            
        # 验证选项数量，单选题应至少有2个选项
        if len(question['answer_template']) < 2:
            raise ValueError("单选题至少需要2个选项")
            
        return question
    
    @staticmethod
    def validate_multiple_choice_format(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证多选题格式
        
        Args:
            question: 多选题数据
            
        Returns:
            Dict[str, Any]: 验证后的多选题数据
            
        Raises:
            ValueError: 如果多选题格式不符合规范
        """
        # 和单选题的验证逻辑相似
        answer_template = question.get('answer_template')
        if not answer_template:
            raise ValueError("多选题必须包含答案模板(answer_template)")
            
        # 如果不是列表，尝试解析
        if isinstance(answer_template, str):
            try:
                # 尝试解析为JSON
                parsed = json.loads(answer_template)
                if isinstance(parsed, list):
                    question['answer_template'] = parsed
                else:
                    question['answer_template'] = [answer_template]
            except json.JSONDecodeError:
                # 如果无法解析为JSON，则作为单个选项
                question['answer_template'] = [answer_template]
        
        # 最终确保是列表
        if not isinstance(question.get('answer_template'), list):
            question['answer_template'] = [str(answer_template)]
            
        # 验证选项数量，多选题应至少有3个选项
        if len(question['answer_template']) < 3:
            raise ValueError("多选题至少需要3个选项")
            
        return question
    
    @staticmethod
    def validate_fill_blank_format(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证填空题格式
        
        Args:
            question: 填空题数据
            
        Returns:
            Dict[str, Any]: 验证后的填空题数据
            
        Raises:
            ValueError: 如果填空题格式不符合规范
        """
        # 验证问题内容是否包含填空标记 
        content = question.get('content', '')
        if '___' not in content and '[BLANK]' not in content:
            logger.warning(f"填空题内容中未检测到填空标记('___'或'[BLANK]'): {content}")
            # 这只是警告，不阻止验证通过
            
        # 验证答案模板
        answer_template = question.get('answer_template')
        if not answer_template:
            raise ValueError("填空题必须包含答案模板(answer_template)")
            
        # 如果不是列表，尝试转换为列表
        if isinstance(answer_template, str):
            try:
                # 尝试解析为JSON
                parsed = json.loads(answer_template)
                if isinstance(parsed, list):
                    question['answer_template'] = parsed
                else:
                    question['answer_template'] = [answer_template]
            except json.JSONDecodeError:
                # 如果无法解析为JSON，则作为单个答案
                question['answer_template'] = [answer_template]
        
        # 最终确保是列表
        if not isinstance(question.get('answer_template'), list):
            question['answer_template'] = [str(answer_template)]
            
        return question
    
    @staticmethod
    def validate_short_answer_format(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证简答题格式
        
        Args:
            question: 简答题数据
            
        Returns:
            Dict[str, Any]: 验证后的简答题数据
            
        Raises:
            ValueError: 如果简答题格式不符合规范
        """
        # 简答题的答案模板可以是字符串或者列表
        answer_template = question.get('answer_template')
        if not answer_template:
            raise ValueError("简答题必须包含参考答案(answer_template)")
            
        # 保持原始类型，可以是字符串或列表
        return question
    
    @staticmethod
    def validate_coding_format(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证编程题格式
        
        Args:
            question: 编程题数据
            
        Returns:
            Dict[str, Any]: 验证后的编程题数据
            
        Raises:
            ValueError: 如果编程题格式不符合规范
        """
        # 编程题的答案模板应该是示例代码或解题思路
        answer_template = question.get('answer_template')
        if not answer_template:
            raise ValueError("编程题必须包含示例代码或解题思路(answer_template)")
            
        # 编程题的答案模板通常是字符串
        if isinstance(answer_template, list):
            question['answer_template'] = '\n'.join(answer_template)
            
        return question
    
    @staticmethod
    def validate_default_format(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        默认验证方法，用于未特别指定验证方法的题型
        
        Args:
            question: 问题数据
            
        Returns:
            Dict[str, Any]: 验证后的问题数据
        """
        # 确保存在答案模板字段
        if 'answer_template' not in question or question['answer_template'] is None:
            question['answer_template'] = ""
            
        return question


class QuestionFormatter:
    """问题格式化工具，负责标准化AI生成的问题格式"""
    
    @staticmethod
    def format_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化问题列表
        
        Args:
            questions: 问题列表
            
        Returns:
            List[Dict[str, Any]]: 格式化后的问题列表
        """
        formatted_questions = []
        
        for question in questions:
            try:
                # 获取对应题型的格式化方法，如果没有则使用默认方法
                formatter_method = getattr(
                    QuestionFormatter,
                    f"format_{question.get('type', '')}_question",
                    QuestionFormatter.format_default_question
                )
                formatted = formatter_method(question)
                formatted_questions.append(formatted)
            except Exception as e:
                logger.error(f"格式化问题时出错: {str(e)}")
                # 如果格式化失败，添加原始问题
                formatted_questions.append(question)
            
        return formatted_questions
    
    @staticmethod
    def format_single_choice_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化单选题
        
        Args:
            question: 单选题数据
            
        Returns:
            Dict[str, Any]: 格式化后的单选题数据
        """
        # 确保title和content是字符串
        if 'title' in question:
            question['title'] = str(question['title']).strip()
        
        if 'content' in question:
            question['content'] = str(question['content']).strip()
        
        # 确保answer_template是列表形式
        if 'answer_template' in question:
            answer_template = question['answer_template']
            
            # 如果是字符串，尝试解析为列表
            if isinstance(answer_template, str):
                try:
                    # 尝试解析为JSON列表
                    parsed = json.loads(answer_template)
                    if isinstance(parsed, list):
                        question['answer_template'] = parsed
                    else:
                        # 如果不是列表，转为单元素列表
                        question['answer_template'] = [answer_template]
                except (json.JSONDecodeError, TypeError):
                    # 尝试检查是否是文本形式的列表表示
                    if answer_template.strip().startswith('[') and answer_template.strip().endswith(']'):
                        try:
                            # 尝试再次解析，但先处理可能的单引号问题
                            cleaned = answer_template.replace("'", '"')
                            parsed = json.loads(cleaned)
                            if isinstance(parsed, list):
                                question['answer_template'] = parsed
                                return question
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    # 如果解析失败，将其作为单个选项
                    question['answer_template'] = [answer_template]
        
        return question
    
    @staticmethod
    def format_multiple_choice_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化多选题
        
        Args:
            question: 多选题数据
            
        Returns:
            Dict[str, Any]: 格式化后的多选题数据
        """
        # 多选题和单选题的格式化逻辑相同
        return QuestionFormatter.format_single_choice_question(question)
    
    @staticmethod
    def format_fill_blank_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化填空题
        
        Args:
            question: 填空题数据
            
        Returns:
            Dict[str, Any]: 格式化后的填空题数据
        """
        # 确保title和content是字符串
        if 'title' in question:
            question['title'] = str(question['title']).strip()
        
        if 'content' in question:
            question['content'] = str(question['content']).strip()
            
            # 确保填空题内容有填空标记
            content = question['content']
            if '___' not in content and '[BLANK]' not in content:
                # 添加简单标记以确保识别为填空题
                logger.warning(f"填空题内容缺少填空标记，已自动添加: {content}")
                question['content'] = f"{content} [填空: ___]"
        
        # 确保answer_template是列表形式，处理方式和单选题相同
        return QuestionFormatter.format_single_choice_question(question)
    
    @staticmethod
    def format_short_answer_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化简答题
        
        Args:
            question: 简答题数据
            
        Returns:
            Dict[str, Any]: 格式化后的简答题数据
        """
        # 确保title和content是字符串
        if 'title' in question:
            question['title'] = str(question['title']).strip()
        
        if 'content' in question:
            question['content'] = str(question['content']).strip()
        
        # 对于简答题，answer_template可以是字符串，不需要特殊处理
        # 但需要确保不是None
        if 'answer_template' in question and question['answer_template'] is None:
            question['answer_template'] = ""
        
        return question
    
    @staticmethod
    def format_coding_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化编程题
        
        Args:
            question: 编程题数据
            
        Returns:
            Dict[str, Any]: 格式化后的编程题数据
        """
        # 确保title和content是字符串
        if 'title' in question:
            question['title'] = str(question['title']).strip()
        
        if 'content' in question:
            question['content'] = str(question['content']).strip()
        
        # 编程题的答案模板通常是字符串形式的代码
        if 'answer_template' in question:
            if isinstance(question['answer_template'], list):
                # 如果是列表，合并为字符串
                question['answer_template'] = '\n'.join(str(item) for item in question['answer_template'])
            elif question['answer_template'] is None:
                question['answer_template'] = ""
            else:
                question['answer_template'] = str(question['answer_template'])
        
        return question
    
    @staticmethod
    def format_default_question(question: Dict[str, Any]) -> Dict[str, Any]:
        """
        默认格式化方法
        
        Args:
            question: 问题数据
            
        Returns:
            Dict[str, Any]: 格式化后的问题数据
        """
        # 确保基本字段是字符串形式
        if 'title' in question:
            question['title'] = str(question['title']).strip()
        
        if 'content' in question:
            question['content'] = str(question['content']).strip()
            
        # 确保answer_template存在且不为None
        if 'answer_template' in question and question['answer_template'] is None:
            question['answer_template'] = ""
            
        return question 