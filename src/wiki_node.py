# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/26 14:20
# @file         : wiki_node.py
# @Desc         :
# -----------------------------------------

# import from official
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
# import from third-party

# import from self-defined
from src.wiki_template import Template
from src.wiki_renderer import WikiRenderer

class WikiNode:
    """Wiki节点基类"""

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    def is_directory(self) -> bool:
        return isinstance(self, DirectoryNode)

    def is_document(self) -> bool:
        return isinstance(self, DocumentNode)


class DirectoryNode(WikiNode):
    """目录节点类，包含子节点和可能的模板"""

    def __init__(self, name: str, path: Path, index_file: Path):
        super().__init__(name, path)
        self.index_file = index_file  # 目录索引文件路径
        self.children: List[WikiNode] = []
        self.template: Optional[Template] = None
        self.template_path: Optional[Path] = None

    def add_child(self, child: WikiNode) -> None:
        """添加子节点"""
        self.children.append(child)

    def set_template(self, template_path: Path) -> None:
        """设置目录使用的模板"""
        if template_path:
            full_path = self.path / template_path
            self.template_path = full_path
            self.template = Template(full_path)


class DocumentNode(WikiNode):
    """资料文件节点类"""

    def __init__(self, name: str, path: Path, data_file: Path):
        super().__init__(name, path)
        self.data_file = data_file  # 资料文件路径
        self.data: Optional[Dict[str, Any]] = None
        self.template: Optional[Template] = None

    def load_data(self) -> None:
        """加载资料文件数据"""
        full_path = self.path / self.data_file
        if not full_path.exists():
            raise FileNotFoundError(f"资料文件不存在: {full_path}")

        print(f"加载资料文件: {full_path}")

        if full_path.suffix == '.json':
            with open(full_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        elif full_path.suffix == '.md':
            with open(full_path, 'r', encoding='utf-8') as f:
                self.data = {'content': f.read()}

    def set_template(self, template: Template) -> None:
        """设置用于渲染该资料的模板"""
        self.template = template

    def render(self, pre_renderer: Optional[WikiRenderer] = None) -> str:
        """渲染资料内容"""
        if not self.data:
            self.load_data()

        if not self.template:
            raise ValueError(f"资料 {self.name} 没有设置模板")

        # 使用传入的预渲染器处理数据
        render_data = self.data
        if pre_renderer and self.data is not None:
            render_data = pre_renderer.render(self.data)

        return self.template.render(render_data)