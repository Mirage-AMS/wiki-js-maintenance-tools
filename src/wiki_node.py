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
import frontmatter
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
        self.data: Optional[Dict[str, Any]] = None  # 公共数据存储
        self.data_file: Optional[Path] = None  # 公共数据文件路径
        self.template: Optional[Template] = None  # 公共模板
        self.template_path: Optional[Path] = None  # 公共模板路径
        self.parent: Optional[WikiNode] = None  # 新增父节点引用

    def is_directory(self) -> bool:
        return isinstance(self, DirectoryNode)

    def is_document(self) -> bool:
        return isinstance(self, DocumentNode)

    def load_data(self) -> None:
        """加载数据文件（目录节点和文档节点通用）"""
        if not self.data_file:
            return

        full_path = self.path / self.data_file
        if not full_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {full_path}")

        print(f"加载数据文件: {full_path}")

        if full_path.suffix == '.json':
            with open(full_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        elif full_path.suffix == '.md':
            post = frontmatter.load(str(full_path))
            self.data = post.metadata
            self.data['content'] = post.content
        else:
            raise ValueError(f"未知的数据文件格式: {full_path}")

    # 提取公共的渲染方法到父类
    def render(self, renderer: Optional[WikiRenderer]) -> str:
        """渲染内容（目录节点和文档节点通用）"""
        if not self.data and self.data_file:
            self.load_data()

        if not self.template:
            raise ValueError(f"节点 {self.name} 没有设置模板")

        # 模板渲染
        render_data = self.template.render(self.data or {})

        # 后渲染
        if renderer and render_data:
            suffix = self.template.template_path.suffix
            render_data = renderer.render(render_data, suffix)

        return render_data

    def set_template(self, template: Template) -> None:
        """设置模板（目录节点和文档节点通用）"""
        if isinstance(template, Template):
            self.template = template
            self.template_path = template.template_path
        else:
            raise TypeError("模板必须是Template类型")

class DirectoryNode(WikiNode):
    """目录节点类，包含子节点和索引文件"""

    def __init__(self, name: str, path: Path, index_file: Path, data_file: Optional[Path] = None):
        super().__init__(name, path)
        self.index_file = index_file  # 目录索引文件路径（目录节点特有）
        if not self.index_file.exists():
            raise FileNotFoundError(f"索引文件不存在: {self.index_file}")

        self.children: List[WikiNode] = []  # 子节点列表（目录节点特有）
        self.data_file = data_file  # 目录数据文件路径（目录节点可选）
        if self.data_file and not self.data_file.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_file}")

    def add_child(self, child: WikiNode) -> None:
        """添加子节点并设置父引用"""
        child.parent = self  # 新增：设置子节点的父节点
        self.children.append(child)


class DocumentNode(WikiNode):
    """资料文件节点类"""

    def __init__(self, name: str, path: Path, data_file: Path):
        super().__init__(name, path)
        self.data_file = data_file  # 初始化数据文件（文档节点必传）
        if not self.data_file.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
