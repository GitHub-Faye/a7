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
        on_delete=models.CASCADE, 
        related_name='courses',
        verbose_name='教师'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class KnowledgePoint(models.Model):
    """
    知识点模型，表示课程中的知识点，可以有层次结构
    """
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
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
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='父知识点'
    )
    
    class Meta:
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        ordering = ['importance', 'title']
    
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
        on_delete=models.CASCADE, 
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
        on_delete=models.CASCADE, 
        related_name='created_coursewares',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '课件'
        verbose_name_plural = '课件'
        ordering = ['-created_at']
    
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
        on_delete=models.CASCADE,
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
    
    def __str__(self):
        return self.title

class StudentAnswer(models.Model):
    """
    学生答案模型，记录学生对练习题的回答
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='学生'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
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
        unique_together = ['student', 'exercise']  # 每个学生对每道题只能有一个答案
    
    def __str__(self):
        return f"{self.student.username} - {self.exercise.title}"
