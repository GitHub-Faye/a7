from django.test import TestCase
from django.utils import timezone
import json
from datetime import timedelta

from users.models import User
from .models import UsageStatistics, PerformanceMetric

class UsageStatisticsModelTest(TestCase):
    """使用统计模型的测试类"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建测试用例数据
        self.usage_stat = UsageStatistics.objects.create(
            user=self.user,
            module='course',
            action='view',
            details=json.dumps({'course_id': 1, 'time_spent': 120}),
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
    
    def test_usage_statistics_creation(self):
        """测试UsageStatistics模型实例创建"""
        self.assertEqual(self.usage_stat.user, self.user)
        self.assertEqual(self.usage_stat.module, 'course')
        self.assertEqual(self.usage_stat.action, 'view')
        self.assertEqual(self.usage_stat.ip_address, '127.0.0.1')
        self.assertIsNotNone(self.usage_stat.timestamp)
    
    def test_get_details_dict_method(self):
        """测试get_details_dict方法解析JSON数据"""
        details_dict = self.usage_stat.get_details_dict()
        self.assertIsInstance(details_dict, dict)
        self.assertEqual(details_dict['course_id'], 1)
        self.assertEqual(details_dict['time_spent'], 120)
    
    def test_get_details_dict_empty(self):
        """测试details为空时的get_details_dict方法"""
        self.usage_stat.details = None
        self.usage_stat.save()
        self.assertEqual(self.usage_stat.get_details_dict(), {})
    
    def test_get_details_dict_invalid_json(self):
        """测试details为无效JSON时的get_details_dict方法"""
        self.usage_stat.details = 'not a valid json'
        self.usage_stat.save()
        self.assertEqual(
            self.usage_stat.get_details_dict(), 
            {'error': 'Invalid JSON data'}
        )
    
    def test_str_representation(self):
        """测试UsageStatistics的字符串表示"""
        expected_str = f"{self.user.username} - course.view - {self.usage_stat.timestamp}"
        self.assertEqual(str(self.usage_stat), expected_str)
    
    def test_ordering(self):
        """测试UsageStatistics的排序（按时间戳倒序）"""
        # 设置第一个记录为较早的时间
        earlier_time = timezone.now() - timedelta(hours=1)
        self.usage_stat.timestamp = earlier_time
        self.usage_stat.save()
        
        # 创建第二个统计记录（时间较新）
        later_usage = UsageStatistics.objects.create(
            user=self.user,
            module='exercise',
            action='submit',
            ip_address='127.0.0.1'
        )
        
        # 确保较新的记录排在前面
        all_records = list(UsageStatistics.objects.all())
        self.assertEqual(all_records[0], later_usage)
        self.assertEqual(all_records[1], self.usage_stat)
    
    def test_usage_tracking_scenario(self):
        """测试在实际应用场景中跟踪用户活动"""
        # 模拟用户登录
        login_stat = UsageStatistics.objects.create(
            user=self.user,
            module='auth',
            action='login',
            details=json.dumps({
                'success': True, 
                'method': 'password',
                'ip': '192.168.1.1'
            })
        )
        
        # 模拟用户浏览课程列表
        browse_courses = UsageStatistics.objects.create(
            user=self.user,
            module='course',
            action='list',
            details=json.dumps({
                'filters': {'subject': '数学'},
                'page': 1,
                'items_per_page': 10
            })
        )
        
        # 模拟用户查看特定课程
        view_course = UsageStatistics.objects.create(
            user=self.user,
            module='course',
            action='view',
            details=json.dumps({
                'course_id': 42,
                'time_spent': 180,
                'sections_viewed': ['简介', '第一章']
            })
        )
        
        # 模拟用户完成练习
        complete_exercise = UsageStatistics.objects.create(
            user=self.user,
            module='exercise',
            action='submit',
            details=json.dumps({
                'exercise_id': 15,
                'course_id': 42,
                'correct': True,
                'time_spent': 120,
                'attempts': 2
            })
        )
        
        # 验证用户活动记录数量
        user_activities = UsageStatistics.objects.filter(user=self.user)
        # 1个初始记录 + 4个新记录
        self.assertEqual(user_activities.count(), 5)
        
        # 验证按模块过滤的记录
        course_activities = UsageStatistics.objects.filter(
            user=self.user,
            module='course'
        )
        self.assertEqual(course_activities.count(), 3)  # 1个初始记录 + 2个新记录
        
        # 验证按动作过滤的记录
        view_activities = UsageStatistics.objects.filter(
            user=self.user,
            action='view'
        )
        self.assertEqual(view_activities.count(), 2)  # 1个初始记录 + 1个新记录
        
        # 验证JSON数据查询
        # 注意：这里只是演示如何访问details字段中的数据
        # 实际上Django ORM不能直接查询JSON字段内部的数据（除非使用PostgreSQL with JSONField）
        # 我们这里手动过滤以验证逻辑
        exercise_activities = [
            activity for activity in user_activities
            if activity.module == 'exercise' and 
               activity.get_details_dict().get('exercise_id') == 15
        ]
        self.assertEqual(len(exercise_activities), 1)
        self.assertEqual(exercise_activities[0].action, 'submit')
        
        # 验证时间线顺序（应该按时间戳倒序排列）
        timeline = list(user_activities.order_by('-timestamp'))
        self.assertEqual(timeline[0], complete_exercise)
        self.assertEqual(timeline[1], view_course)
        self.assertEqual(timeline[2], browse_courses)
        self.assertEqual(timeline[3], login_stat)


class PerformanceMetricModelTest(TestCase):
    """性能指标模型的测试类"""
    
    def setUp(self):
        # 创建测试用例数据
        self.metric = PerformanceMetric.objects.create(
            metric_type='response_time',
            value=120.5,
            unit='ms',
            related_entity='api/courses',
            context=json.dumps({'server': 'app-server-1', 'load': 0.75})
        )
    
    def test_performance_metric_creation(self):
        """测试PerformanceMetric模型实例创建"""
        self.assertEqual(self.metric.metric_type, 'response_time')
        self.assertEqual(self.metric.value, 120.5)
        self.assertEqual(self.metric.unit, 'ms')
        self.assertEqual(self.metric.related_entity, 'api/courses')
        self.assertIsNotNone(self.metric.timestamp)
    
    def test_get_context_dict_method(self):
        """测试get_context_dict方法解析JSON数据"""
        context_dict = self.metric.get_context_dict()
        self.assertIsInstance(context_dict, dict)
        self.assertEqual(context_dict['server'], 'app-server-1')
        self.assertEqual(context_dict['load'], 0.75)
    
    def test_get_context_dict_empty(self):
        """测试context为空时的get_context_dict方法"""
        self.metric.context = None
        self.metric.save()
        self.assertEqual(self.metric.get_context_dict(), {})
    
    def test_get_context_dict_invalid_json(self):
        """测试context为无效JSON时的get_context_dict方法"""
        self.metric.context = 'not a valid json'
        self.metric.save()
        self.assertEqual(
            self.metric.get_context_dict(), 
            {'error': 'Invalid JSON data'}
        )
    
    def test_str_representation(self):
        """测试PerformanceMetric的字符串表示"""
        expected_str = f"{self.metric.metric_type} - {self.metric.value}{self.metric.unit} - {self.metric.timestamp}"
        self.assertEqual(str(self.metric), expected_str)
    
    def test_ordering(self):
        """测试PerformanceMetric的排序（按时间戳倒序）"""
        # 设置第一个指标为较早的时间
        earlier_time = timezone.now() - timedelta(hours=1)
        self.metric.timestamp = earlier_time
        self.metric.save()
        
        # 创建第二个性能指标（时间较新）
        later_metric = PerformanceMetric.objects.create(
            metric_type='cpu_usage',
            value=45.2,
            unit='%',
            related_entity='app-server-1'
        )
        
        # 确保较新的记录排在前面
        all_metrics = list(PerformanceMetric.objects.all())
        self.assertEqual(all_metrics[0], later_metric)
        self.assertEqual(all_metrics[1], self.metric)
    
    def test_performance_monitoring_scenario(self):
        """测试在实际应用场景中监控系统性能"""
        # 1. 模拟记录API响应时间
        api_metrics = []
        for i in range(5):
            # 模拟不同API端点的响应时间
            api_metric = PerformanceMetric.objects.create(
                metric_type='response_time',
                value=100 + (i * 20),  # 100, 120, 140, 160, 180 ms
                unit='ms',
                related_entity=f'api/endpoint{i}',
                context=json.dumps({
                    'server': 'web-server-1',
                    'db_queries': 5 + i,
                    'cache_hit': i % 2 == 0
                })
            )
            api_metrics.append(api_metric)
        
        # 2. 模拟记录服务器资源使用情况
        resource_metrics = []
        for server_id in range(1, 4):  # 3个服务器
            # CPU使用率
            cpu_metric = PerformanceMetric.objects.create(
                metric_type='cpu_usage',
                value=30 + (server_id * 10),  # 40%, 50%, 60%
                unit='%',
                related_entity=f'server-{server_id}',
                context=json.dumps({
                    'cores': 8,
                    'load_avg': [2.5, 2.8, 3.0]
                })
            )
            
            # 内存使用率
            memory_metric = PerformanceMetric.objects.create(
                metric_type='memory_usage',
                value=50 + (server_id * 5),  # 55%, 60%, 65%
                unit='%',
                related_entity=f'server-{server_id}',
                context=json.dumps({
                    'total_mb': 16384,
                    'used_mb': (50 + (server_id * 5)) * 16384 / 100
                })
            )
            
            resource_metrics.extend([cpu_metric, memory_metric])
        
        # 3. 模拟记录错误率
        error_metric = PerformanceMetric.objects.create(
            metric_type='error_rate',
            value=2.5,
            unit='%',
            related_entity='api/all',
            context=json.dumps({
                'total_requests': 1000,
                'error_count': 25,
                'status_codes': {
                    '200': 975,
                    '500': 20,
                    '404': 5
                }
            })
        )
        
        # 验证指标记录数量
        # 初始值 + 5个API + 6个资源 + 1个错误率 = 13
        self.assertEqual(PerformanceMetric.objects.count(), 13)
        
        # 验证按类型过滤的指标
        response_time_metrics = PerformanceMetric.objects.filter(metric_type='response_time')
        self.assertEqual(response_time_metrics.count(), 6)  # 初始值 + 5个新API
        
        cpu_metrics = PerformanceMetric.objects.filter(metric_type='cpu_usage')
        self.assertEqual(cpu_metrics.count(), 3)  # 3个服务器
        
        # 验证计算平均响应时间
        avg_response_time = response_time_metrics.exclude(
            related_entity='api/courses'  # 排除初始值
        ).values_list('value', flat=True)
        avg = sum(avg_response_time) / len(avg_response_time)
        expected_avg = (100 + 120 + 140 + 160 + 180) / 5  # 140ms
        self.assertEqual(avg, expected_avg)
        
        # 验证查找最高CPU使用率
        max_cpu = PerformanceMetric.objects.filter(
            metric_type='cpu_usage'
        ).order_by('-value').first()
        self.assertEqual(max_cpu.value, 60.0)
        self.assertEqual(max_cpu.related_entity, 'server-3')
        
        # 验证查找平均内存使用率
        memory_values = PerformanceMetric.objects.filter(
            metric_type='memory_usage'
        ).values_list('value', flat=True)
        avg_memory = sum(memory_values) / len(memory_values)
        expected_memory_avg = (55 + 60 + 65) / 3  # 60%
        self.assertEqual(avg_memory, expected_memory_avg) 