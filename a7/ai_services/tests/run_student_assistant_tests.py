#!/usr/bin/env python
"""
学生助手模块手动测试脚本

这个脚本允许在命令行环境中手动触发和执行学生助手模块的集成测试。
使用方法：
    python run_student_assistant_tests.py --test [测试类型]
    
测试类型选项:
    all - 执行所有测试
    dialogue - 仅测试对话API
    exercise - 仅测试练习生成API
    answer - 仅测试答案校正API
    integration - 仅测试完整流程集成
    scenario - 仅测试端到端场景
"""

import os
import sys
import argparse
import json
import uuid
import time
import django
from pathlib import Path

# 设置Django环境
# 调整BASE_DIR以确保指向正确的项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a7.settings")
django.setup()

# 导入Django测试客户端和其他必要模块
from rest_framework.test import APIClient
from django.urls import reverse
from django.db import connection
from django.test.utils import setup_databases, teardown_databases

# 导入模型
from courses.models import Course, KnowledgePoint, Exercise
from users.models import User

# 导入AI服务客户端
from ai_services.services.n8n_webhook.client import N8nWebhookClient


class TestRunner:
    """测试运行器类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.client = APIClient()
        self.dialogue_url = reverse('student-dialogue-list')
        self.exercise_url = reverse('ai_services:generate-exercises-list')
        self.correction_url = reverse('ai_services:correct-answer-list')
        self.n8n_client = None
        
        # 测试数据
        self.session_id = str(uuid.uuid4())
        self.course = None
        self.knowledge_point = None
        self.exercise = None
        
        # 测试状态跟踪
        self.test_results = {
            "dialogue": {"passed": 0, "failed": 0, "total": 0},
            "exercise": {"passed": 0, "failed": 0, "total": 0},
            "answer": {"passed": 0, "failed": 0, "total": 0},
            "integration": {"passed": 0, "failed": 0, "total": 0},
            "scenario": {"passed": 0, "failed": 0, "total": 0},
        }
    
    def setup_test_data(self):
        """设置测试数据"""
        print("设置测试数据...")
        
        # 创建测试用户
        try:
            self.teacher = User.objects.get(username='test_teacher')
            print("  使用已存在的测试教师账号")
        except User.DoesNotExist:
            self.teacher = User.objects.create_user(
                username='test_teacher',
                password='testpassword123',
                email='test@example.com'
            )
            print("  创建测试教师账号")
        
        # 创建测试课程
        self.course = Course.objects.create(
            title="测试物理课程", 
            description="用于测试的物理学课程",
            subject="物理",
            grade_level="高中",
            teacher=self.teacher
        )
        print(f"  创建测试课程: {self.course.title}")
        
        # 创建测试知识点
        self.knowledge_point = KnowledgePoint.objects.create(
            course=self.course,
            title="牛顿运动定律",
            content="牛顿运动定律是经典力学的基础，包括三个定律...",
            importance=5
        )
        print(f"  创建测试知识点: {self.knowledge_point.title}")
        
        # 创建测试练习题
        self.exercise = Exercise.objects.create(
            title="牛顿第二定律应用题",
            content="一个5kg的物体在10N力的作用下，其加速度是多少?",
            type="short_answer",
            difficulty=3,
            knowledge_point=self.knowledge_point,
            answer_template="2 m/s^2"
        )
        print(f"  创建测试练习题: {self.exercise.title}")
        
        # 初始化AI服务客户端
        try:
            self.n8n_client = N8nWebhookClient()
            print("  AI服务客户端初始化成功")
        except Exception as e:
            print(f"  AI服务客户端初始化失败: {str(e)}")
            print("  测试将使用API端点，而不是直接调用客户端")
        
        print("测试数据设置完成！\n")
    
    def test_dialogue_flow(self):
        """测试对话API流程"""
        print("\n=== 开始测试对话API ===")
        
        # 步骤1: 发起初始对话
        print("\n1. 发送初始对话请求...")
        dialogue_data = {
            'query': '请解释牛顿第二定律',
            'session_id': self.session_id
        }
        
        try:
            response = self.client.post(
                self.dialogue_url,
                data=json.dumps(dialogue_data),
                content_type='application/json'
            )
            self._print_response(response)
            
            if response.status_code == 200 and response.data['success']:
                self._record_test_result("dialogue", True)
                print("✅ 初始对话测试通过")
            else:
                self._record_test_result("dialogue", False)
                print("❌ 初始对话测试失败")
                return
        except Exception as e:
            self._record_test_result("dialogue", False)
            print(f"❌ 初始对话测试出错: {str(e)}")
            return
        
        # 步骤2: 发起后续对话
        print("\n2. 发送后续对话请求...")
        follow_up_data = {
            'query': '你能进一步解释牛顿第一定律吗？',
            'session_id': self.session_id
        }
        
        try:
            response = self.client.post(
                self.dialogue_url,
                data=json.dumps(follow_up_data),
                content_type='application/json'
            )
            self._print_response(response)
            
            if response.status_code == 200 and response.data['success']:
                self._record_test_result("dialogue", True)
                print("✅ 后续对话测试通过")
            else:
                self._record_test_result("dialogue", False)
                print("❌ 后续对话测试失败")
        except Exception as e:
            self._record_test_result("dialogue", False)
            print(f"❌ 后续对话测试出错: {str(e)}")
        
        print("\n=== 对话API测试完成 ===")
    
    def test_exercise_generation(self):
        """测试练习题生成API"""
        print("\n=== 开始测试练习题生成API ===")
        
        # 步骤1: 生成练习题请求
        print("\n1. 发送练习题生成请求...")
        exercise_data = {
            'query': '牛顿第二定律练习题',
            'knowledge_point_ids': [self.knowledge_point.id],
            'quantity': 1,
            'session_id': self.session_id
        }
        
        try:
            response = self.client.post(
                self.exercise_url,
                data=json.dumps(exercise_data),
                content_type='application/json'
            )
            self._print_response(response)
            
            if response.status_code == 200 and response.data['success']:
                self._record_test_result("exercise", True)
                print("✅ 练习题生成测试通过")
                
                # 保存生成的练习题信息以供后续测试使用
                self.generated_exercises = response.data['data'].get('exercises', [])
                if self.generated_exercises:
                    print(f"\n生成了 {len(self.generated_exercises)} 道练习题")
                    for idx, ex in enumerate(self.generated_exercises, 1):
                        print(f"  题目 {idx}: {ex['title']}")
                        print(f"  内容: {ex['content']}")
                        print(f"  类型: {ex['type']}")
                        print(f"  难度: {ex['difficulty']}")
                        print("")
            else:
                self._record_test_result("exercise", False)
                print("❌ 练习题生成测试失败")
        except Exception as e:
            self._record_test_result("exercise", False)
            print(f"❌ 练习题生成测试出错: {str(e)}")
        
        print("\n=== 练习题生成API测试完成 ===")
    
    def test_answer_correction(self):
        """测试答案校正API"""
        print("\n=== 开始测试答案校正API ===")
        
        # 步骤1: 提交答案校正请求
        print("\n1. 发送答案校正请求...")
        correction_data = {
            'exercise_id': self.exercise.id,
            'student_answer': '2 m/s^2',
            'session_id': self.session_id
        }
        
        try:
            response = self.client.post(
                self.correction_url,
                data=json.dumps(correction_data),
                content_type='application/json'
            )
            self._print_response(response)
            
            if response.status_code == 200 and response.data['success']:
                self._record_test_result("answer", True)
                print("✅ 答案校正测试通过")
                
                # 显示答案评估结果
                print("\n答案评估结果:")
                print(f"  正确性: {'正确' if response.data['data']['is_correct'] else '错误'}")
                print(f"  得分: {response.data['data']['score']}")
                print(f"  反馈: {response.data['data']['feedback']}")
                print(f"  改进建议: {response.data['data']['improvement_suggestions']}")
                print(f"  解析: {response.data['data']['explanation']}")
            else:
                self._record_test_result("answer", False)
                print("❌ 答案校正测试失败")
        except Exception as e:
            self._record_test_result("answer", False)
            print(f"❌ 答案校正测试出错: {str(e)}")
        
        print("\n=== 答案校正API测试完成 ===")
    
    def test_integration_workflow(self):
        """测试完整流程集成"""
        print("\n=== 开始测试完整集成流程 ===")
        
        # 为集成测试创建新会话ID
        integration_session_id = str(uuid.uuid4())
        print(f"使用会话ID: {integration_session_id}\n")
        
        # 步骤1: 发起对话
        print("1. 发起初始对话...")
        dialogue_data = {
            'query': '请解释牛顿第二定律并给我一个例子',
            'session_id': integration_session_id
        }
        
        try:
            dialogue_response = self.client.post(
                self.dialogue_url,
                data=json.dumps(dialogue_data),
                content_type='application/json'
            )
            self._print_response(dialogue_response)
            
            if dialogue_response.status_code != 200 or not dialogue_response.data['success']:
                self._record_test_result("integration", False)
                print("❌ 集成测试步骤1失败")
                return
            print("✅ 步骤1完成")
        except Exception as e:
            self._record_test_result("integration", False)
            print(f"❌ 步骤1出错: {str(e)}")
            return
        
        # 步骤2: 生成练习题
        print("\n2. 生成练习题...")
        exercise_data = {
            'query': '生成关于牛顿第二定律的练习题',
            'knowledge_point_ids': [self.knowledge_point.id],
            'session_id': integration_session_id
        }
        
        try:
            exercise_response = self.client.post(
                self.exercise_url,
                data=json.dumps(exercise_data),
                content_type='application/json'
            )
            self._print_response(exercise_response)
            
            if exercise_response.status_code != 200 or not exercise_response.data['success']:
                self._record_test_result("integration", False)
                print("❌ 集成测试步骤2失败")
                return
            print("✅ 步骤2完成")
        except Exception as e:
            self._record_test_result("integration", False)
            print(f"❌ 步骤2出错: {str(e)}")
            return
        
        # 步骤3: 提交答案并获取校正
        print("\n3. 提交答案并获取校正...")
        correction_data = {
            'exercise_id': self.exercise.id,
            'student_answer': '2 m/s^2',
            'session_id': integration_session_id
        }
        
        try:
            correction_response = self.client.post(
                self.correction_url,
                data=json.dumps(correction_data),
                content_type='application/json'
            )
            self._print_response(correction_response)
            
            if correction_response.status_code != 200 or not correction_response.data['success']:
                self._record_test_result("integration", False)
                print("❌ 集成测试步骤3失败")
                return
            print("✅ 步骤3完成")
        except Exception as e:
            self._record_test_result("integration", False)
            print(f"❌ 步骤3出错: {str(e)}")
            return
        
        # 步骤4: 继续对话，讨论答案
        print("\n4. 继续对话讨论答案...")
        follow_up_data = {
            'query': '我的答案正确吗？能解释一下答案是怎么计算的？',
            'session_id': integration_session_id
        }
        
        try:
            follow_up_response = self.client.post(
                self.dialogue_url,
                data=json.dumps(follow_up_data),
                content_type='application/json'
            )
            self._print_response(follow_up_response)
            
            if follow_up_response.status_code != 200 or not follow_up_response.data['success']:
                self._record_test_result("integration", False)
                print("❌ 集成测试步骤4失败")
                return
            print("✅ 步骤4完成")
        except Exception as e:
            self._record_test_result("integration", False)
            print(f"❌ 步骤4出错: {str(e)}")
            return
        
        # 验证整个流程会话ID一致性
        session_ids = [
            dialogue_response.data['data'].get('session_id'),
            exercise_response.data['data'].get('session_id'),
            correction_response.data['data'].get('session_id'),
            follow_up_response.data['data'].get('session_id')
        ]
        
        # 添加调试信息
        print("\n会话ID验证信息:")
        print(f"  期望的会话ID: {integration_session_id}")
        for i, sid in enumerate(session_ids):
            print(f"  步骤{i+1}返回的会话ID: {sid}")
            if sid != integration_session_id:
                print(f"  ❌ 步骤{i+1}会话ID不匹配")
            else:
                print(f"  ✅ 步骤{i+1}会话ID匹配")
        
        # 检查响应数据结构
        print("\n响应数据结构检查:")
        print(f"  对话响应数据结构: {list(dialogue_response.data['data'].keys())}")
        print(f"  练习题响应数据结构: {list(exercise_response.data['data'].keys())}")
        print(f"  答案校正响应数据结构: {list(correction_response.data['data'].keys())}")
        print(f"  后续对话响应数据结构: {list(follow_up_response.data['data'].keys())}")
        
        if all(sid == integration_session_id for sid in session_ids):
            self._record_test_result("integration", True)
            print("\n✅ 会话ID一致性检查通过")
            print("✅ 完整集成流程测试通过！")
        else:
            self._record_test_result("integration", False)
            print("\n❌ 会话ID一致性检查失败")
            print("❌ 完整集成流程测试失败")
        
        print("\n=== 完整集成流程测试完成 ===")

    def test_end_to_end_scenario(self):
        """测试端到端学习场景"""
        print("\n=== 开始测试端到端学习场景 ===")
        
        # 为端到端场景创建新会话ID
        scenario_session_id = str(uuid.uuid4())
        print(f"使用会话ID: {scenario_session_id}\n")
        
        # 步骤1: 学生询问概念
        print("1. 学生询问概念...")
        dialogue_data = {
            'query': '请解释牛顿第二定律，并说明它在日常生活中的应用',
            'session_id': scenario_session_id
        }
        
        try:
            response1 = self.client.post(
                self.dialogue_url,
                data=json.dumps(dialogue_data),
                content_type='application/json'
            )
            self._print_response(response1)
            
            if response1.status_code != 200 or not response1.data['success']:
                self._record_test_result("scenario", False)
                print("❌ 端到端场景步骤1失败")
                return
            print("✅ 步骤1完成")
            
            # 等待一下，模拟真实用户阅读时间
            time.sleep(2)
        except Exception as e:
            self._record_test_result("scenario", False)
            print(f"❌ 步骤1出错: {str(e)}")
            return
        
        # 步骤2: 学生请求练习题
        print("\n2. 学生请求练习题...")
        dialogue_data = {
            'query': '你能给我一些练习题来帮助理解这个概念吗？',
            'session_id': scenario_session_id
        }
        
        try:
            response2 = self.client.post(
                self.dialogue_url,
                data=json.dumps(dialogue_data),
                content_type='application/json'
            )
            self._print_response(response2)
            
            if response2.status_code != 200 or not response2.data['success']:
                self._record_test_result("scenario", False)
                print("❌ 端到端场景步骤2失败")
                return
            
            # 检查是否包含练习题请求信息
            if 'exercise_request' in response2.data['data']:
                print("✅ 步骤2完成 - 对话响应中包含练习题请求信息")
            else:
                print("ℹ️ 步骤2完成 - 对话响应中不包含练习题请求信息，使用默认值继续测试")
            
            # 等待一下，模拟真实用户阅读时间
            time.sleep(2)
        except Exception as e:
            self._record_test_result("scenario", False)
            print(f"❌ 步骤2出错: {str(e)}")
            return
        
        # 步骤3: 系统生成练习题
        print("\n3. 系统生成练习题...")
        # 获取对话中的练习请求信息，或使用默认值
        exercise_request = response2.data['data'].get('exercise_request', {})
        knowledge_point_ids = exercise_request.get('knowledge_point_ids', [self.knowledge_point.id])
        quantity = exercise_request.get('quantity', 1)
        difficulty = exercise_request.get('difficulty', 3)
        
        exercise_data = {
            'query': '牛顿第二定律练习题',
            'knowledge_point_ids': knowledge_point_ids,
            'quantity': quantity,
            'difficulty': difficulty,
            'session_id': scenario_session_id
        }
        
        try:
            response3 = self.client.post(
                self.exercise_url,
                data=json.dumps(exercise_data),
                content_type='application/json'
            )
            self._print_response(response3)
            
            if response3.status_code != 200 or not response3.data['success']:
                self._record_test_result("scenario", False)
                print("❌ 端到端场景步骤3失败")
                return
            print("✅ 步骤3完成")
            
            # 等待一下，模拟真实用户阅读和思考时间
            time.sleep(3)
        except Exception as e:
            self._record_test_result("scenario", False)
            print(f"❌ 步骤3出错: {str(e)}")
            return
        
        # 步骤4: 学生提交答案
        print("\n4. 学生提交答案...")
        # 使用预设的练习题
        correction_data = {
            'exercise_id': self.exercise.id,
            'student_answer': '2 m/s^2',
            'session_id': scenario_session_id
        }
        
        try:
            response4 = self.client.post(
                self.correction_url,
                data=json.dumps(correction_data),
                content_type='application/json'
            )
            self._print_response(response4)
            
            if response4.status_code != 200 or not response4.data['success']:
                self._record_test_result("scenario", False)
                print("❌ 端到端场景步骤4失败")
                return
            print("✅ 步骤4完成")
            
            # 等待一下，模拟真实用户阅读反馈时间
            time.sleep(2)
        except Exception as e:
            self._record_test_result("scenario", False)
            print(f"❌ 步骤4出错: {str(e)}")
            return
        
        # 步骤5: 学生请求更多解释
        print("\n5. 学生请求更多解释...")
        dialogue_data = {
            'query': '我想更深入地理解这个概念，你能给我提供一些进阶的资料或者解释一下相关的力学定律吗？',
            'session_id': scenario_session_id
        }
        
        try:
            response5 = self.client.post(
                self.dialogue_url,
                data=json.dumps(dialogue_data),
                content_type='application/json'
            )
            self._print_response(response5)
            
            if response5.status_code != 200 or not response5.data['success']:
                self._record_test_result("scenario", False)
                print("❌ 端到端场景步骤5失败")
                return
            print("✅ 步骤5完成")
        except Exception as e:
            self._record_test_result("scenario", False)
            print(f"❌ 步骤5出错: {str(e)}")
            return
        
        # 验证整个场景会话ID一致性
        session_ids = [
            response1.data['data'].get('session_id'),
            response2.data['data'].get('session_id'),
            response3.data['data'].get('session_id'),
            response4.data['data'].get('session_id'),
            response5.data['data'].get('session_id')
        ]
        
        # 添加调试信息
        print("\n会话ID验证信息:")
        print(f"  期望的会话ID: {scenario_session_id}")
        for i, sid in enumerate(session_ids):
            print(f"  步骤{i+1}返回的会话ID: {sid}")
            if sid != scenario_session_id:
                print(f"  ❌ 步骤{i+1}会话ID不匹配")
            else:
                print(f"  ✅ 步骤{i+1}会话ID匹配")
        
        # 检查响应数据结构
        print("\n响应数据结构检查:")
        print(f"  对话1响应数据结构: {list(response1.data['data'].keys())}")
        print(f"  对话2响应数据结构: {list(response2.data['data'].keys())}")
        print(f"  练习题响应数据结构: {list(response3.data['data'].keys())}")
        print(f"  答案校正响应数据结构: {list(response4.data['data'].keys())}")
        print(f"  对话3响应数据结构: {list(response5.data['data'].keys())}")
        
        if all(sid == scenario_session_id for sid in session_ids):
            self._record_test_result("scenario", True)
            print("\n✅ 会话ID一致性检查通过")
            print("✅ 端到端学习场景测试通过！")
        else:
            self._record_test_result("scenario", False)
            print("\n❌ 会话ID一致性检查失败")
            print("❌ 端到端学习场景测试失败")
        
        print("\n=== 端到端学习场景测试完成 ===")
    
    def _print_response(self, response):
        """打印响应结果"""
        print(f"  状态码: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"  成功: {response.data.get('success', False)}")
            if 'error_code' in response.data:
                print(f"  错误代码: {response.data['error_code']}")
                print(f"  错误信息: {response.data.get('message', '无错误信息')}")
            
            # 打印响应摘要
            data = response.data.get('data', {})
            if 'answer' in data:
                print(f"  回答摘要: {data['answer'][:100]}..." if len(data['answer']) > 100 else f"  回答: {data['answer']}")
            if 'exercises' in data:
                print(f"  生成练习题数量: {len(data['exercises'])}")
            if 'is_correct' in data:
                print(f"  答案正确性: {data['is_correct']}")
                print(f"  得分: {data['score']}")
    
    def _record_test_result(self, test_type, passed):
        """记录测试结果"""
        self.test_results[test_type]["total"] += 1
        if passed:
            self.test_results[test_type]["passed"] += 1
        else:
            self.test_results[test_type]["failed"] += 1
    
    def print_test_summary(self):
        """打印测试摘要"""
        print("\n=== 测试结果摘要 ===")
        
        for test_type, results in self.test_results.items():
            if results["total"] > 0:
                success_rate = (results["passed"] / results["total"]) * 100
                print(f"{test_type.capitalize()} 测试: {results['passed']}/{results['total']} 通过 ({success_rate:.1f}%)")
        
        total_tests = sum(r["total"] for r in self.test_results.values())
        total_passed = sum(r["passed"] for r in self.test_results.values())
        
        if total_tests > 0:
            overall_rate = (total_passed / total_tests) * 100
            print(f"\n总体测试通过率: {total_passed}/{total_tests} ({overall_rate:.1f}%)")
            
            if total_passed == total_tests:
                print("\n🎉 所有测试通过！学生助手模块集成测试成功！")
            else:
                print(f"\n❗ {total_tests - total_passed} 个测试失败。请检查日志获取详细信息。")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="学生助手模块手动测试工具")
    parser.add_argument(
        "--test", 
        choices=["all", "dialogue", "exercise", "answer", "integration", "scenario"],
        default="all",
        help="要执行的测试类型"
    )
    args = parser.parse_args()
    
    print("\n====================================")
    print("    学生助手模块集成测试工具")
    print("====================================\n")
    
    try:
        # 初始化测试运行器
        runner = TestRunner()
        
        # 设置测试数据
        runner.setup_test_data()
        
        # 根据参数执行测试
        if args.test in ["all", "dialogue"]:
            runner.test_dialogue_flow()
        
        if args.test in ["all", "exercise"]:
            runner.test_exercise_generation()
        
        if args.test in ["all", "answer"]:
            runner.test_answer_correction()
        
        if args.test in ["all", "integration"]:
            runner.test_integration_workflow()
        
        if args.test in ["all", "scenario"]:
            runner.test_end_to_end_scenario()
        
        # 打印测试摘要
        runner.print_test_summary()
        
    except Exception as e:
        print(f"\n❌ 测试执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 