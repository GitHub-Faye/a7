from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import StudentAnswer, LearningRecord, Exercise
from .services.progress_tracker import ProgressTrackerService


@receiver(post_save, sender=StudentAnswer)
def update_progress_on_student_answer(sender, instance, created, **kwargs):
    """
    当学生提交答案时，更新练习题统计和知识点进度
    """
    # 如果是创建操作，更新练习题统计信息和知识点进度
    if created:
        # 获取相关练习题和知识点
        exercise = instance.exercise
        knowledge_point = exercise.knowledge_point
        student = instance.student
        
        # 更新练习题统计信息
        # 注意：在StudentAnswer的save方法中已更新练习题统计，此处为防止模型中的save方法被修改
        try:
            with transaction.atomic():
                ProgressTrackerService.update_exercise_statistics(
                    exercise=exercise,
                    is_correct=instance.is_correct,
                    save=True
                )
                
                # 更新知识点进度
                ProgressTrackerService.update_knowledge_point_progress(
                    student=student,
                    knowledge_point=knowledge_point
                )
        except Exception as e:
            # 记录错误但不中断流程
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"更新进度失败: {e}")
    
    # 如果是更新操作且is_correct字段发生变化，重新计算统计
    elif hasattr(instance, '_original_is_correct') and instance._original_is_correct != instance.is_correct:
        try:
            with transaction.atomic():
                # 更新相关知识点进度
                ProgressTrackerService.update_knowledge_point_progress(
                    student=instance.student,
                    knowledge_point=instance.exercise.knowledge_point
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"更新进度失败: {e}")


@receiver(post_save, sender=LearningRecord)
def update_course_progress_on_learning_record(sender, instance, created, **kwargs):
    """
    当学习记录更新时，更新课程整体进度
    """
    # 仅在学习记录发生显著变化时才触发更新
    should_update = created or kwargs.get('update_fields') and any(
        field in kwargs.get('update_fields', [])
        for field in ['progress', 'status', 'time_spent']
    )
    
    if should_update:
        try:
            with transaction.atomic():
                ProgressTrackerService.update_course_progress(
                    student=instance.student,
                    course=instance.course
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"更新课程进度失败: {e}") 