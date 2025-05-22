from django.db import models
from users.models import User

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
        on_delete=models.CASCADE,  # 保持CASCADE，删除父知识点时连带删除子知识点
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='父知识点'
    )
    
    class Meta:
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        ordering = ['importance', 'title']
        indexes = [
            models.Index(fields=['course', 'importance'], name='kp_course_imp_idx'),
            models.Index(fields=['parent'], name='kp_parent_idx')
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
    
    class Meta:
        verbose_name = '练习题'
        verbose_name_plural = '练习题'
        ordering = ['knowledge_point', 'difficulty', '-created_at']
        indexes = [
            models.Index(fields=['knowledge_point', 'difficulty'], name='ex_kp_diff_idx'),
            models.Index(fields=['type'], name='ex_type_idx')
        ]
    
    def __str__(self):
        return self.title

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
    
    class Meta:
        verbose_name = '学生答案'
        verbose_name_plural = '学生答案'
        ordering = ['-submitted_at']
        unique_together = ['student', 'exercise']  # 保持约束，每个学生对每道题只能有一个答案
        indexes = [
            models.Index(fields=['student', 'submitted_at'], name='ans_stud_date_idx'),
            models.Index(fields=['exercise', 'score'], name='ans_ex_score_idx')
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.exercise.title}"

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
            return True
        return False
    
    def add_time_spent(self, minutes):
        """添加学习时间（分钟）"""
        if minutes > 0:
            self.time_spent += minutes
            self.save()
            return True
        return False
