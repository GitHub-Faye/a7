from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

class HealthCheckView(APIView):
    """
    一个简单的API健康检查端点
    """
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        返回API健康状态
        """
        return Response(
            {"status": "healthy", "message": "API服务运行正常"},
            status=status.HTTP_200_OK
        ) 