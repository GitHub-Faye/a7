from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Course, KnowledgePoint, Courseware
from .serializers import (
    CourseSerializer, 
    CourseCreateSerializer, 
    CourseUpdateSerializer
)
from .permissions import IsTeacherOrAdmin, IsCourseTeacherOrAdmin


class CourseViewSet(viewsets.ModelViewSet):
    """
    课程视图集，提供课程的增删改查功能
    """
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'subject', 'grade_level']
    ordering_fields = ['created_at', 'title', 'subject', 'grade_level']
    
    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        """
        if self.action == 'create':
            return CourseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CourseUpdateSerializer
        return CourseSerializer
    
    def get_permissions(self):
        """
        根据操作类型设置不同的权限
        """
        if self.action == 'create':
            # 只有教师和管理员可以创建课程
            self.permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 只有课程创建者和管理员可以修改或删除课程
            self.permission_classes = [permissions.IsAuthenticated, IsCourseTeacherOrAdmin]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_summary="获取当前用户创建的课程列表",
        operation_description="返回当前已认证用户创建的所有课程"
    )
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """
        获取当前用户创建的课程列表
        """
        user = request.user
        queryset = self.queryset.filter(teacher=user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
