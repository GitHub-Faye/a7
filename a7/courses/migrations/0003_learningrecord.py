# Generated by Django 4.2.21 on 2025-05-22 07:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0002_exercise_studentanswer'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', '未开始'), ('in_progress', '学习中'), ('completed', '已完成'), ('review_needed', '需要复习')], default='not_started', max_length=20, verbose_name='状态')),
                ('progress', models.FloatField(default=0.0, help_text='0-100的数值，表示完成百分比', verbose_name='进度百分比')),
                ('time_spent', models.PositiveIntegerField(default=0, verbose_name='学习时间(分钟)')),
                ('last_accessed', models.DateTimeField(auto_now=True, verbose_name='最后访问时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_records', to='courses.course', verbose_name='课程')),
                ('knowledge_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_records', to='courses.knowledgepoint', verbose_name='知识点')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_records', to=settings.AUTH_USER_MODEL, verbose_name='学生')),
            ],
            options={
                'verbose_name': '学习记录',
                'verbose_name_plural': '学习记录',
                'ordering': ['-last_accessed'],
                'indexes': [models.Index(fields=['student', 'course'], name='courses_lea_student_a74868_idx'), models.Index(fields=['status'], name='courses_lea_status_2e9e5d_idx'), models.Index(fields=['last_accessed'], name='courses_lea_last_ac_f8e3c2_idx')],
                'unique_together': {('student', 'knowledge_point')},
            },
        ),
    ]
