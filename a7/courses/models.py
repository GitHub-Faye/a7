from django.db import models
from users.models import User
from django.db.models import Avg, Sum
from django.utils import timezone
from .storage import CoursewareFileStorage
from .utils import courseware_file_path, validate_file_type, validate_file_size

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
    # 新增字段，标识是否有关联文件
    has_files = models.BooleanField(default=False, verbose_name='包含文件')
    
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

    def update_has_files(self):
        """更新has_files字段状态"""
        has_files = self.files.exists()
        if self.has_files != has_files:
            self.has_files = has_files
            self.save(update_fields=['has_files'])

class CoursewareFile(models.Model):
    """
    课件文件模型，存储与课件相关的文件元数据
    """
    courseware = models.ForeignKey(
        Courseware, 
        on_delete=models.CASCADE, 
        related_name='files',
        verbose_name='所属课件'
    )
    file = models.FileField(
        upload_to=courseware_file_path,  # 使用自定义路径生成函数
        storage=CoursewareFileStorage(),  # 使用自定义存储类
        verbose_name='文件'
    )
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    file_size = models.PositiveIntegerField(verbose_name='文件大小(字节)')
    file_type = models.CharField(max_length=100, verbose_name='文件类型')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        verbose_name = '课件文件'
        verbose_name_plural = '课件文件'
        ordering = ['-upload_time']
        indexes = [
            models.Index(fields=['courseware', 'file_type'], name='cwfile_cw_type_idx'),
            models.Index(fields=['upload_time'], name='cwfile_upload_time_idx')
        ]
    
    def __str__(self):
        return self.file_name
        
    def save(self, *args, **kwargs):
        # 如果是新创建的记录，自动设置file_name, file_size和file_type
        if not self.pk:
            self.file_name = self.file.name.split('/')[-1]
            self.file_size = self.file.size
            
            # 直接从kwargs中获取content_type
            if hasattr(self.file, 'content_type') and self.file.content_type:
                self.file_type = self.file.content_type
            # 尝试从_file对象获取content_type属性
            elif hasattr(self.file, '_file') and hasattr(self.file._file, 'content_type'):
                self.file_type = self.file._file.content_type
            # 根据文件扩展名判断类型
            else:
                ext = self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''
                content_type_map = {
                    'pdf': 'application/pdf',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'ppt': 'application/vnd.ms-powerpoint',
                    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'txt': 'text/plain',
                    'csv': 'text/csv',
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'gif': 'image/gif',
                }
                self.file_type = content_type_map.get(ext, '')
                
        super().save(*args, **kwargs)
        
        # 确保更新关联课件的has_files状态
        self.courseware.update_has_files()
        
    def get_file_url(self):
        """获取文件的URL"""
        return self.file.url
        
    def validate_file(self, allowed_types=None, max_size_mb=10):
        """验证文件类型和大小"""
        if not validate_file_type(self.file, allowed_types):
            return False, "不支持的文件类型"
        
        if not validate_file_size(self.file, max_size_mb):
            return False, f"文件大小超过限制（最大{max_size_mb}MB）"
            
        return True, "文件验证通过"

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
    
    def __init__(self, *args, **kwargs):
        """初始化方法，记录原始is_correct值以便在save中检测变化"""
        self._old_is_correct = None
        super().__init__(*args, **kwargs)
        if self.pk:
            self._old_is_correct = self.is_correct
    
    def save(self, *args, **kwargs):
        """
        重写保存方法，更新练习题统计信息
        1. 新创建的正确答案：增加练习题正确次数
        2. 现有答案从错误变为正确：增加练习题正确次数
        3. 现有答案从正确变为错误：减少练习题正确次数
        """
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        # 处理is_correct变化
        if self.is_correct is not None:  # 只有明确标记了是否正确的答案才会影响统计
            if is_new:  # 新创建的答案
                if self.is_correct:
                    self.exercise.correct_count += 1
                self.exercise.attempt_count += 1
                self.exercise.save(update_fields=['correct_count', 'attempt_count'])
            elif self._old_is_correct is not None and self._old_is_correct != self.is_correct:
                # 现有答案的正确性发生变化
                if self.is_correct:  # 从错误变为正确
                    self.exercise.correct_count += 1
                else:  # 从正确变为错误
                    self.exercise.correct_count -= 1
                self.exercise.save(update_fields=['correct_count'])
        
        # 更新原始值以便下次比较
        self._old_is_correct = self.is_correct

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
            models.Index(fields=['student', 'status'], name='lr_stud_status_idx'),
            models.Index(fields=['knowledge_point', 'status'], name='lr_kp_status_idx'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.knowledge_point.title}"
    
    @property
    def is_complete(self):
        """判断是否完成学习"""
        return self.status == 'completed'
    
    def update_progress(self, progress_value):
        """更新学习进度"""
        # 确保进度值在0-100之间
        progress_value = max(0, min(100, progress_value))
        
        # 更新进度值
        self.progress = progress_value
        
        # 根据进度值自动更新状态
        if progress_value >= 100:
            self.status = 'completed'
        elif progress_value > 0:
            self.status = 'in_progress'
        else:
            self.status = 'not_started'
            
        self.save()
        
        # 更新课程整体进度
        self._update_course_progress()
    
    def add_time_spent(self, minutes):
        """增加学习时间（分钟）"""
        # 确保时间为正值
        if minutes > 0:
            self.time_spent += minutes
            self.save(update_fields=['time_spent'])
            
            # 更新课程整体进度
            self._update_course_progress()
    
    def _update_course_progress(self):
        """更新课程整体进度（内部方法）"""
        CourseProgress.objects.get_or_create(
            student=self.student,
            course=self.course
        )[0].update_from_learning_records()

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
    exercise_attempt_count = models.PositiveIntegerField(default=0, verbose_name='练习尝试次数')
    exercise_correct_count = models.PositiveIntegerField(default=0, verbose_name='练习正确次数')
    
    class Meta:
        verbose_name = '课程进度'
        verbose_name_plural = '课程进度'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'is_completed'], name='cp_stud_comp_idx'),
            models.Index(fields=['course', 'is_completed'], name='cp_course_comp_idx'),
            models.Index(fields=['overall_progress'], name='cp_progress_idx'),
            models.Index(fields=['required_completed'], name='cp_req_comp_idx'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.overall_progress:.1f}%"
    
    def update_from_learning_records(self):
        """从学习记录更新课程整体进度"""
        # 获取该学生在该课程所有知识点的学习记录
        records = LearningRecord.objects.filter(
            student=self.student,
            course=self.course
        )
        
        # 获取该课程的所有知识点
        all_kps = self.course.knowledge_points.all()
        total_kps = all_kps.count()
        
        if total_kps > 0:
            # 计算整体进度
            completed_kps = records.filter(status='completed').count()
            self.overall_progress = (completed_kps / total_kps) * 100
            
            # 计算必修内容是否完成
            required_kps = all_kps.filter(is_required=True)
            total_required = required_kps.count()
            
            if total_required > 0:
                completed_required = records.filter(
                    status='completed',
                    knowledge_point__is_required=True
                ).count()
                
                self.required_completed = (completed_required == total_required)
            else:
                self.required_completed = True
            
            # 更新完成状态
            was_completed = self.is_completed
            self.is_completed = self.required_completed and self.overall_progress >= 100
            
            # 如果从未完成变为完成，记录完成时间
            if self.is_completed and not was_completed:
                self.completion_date = timezone.now()
            # 如果从完成变为未完成，清除完成时间
            elif not self.is_completed and was_completed:
                self.completion_date = None
            
            # 计算总学习时间
            self.total_time_spent = records.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
            
            # 计算练习题正确率
            student_answers = StudentAnswer.objects.filter(
                student=self.student,
                exercise__knowledge_point__course=self.course
            )
            
            self.exercise_attempt_count = student_answers.count()
            self.exercise_correct_count = student_answers.filter(is_correct=True).count()
            
            if self.exercise_attempt_count > 0:
                self.correctness_rate = (self.exercise_correct_count / self.exercise_attempt_count) * 100
            else:
                self.correctness_rate = 0.0
            
            self.save()
