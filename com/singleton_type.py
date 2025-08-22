# ----------------------------------------------------------
# @Time:    2022/9/5 11:33
# @Author:  weiyifan
# @Email:   weiyifan@zwcad.com
# @Version: 1.0
# @Desc:    
# @File:    singleton_type.py
# ----------------------------------------------------------
# off
import threading
# third-site

# self-defined


# # BEGIN WITH
class SingletonType(type):
    """线程安全的单例类"""
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


