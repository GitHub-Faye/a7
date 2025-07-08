from django.urls import path
from .views import MarpConversionView

app_name = 'marp_service'
 
urlpatterns = [
    path('convert/', MarpConversionView.as_view(), name='convert'),
    # 如果将来实现文件上传端点，可以添加在这里
    # path('convert-file/', MarpFileConversionView.as_view(), name='convert_file'),
] 