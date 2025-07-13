from django.db import models
from users.models import User
from django.db.models import Avg, Sum
from django.utils import timezone

class Course(models.Model):
    """
    课程模型，表示教育系统中的一个课程
    """
    title = models.CharField(max_length=100, verbose_name='课程标题')
    description = models.TextField(blank=True, verbose_name='课程描述')
    subject = models.CharField(max_length=50, verbose_name='学科')
    grade_level = models.CharField(max_length=20, verbose_name='年级水平')
    teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # 修改为SET_NULL，避免删除教师时连带删除课程
        null=True,  # 允许为空，配合SET_NULL使用
        related_name='courses',
        verbose_name='教师'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'grade_level'], name='course_subj_grade_idx'),
            models.Index(fields=['teacher', 'created_at'], name='course_teacher_date_idx')
        ]
    
    def __str__(self):
        return self.title


class KnowledgePoint(models.Model):
    """
    知识点模型，表示课程中的知识点，可以有层次结构
    """
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,  # 保持CASCADE，删除课程时连带删除知识点
        related_name='knowledge_points',
        verbose_name='所属课程'
    )
    title = models.CharField(max_length=100, verbose_name='知识点标题')
    content = models.TextField(blank=True, verbose_name='知识点内容')
    importance = models.IntegerField(
        default=5, 
        choices=[(i, str(i)) for i in range(1, 11)],
        verbose_name='重要性(1-10)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,  # 修改为SET_NULL，删除父知识点不应影响子知识点
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父知识点'
    )
    is_required = models.BooleanField(default=True, verbose_name='是否必修')
    estimated_time = models.PositiveIntegerField(default=30, verbose_name='预计学习时间(分钟)')
    
    class Meta:
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        ordering = ['importance', 'title']
        indexes = [
            models.Index(fields=['course', 'importance'], name='kp_course_imp_idx'),
            models.Index(fields=['parent'], name='kp_parent_idx'),
            models.Index(fields=['is_required'], name='kp_required_idx'),
        ]
    
    def __str__(self):
        return self.title


class Courseware(models.Model):
    """
    课件模型，表示课程相关的教学资料
    """
    COURSEWARE_TYPES = (
        ('document', '文档'),
        ('video', '视频'),
        ('audio', '音频'),
        ('image', '图片'),
        ('interactive', '交互式内容'),
        ('other', '其他'),
    )
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,  # 保持CASCADE，删除课程时连带删除课件
        related_name='coursewares',
        verbose_name='所属课程'
    )
    title = models.CharField(max_length=100, verbose_name='课件标题')
    content = models.TextField(verbose_name='课件内容')
    type = models.CharField(
        max_length=20, 
        choices=COURSEWARE_TYPES, 
        default='document',
        verbose_name='课件类型'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # 修改为SET_NULL，避免删除用户时连带删除课件
        null=True,  # 允许为空，配合SET_NULL使用
        related_name='created_coursewares',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '课件'
        verbose_name_plural = '课件'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course', 'type'], name='cw_course_type_idx'),
            models.Index(fields=['created_by', 'created_at'], name='cw_creator_date_idx')
        ]
    
    def __str__(self):
        return self.title

class Exercise(models.Model):
    """
    练习模型，表示与知识点相关的练习题
    """
    EXERCISE_TYPES = (
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
        ('coding', '编程题'),
        ('other', '其他'),
    )
    
    DIFFICULTY_LEVELS = (
        (1, '简单'),
        (2, '较简单'),
        (3, '中等'),
        (4, '较难'),
        (5, '困难'),
    )
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='题目内容')
    type = models.CharField(
        max_length=20, 
        choices=EXERCISE_TYPES, 
        default='single_choice',
        verbose_name='题目类型'
    )
    difficulty = models.IntegerField(
        choices=DIFFICULTY_LEVELS,
        default=3,
        verbose_name='难度等级'
    )
    knowledge_point = models.ForeignKey(
        KnowledgePoint,
        on_delete=models.CASCADE,  # 保持CASCADE，删除知识点时连带删除练习题
        related_name='exercises',
        verbose_name='关联知识点'
    )
    answer_template = models.TextField(
        blank=True,
        null=True,
        verbose_name='答案模板'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_required = models.BooleanField(default=True, verbose_name='是否必做题')
    correct_count = models.PositiveIntegerField(default=0, verbose_name='正确次数')
    attempt_count = models.PositiveIntegerField(default=0, verbose_name='尝试次数')
    
    class Meta:
        verbose_name = '练习题'
        verbose_name_plural = '练习题'
        ordering = ['knowledge_point', 'difficulty', '-created_at']
        indexes = [
            models.Index(fields=['knowledge_point', 'difficulty'], name='ex_kp_diff_idx'),
            models.Index(fields=['type'], name='ex_type_idx'),
            models.Index(fields=['is_required'], name='ex_required_idx'),
        ]
    
    def __str__(self):
        return self.title
        
    def update_statistics(self, is_correct):
        """更新练习题的统计信息"""
        self.attempt_count += 1
        if is_correct:
            self.correct_count += 1
        self.save(update_fields=['attempt_count', 'correct_count'])
        
    @property
    def correctness_rate(self):
        """计算练习题的正确率"""
        if self.attempt_count == 0:
            return 0.0
        return (self.correct_count / self.attempt_count) * 100

class StudentAnswer(models.Model):
    """
    学生答案模型，记录学生对练习题的回答
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # 保持CASCADE，删除学生时删除其所有答案
        related_name='answers',
        verbose_name='学生'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,  # 保持CASCADE，删除练习题时删除相关答案
        related_name='student_answers',
        verbose_name='练习题'
    )
    content = models.TextField(verbose_name='答案内容')
    score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='得分'
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name='反馈'
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    is_correct = models.BooleanField(null=True, blank=True, verbose_name='是否正确')
    attempt_count = models.PositiveIntegerField(default=1, verbose_name='尝试次数')
    
    class Meta:
        verbose_name = '学生答案'
        verbose_name_plural = '学生答案'
        ordering = ['-submitted_at']
        unique_together = ['student', 'exercise']  # 保持约束，每个学生对每道题只能有一个答案
        indexes = [
            models.Index(fields=['student', 'submitted_at'], name='ans_stud_date_idx'),
            models.Index(fields=['exercise', 'score'], name='ans_ex_score_idx'),
            models.Index(fields=['is_correct'], name='ans_correct_idx'),
            models.Index(fields=['student', 'is_correct'], name='ans_stud_correct_idx'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.exercise.title}"
        
    def save(self, *args, **kwargs):
        """重写save方法，以便在保存答案时更新练习题统计信息"""
        is_new = not self.pk  # 判断是否为新记录
        old_is_correct = None
        
        # 如果不是新记录，获取旧的is_correct值
        if not is_new:
            old_instance = StudentAnswer.objects.get(pk=self.pk)
            old_is_correct = old_instance.is_correct
            
        # 调用原始save方法保存记录
        super().save(*args, **kwargs)
        
        # 只有当is_correct有变化或是新记录时更新练习题统计
        if is_new:
            # 新记录，增加尝试次数和正确计数（如果正确）
            self.exercise.update_statistics(self.is_correct)
        elif self.is_correct is not None and self.is_correct != old_is_correct:
            # 已有记录的正确性发生变化，只更新正确计数
            if self.is_correct:
                self.exercise.correct_count += 1
            else:
                self.exercise.correct_count -= 1
            self.exercise.save(update_fields=['correct_count'])

class LearningRecord(models.Model):
    """
    学习记录模型，跟踪学生在特定课程和知识点上的学习进度
    """
    STATUS_CHOICES = (
        ('not_started', '未开始'),
        ('in_progress', '学习中'),
        ('completed', '已完成'),
        ('review_needed', '需要复习'),
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # 保持CASCADE，删除学生时删除其所有学习记录
        related_name='learning_records',
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,  # 保持CASCADE，删除课程时删除相关学习记录
        related_name='learning_records',
        verbose_name='课程'
    )
    knowledge_point = models.ForeignKey(
        KnowledgePoint,
        on_delete=models.CASCADE,  # 保持CASCADE，删除知识点时删除相关学习记录
        related_name='learning_records',
        verbose_name='知识点'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name='状态'
    )
    progress = models.FloatField(
        default=0.0,
        verbose_name='进度百分比',
        help_text='0-100的数值，表示完成百分比'
    )
    time_spent = models.PositiveIntegerField(
        default=0,
        verbose_name='学习时间(分钟)'
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        verbose_name='最后访问时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '学习记录'
        verbose_name_plural = '学习记录'
        ordering = ['-last_accessed']
        unique_together = ['student', 'knowledge_point']  # 保持约束，每个学生对每个知识点只有一条记录
        indexes = [
            models.Index(fields=['student', 'course'], name='lr_stud_course_idx'),
            models.Index(fields=['status'], name='lr_status_idx'),
            models.Index(fields=['last_accessed'], name='lr_access_idx'),
            models.Index(fields=['progress'], name='lr_progress_idx')
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.knowledge_point.title} ({self.get_status_display()})"
    
    @property
    def is_complete(self):
        """判断是否已完成学习"""
        return self.status == 'completed'
    
    def update_progress(self, progress_value):
        """更新学习进度"""
        if 0 <= progress_value <= 100:
            self.progress = progress_value
            if progress_value >= 100:
                self.status = 'completed'
            elif progress_value > 0:
                self.status = 'in_progress'
            self.save()
            
            # 更新关联的课程进度
            self._update_course_progress()
            return True
        return False
    
    def add_time_spent(self, minutes):
        """添加学习时间（分钟）"""
        if minutes > 0:
            self.time_spent += minutes
            self.save()
            
            # 更新关联的课程进度
            self._update_course_progress()
            return True
        return False
        
    def _update_course_progress(self):
        """更新关联的课程进度"""
        # 获取或创建CourseProgress实例
        course_progress, created = CourseProgress.objects.get_or_create(
            student=self.student,
            course=self.course
        )
        # 更新课程进度
        course_progress.update_from_learning_records()

class CourseProgress(models.Model):
    """
    课程进度模型，跟踪学生在整个课程上的综合进度
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_progress',
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='student_progress',
        verbose_name='课程'
    )
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    overall_progress = models.FloatField(default=0.0, verbose_name='整体进度百分比')
    required_completed = models.BooleanField(default=False, verbose_name='必修内容是否完成')
    correctness_rate = models.FloatField(default=0.0, verbose_name='练习题正确率')
    total_time_spent = models.PositiveIntegerField(default=0, verbose_name='总学习时间(分钟)')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='最近活动时间')
    
    class Meta:
        verbose_name = '课程进度'
        verbose_name_plural = '课程进度'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'course'], name='cp_stud_course_idx'),
            models.Index(fields=['is_completed'], name='cp_completed_idx'),
            models.Index(fields=['overall_progress'], name='cp_progress_idx'),
        ]
        
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.overall_progress:.1f}%)"
    
    def update_from_learning_records(self):
        """根据学习记录更新课程整体进度"""
        # 获取该课程下所有知识点
        all_kp = self.course.knowledge_points.all()
        required_kp = all_kp.filter(is_required=True)
        
        # 没有知识点时直接返回
        if not all_kp.exists():
            return
        
        # 获取该学生在该课程下的所有学习记录
        learning_records = LearningRecord.objects.filter(
            student=self.student,
            course=self.course
        )
        
        # 计算总进度
        total_progress = 0
        if learning_records.exists():
            total_progress = learning_records.aggregate(Avg('progress'))['progress__avg'] or 0
        
        # 计算是否完成所有必修知识点
        if required_kp.exists():
            completed_required = learning_records.filter(
                knowledge_point__in=required_kp,
                status='completed'
            ).count()
            self.required_completed = (completed_required == required_kp.count())
        else:
            self.required_completed = True
        
        # 计算总学习时间
        total_time = learning_records.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
        
        # 计算练习题正确率
        student_answers = StudentAnswer.objects.filter(
            student=self.student,
            exercise__knowledge_point__course=self.course,
            is_correct__isnull=False
        )
        
        if student_answers.exists():
            correct_count = student_answers.filter(is_correct=True).count()
            self.correctness_rate = (correct_count / student_answers.count()) * 100
        else:
            self.correctness_rate = 0
        
        # 更新字段
        self.overall_progress = total_progress
        self.total_time_spent = total_time
        
        # 检查是否完成课程
        all_completed = False
        if required_kp.exists():
            all_completed = learning_records.filter(
                knowledge_point__in=required_kp,
                status='completed'
            ).count() == required_kp.count()
        else:
            all_completed = total_progress >= 100
        
        if all_completed and not self.is_completed:
            self.is_completed = True
            self.completion_date = timezone.now()
        
        self.save()
