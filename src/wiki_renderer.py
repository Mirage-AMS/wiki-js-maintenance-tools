# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/28 08:53
# @file         : wiki_renderer.py
# @Desc         : 预处理器
# -----------------------------------------

# import from official
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union
from pathlib import Path
# import from third-party
# import from self-defined


class WikiRenderer(ABC):
    @abstractmethod
    def render(self, content: Any) -> Any:
        """
        渲染Wiki内容
        :param content:
        :return:
        """
        pass


class WikiPTLRenderer(WikiRenderer):
    """
    在模板渲染前对原始数据进行预渲染处理的类，主要处理HTML转义和图标替换
    """
    IMAGE_STORAGE_PATH = "/assets/icon"
    # 优化正则表达式，只匹配符合命名规范的图标（字母、数字、下划线、连字符）
    ICON_PATTERN = re.compile(r"\$\{([a-zA-Z0-9_-]+)\}")

    def _render_html_content(self, content: str) -> str:
        """将文本中的换行符转换为HTML的<br>标签"""
        return content.replace("\n", "<br>")

    def _render_icon_content(self, content: str) -> str:
        """
        替换内容中的图标占位符为HTML img标签

        占位符格式: ${icon_name}
        替换后: <img src="path/to/icon_name.png" alt="icon_name">
        """

        def replace_icon(match: re.Match) -> str:
            image_name = match.group(1)
            image_path = f"{self.IMAGE_STORAGE_PATH}/{image_name}.png"
            return f'<img src="{image_path}" alt="{image_name}" style="height: 1em; vertical-align: -0.15em;">'

        return self.ICON_PATTERN.sub(replace_icon, content)

    def _process_string(self, content: str) -> str:
        """处理字符串类型的内容：先处理HTML，再处理图标"""
        processed = self._render_html_content(content)
        processed = self._render_icon_content(processed)
        return processed

    def _recur_render(self, content: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
        """
        递归渲染内容

        对于字典：递归处理每个值
        对于列表：递归处理每个元素
        对于字符串：处理HTML和图标
        其他类型：保持不变
        """
        if isinstance(content, Dict):
            return {key: self._recur_render(value) for key, value in content.items()}
        elif isinstance(content, List):
            return [self._recur_render(item) for item in content]
        elif isinstance(content, str):
            return self._process_string(content)
        else:
            return content

    def render(self, content: Any) -> Any:
        """
        渲染入口方法，对内容进行预渲染处理

        :param content: 需要处理的数据，必须是字典类型
        :return: 处理后的内容
        :raises TypeError: 如果输入内容不是字典类型
        """
        if not isinstance(content, Dict):
            raise TypeError("Content must be a dictionary.")

        return self._recur_render(content)

if __name__ ==  "__main__":
    renderer = WikiPTLRenderer()
    data = {
        "title": "Hello World",
        "body": "This is my first post.\nIt contains some text and an icon: ${aP01}${eE01}.",
        "data": {
            "text": "Some additional information.",
            "list": ["Item 1", "Item 2\nwith line break"]
        },
        "footer": [
            "Copyright © 2023 My Blog",
            "Powered by ${iPTL}"
        ]
    }
    rendered_data = renderer.render(data)
    print(rendered_data)