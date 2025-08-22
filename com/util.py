# -*- coding: utf-8 -*-
# @Author       : weiyifan
# @Time         : 2022-07-30
# @File         : util.py
# @Desc         :
# 
# -----------------------------------------

# import from official
from pathlib import Path
# import from third-party
# import from self-defined
from com.singleton_type import SingletonType


class PathUtil(metaclass=SingletonType):
    """
    路径处理工具类
    使用PathUtil.rootPath()获取根目录路径
    """

    def __init__(self) -> None:
        self.rootPath = Path(__file__).resolve().parent.parent

    def getEnvFile(self) -> Path:
        return self.rootPath / ".env"

    # 返回src路径
    def getSrcDir(self) -> Path:
        return self.rootPath / "src"

    def getDocDir(self) -> Path:
        return self.rootPath / "doc"

    def getModelsDir(self) -> Path:
        return self.rootPath / "models"

    def getTmpDir(self) -> Path:
        return self.rootPath / "tmp"

pathUtil = PathUtil()

if __name__ == '__main__':
    """测试"""
    print(pathUtil.rootPath)
