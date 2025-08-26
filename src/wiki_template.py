# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/26 14:19
# @file         : wiki_template.py
# @Desc         :
# -----------------------------------------

# import from official
from typing import Dict, Any
from pathlib import Path
# import from third-party
# import from self-defined

class Template:
    """模板文件处理类"""

    def __init__(self, template_path: Path):
        """初始化模板

        Args:
            template_path: 模板文件路径
        """
        self.template_path = template_path
        self.content = self._load_template()

    def _load_template(self) -> str:
        """加载模板文件内容

        Returns:
            模板文件内容
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {self.template_path}")

        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def render(self, data: Dict[str, Any]) -> str:
        """渲染模板

        Args:
            data: 用于渲染模板的数据

        Returns:
            渲染后的内容
        """
        # 这里使用简单的字符串替换作为示例
        # 实际应用中可以使用更强大的模板引擎如Jinja2
        rendered = self.content
        for key, value in data.items():
            key_to_replace = "{{" + key + "}}"
            rendered = rendered.replace(key_to_replace, str(value))
        return rendered