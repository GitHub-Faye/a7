from django.db import models, transaction
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from ..models import Exercise, KnowledgePoint, StudentAnswer, LearningRecord, CourseProgress, Course


class ProgressTrackerService:
    """
    学习进度跟踪服务，负责更新和管理学生的学习进度数据
    """
    
    @staticmethod
    def update_exercise_statistics(exercise, is_correct=None, save=True):
        """
        更新练习题的统计信息
        
        Args:
            exercise: Exercise模型实例
            is_correct: 答案是否正确，如果为None则仅更新统计不改变correct_count
            save: 是否保存更新后的Exercise对象
            
        Returns:
            更新后的Exercise对象
        """
        # 增加尝试次数
        exercise.attempt_count += 1
        
        # 如果指定了答案正确性，更新正确次数
        if is_correct:
            exercise.correct_count += 1
        
        if save:
            exercise.save(update_fields=['attempt_count', 'correct_count'])
        
        return exercise
    
    @staticmethod
    @transaction.atomic
    def update_knowledge_point_progress(student, knowledge_point):
        """
        更新学生在特定知识点的学习进度
        
        Args:
            student: User模型实例
            knowledge_point: KnowledgePoint模型实例
            
        Returns:
            (updated_record, progress_status) 元组，包含更新后的学习记录和进度状态变更标志
        """
        # 获取或创建学习记录
        learning_record, created = LearningRecord.objects.get_or_create(
            student=student,
            knowledge_point=knowledge_point,
            course=knowledge_point.course,
            defaults={
                'status': 'not_started',
                'progress': 0.0,
                'time_spent': 0
            }
        )
        
        # 获取该知识点的所有练习题
        exercises = Exercise.objects.filter(knowledge_point=knowledge_point)
        total_exercises = exercises.count()
        
        # 如果没有练习题，则无需更新
        if total_exercises == 0:
            return learning_record, False
        
        # 获取学生已回答的练习题
        answered_exercises = StudentAnswer.objects.filter(
            student=student,
            exercise__in=exercises
        ).values_list('exercise_id', flat=True)
        
        # 计算进度百分比
        completed_count = len(answered_exercises)
        progress_percentage = (completed_count / total_exercises) * 100 if total_exercises > 0 else 0
        
        # 检查是否需要更新状态
        status_changed = False
        old_status = learning_record.status
        
        # 计算新状态
        if progress_percentage >= 100:
            new_status = 'completed'
        elif progress_percentage > 0:
            new_status = 'in_progress'
        else:
            new_status = 'not_started'
            
        # 如果状态变更，更新记录
        if new_status != old_status:
            learning_record.status = new_status
            status_changed = True
        
        # 更新进度值
        learning_record.progress = progress_percentage
        learning_record.save(update_fields=['progress', 'status'])
        
        # 更新课程整体进度
        ProgressTrackerService.update_course_progress(student, knowledge_point.course)
        
        return learning_record, status_changed
    
    @staticmethod
    @transaction.atomic
    def update_course_progress(student, course):
        """
        更新学生在特定课程的整体进度
        
        Args:
            student: User模型实例
            course: Course模型实例
            
        Returns:
            更新后的CourseProgress对象
        """
        # 获取或创建课程进度记录
        course_progress, created = CourseProgress.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                'overall_progress': 0.0,
                'required_completed': False,
                'correctness_rate': 0.0,
                'total_time_spent': 0
            }
        )
        
        # 获取课程的所有知识点
        all_knowledge_points = KnowledgePoint.objects.filter(course=course)
        
        # 获取必修知识点
        required_knowledge_points = all_knowledge_points.filter(is_required=True)
        
        # 获取学生在该课程中的所有学习记录
        learning_records = LearningRecord.objects.filter(
            student=student,
            course=course
        )
        
        # 计算整体进度
        total_kps = all_knowledge_points.count()
        if total_kps > 0:
            # 计算平均进度
            avg_progress = learning_records.aggregate(Avg('progress'))['progress__avg'] or 0
            course_progress.overall_progress = avg_progress
        
        # 计算必修内容是否完成
        if required_knowledge_points.exists():
            # 获取已完成的必修知识点
            completed_required_records = learning_records.filter(
                knowledge_point__in=required_knowledge_points,
                status='completed'
            ).count()
            
            required_count = required_knowledge_points.count()
            course_progress.required_completed = completed_required_records == required_count
        else:
            course_progress.required_completed = True
        
        # 计算正确率
        student_answers = StudentAnswer.objects.filter(
            student=student,
            exercise__knowledge_point__course=course
        )
        
        if student_answers.exists():
            correct_answers = student_answers.filter(is_correct=True).count()
            total_answers = student_answers.count()
            course_progress.correctness_rate = (correct_answers / total_answers) * 100 if total_answers > 0 else 0
        
        # 计算总学习时间
        total_time = learning_records.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
        course_progress.total_time_spent = total_time
        
        # 检查是否完成课程
        old_is_completed = course_progress.is_completed
        
        # 课程完成条件：必修内容已完成且整体进度>=90%
        is_completed_now = course_progress.required_completed and course_progress.overall_progress >= 90
        
        if is_completed_now and not old_is_completed:
            # 首次完成，设置完成日期
            course_progress.is_completed = True
            course_progress.completion_date = timezone.now()
        elif not is_completed_now and old_is_completed:
            # 从已完成变为未完成，清除完成日期
            course_progress.is_completed = False
            course_progress.completion_date = None
        
        # 保存更新
        course_progress.save()
        
        return course_progress
    
    @staticmethod
    def get_student_progress(student, course=None):
        """
        获取学生进度概览
        
        Args:
            student: User模型实例
            course: 可选，Course模型实例，如果提供则只返回特定课程的进度
            
        Returns:
            包含学生进度数据的字典
        """
        # 基本查询过滤条件
        query_filter = {'student': student}
        
        # 如果指定了课程，则只返回该课程的进度
        if course:
            query_filter['course'] = course
            
        # 获取课程进度
        course_progress_list = CourseProgress.objects.filter(**query_filter)
        
        # 汇总数据
        result = {
            'courses': [],
            'total_courses': course_progress_list.count(),
            'completed_courses': course_progress_list.filter(is_completed=True).count(),
            'avg_correctness_rate': course_progress_list.aggregate(Avg('correctness_rate'))['correctness_rate__avg'] or 0,
            'total_time_spent': course_progress_list.aggregate(Sum('total_time_spent'))['total_time_spent__sum'] or 0
        }
        
        # 获取各课程详情
        for progress in course_progress_list:
            course_data = {
                'id': progress.course.id,
                'title': progress.course.title,
                'overall_progress': progress.overall_progress,
                'is_completed': progress.is_completed,
                'correctness_rate': progress.correctness_rate,
                'time_spent': progress.total_time_spent
            }
            result['courses'].append(course_data)
            
        return result 