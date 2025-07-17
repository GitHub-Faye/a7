import os
import uuid
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

@deconstructible
class CoursewareFileStorage(FileSystemStorage):
    """
    自定义文件存储类，用于处理课件文件的存储
    - 生成唯一文件名，避免文件覆盖
    - 按课程ID和文件类型组织文件结构
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_valid_name(self, name):
        """
        返回适合文件系统的文件名
        """
        return super().get_valid_name(name)
    
    def get_available_name(self, name, max_length=None):
        """
        生成唯一的文件名，避免文件覆盖
        使用UUID确保唯一性
        
        注意：此方法不应改变文件路径，只处理文件名部分
        """
        # 分离文件路径和文件名
        dir_name, file_name = os.path.split(name)
        # 获取文件扩展名
        ext = os.path.splitext(file_name)[1]
        # 生成UUID作为文件名
        uuid_name = f"{uuid.uuid4().hex}{ext}"
        # 重新组合路径和文件名
        name = os.path.join(dir_name, uuid_name) if dir_name else uuid_name
        
        return super().get_available_name(name, max_length)
    
    def generate_filename(self, filename):
        """
        生成完整的文件路径
        可以在这里实现按课程/文件类型组织文件的逻辑
        """
        return super().generate_filename(filename) 