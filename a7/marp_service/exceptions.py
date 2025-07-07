class MarpServiceError(Exception):
    """基础异常类，所有marp服务相关异常的父类。"""
    pass


class MarpCLIError(MarpServiceError):
    """CLI调用相关错误，如命令执行失败、命令未找到等。"""
    pass


class MarpFileError(MarpServiceError):
    """文件处理错误，如文件创建失败、读写权限问题等。"""
    pass


class MarpConversionError(MarpServiceError):
    """转换过程错误，如转换失败、格式不支持等。"""
    pass 