"""公共工具函数模块"""

def format_file_size(file_size_bytes: int) -> str:
    """
    格式化文件大小为人类可读的格式
    
    Args:
        file_size_bytes: 文件大小（字节）
    
    Returns:
        格式化后的文件大小字符串
    """
    if file_size_bytes is None:
        return "未知大小"
    
    if file_size_bytes < 1024:
        return f"{file_size_bytes} B"
    elif file_size_bytes < 1024 * 1024:
        return f"{file_size_bytes / 1024:.1f} KB"
    elif file_size_bytes < 1024 * 1024 * 1024:
        return f"{file_size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{file_size_bytes / (1024 * 1024 * 1024):.1f} GB"