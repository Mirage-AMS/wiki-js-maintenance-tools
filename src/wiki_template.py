# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/26 14:19
# @file         : wiki_template.py
# @Desc         : 基于Jinja2的模板处理类，支持复杂模板语法
# -----------------------------------------

# import from official
from typing import Dict, Any
from pathlib import Path
# import from third-party
from jinja2 import Environment, FileSystemLoader, Template as JinjaTemplate


# import from self-defined


class Template:
    """基于Jinja2的模板文件处理类"""

    def __init__(self, template_path: Path):
        """初始化模板

        Args:
            template_path: 模板文件路径
        """
        self.template_path = template_path
        self._jinja_env = self._init_jinja_env()
        self._template = self._load_template()

    def _init_jinja_env(self) -> Environment:
        """初始化Jinja2环境

        Returns:
            配置好的Jinja2环境
        """
        # 获取模板所在目录
        template_dir = self.template_path.parent

        # 初始化Jinja2环境，配置模板加载器
        return Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,  # 去除块标签周围的空行
            lstrip_blocks=True,  # 去除块标签起始处的空格
            keep_trailing_newline=True,  # 保留末尾换行符
            autoescape=False  # Markdown不需要HTML转义
        )

    def _load_template(self) -> JinjaTemplate:
        """加载模板文件

        Returns:
            Jinja2模板对象

        Raises:
            FileNotFoundError: 模板文件不存在时
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {self.template_path}")

        # 加载模板（使用文件名作为标识）
        return self._jinja_env.get_template(self.template_path.name)

    def render(self, data: Dict[str, Any]) -> str:
        """渲染模板，支持Jinja2的所有语法

        支持的语法包括：
        - 变量引用: {{ A.B.C }}
        - 条件判断: {% if A.B %}...{% endif %}
        - 循环: {% for item in list %}...{% endfor %}
        - 模板继承: {% extends "base.md" %}
        - 宏定义: {% macro %}...{% endmacro %}
        - 过滤器: {{ value|filter_name }}

        Args:
            data: 用于渲染模板的数据，支持嵌套字典

        Returns:
            渲染后的内容
        """
        return self._template.render(**data)

    def add_filter(self, name: str, func: Any) -> None:
        """添加自定义过滤器

        Args:
            name: 过滤器名称（模板中使用的名称）
            func: 过滤器函数
        """
        self._jinja_env.filters[name] = func

    def add_global(self, name: str, value: Any) -> None:
        """添加全局变量或函数

        Args:
            name: 全局对象名称
            value: 全局对象的值
        """
        self._jinja_env.globals[name] = value
