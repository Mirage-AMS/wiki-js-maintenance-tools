# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/26 14:04
# @file         : wiki_indexer.py
# @Desc         :
# -----------------------------------------

# import from official
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
# import from third-party

# import from self-defined
from com.util import pathUtil
from src.wiki_node import DirectoryNode, DocumentNode, WikiNode
from src.wiki_template import Template


class WikiIndexer:
    """Wiki索引管理器，负责构建整个资料树"""

    def __init__(self, locale: str = "zh", root_index: str = "contents.json"):
        """初始化索引管理器
        Args:
            locale: 语言
            root_index: 根目录索引文件
        """
        self.locale = locale
        self.root_path = pathUtil.getDataDir() / locale
        self.templates_path = self.root_path / "templates"
        self.root_index_file = self.root_path / root_index
        self.root_node: Optional[DirectoryNode] = None

    def _set_node_template(self, node, node_info):
        """设置节点的数据文件和模板"""
        if "template" in node_info and node_info["template"] is not None:
            template_path = self.templates_path / node_info["template"]
            print(f"{node.name}: 加载自定义模板 {template_path}")
            node.template = Template(template_path)
            return
        elif node.template is not None:
            print(f"{node.name}: 已有模板{node.template.template_path}")
            return
        elif node.parent is not None and node.parent.template is not None:
            print(f"{node.name}: 使用父级模板 {node.parent.template.template_path}")
            node.template = node.parent.template
            return

        raise Exception(f"{node.name}: 没有找到模板")

    def build_index(self) -> 'WikiIndexer':
        """构建整个Wiki的索引结构

        Returns:
            根目录节点
        """
        if not self.root_index_file.exists():
            raise FileNotFoundError(f"根目录索引文件不存在: {self.root_index_file}")

        # 解析根目录
        with open(self.root_index_file, 'r', encoding='utf-8') as f:
            root_data = json.load(f)

        self.root_node = DirectoryNode(
            name="root",
            path=self.root_path,
            index_file=self.root_index_file
        )
        # 递归解析子节点
        self._parse_directory(self.root_node, root_data)

        return self

    # 修改wiki_indexer.py中的_parse_directory方法
    def _parse_directory(self, directory_node: DirectoryNode, dir_data: Dict[str, Any]) -> None:
        """
        递归解析目录节点(不存在孤立的叶子节点, 因此所有文档节点都可以被目录访问到)
        目录节点的数据结构形如: {
            "template": "self_template.html",
            "children": {
                # 子目录
                "subdir": {
                    "index": "subdir_index.json",
                    "data?": "subdir_data.json",
                    "template?": "subdir_template.html"
                },
                # 子文档
                "subdoc": {
                    "data": "subdoc_data.json",
                    "template?": "subdoc_template.html"
                }
            }
        }
        :param directory_node: 目录节点
        :param dir_data: 目录信息
        """
        print(f"开始解析: {directory_node.name}")

        # 处理当前节点自身数据和模板
        self._set_node_template(directory_node, dir_data)

        # 处理子节点
        if "children" not in dir_data:
            raise ValueError(f"目录节点{directory_node.name}没有子节点, 可能不是一个有效的目录")

        for child_name, child_info in dir_data["children"].items():
            is_child_directory = "index" in child_info
            is_child_document = "data" in child_info

            # index 文件在子目录下，data文件在当前目录下
            subdir_path = directory_node.path / child_name
            child_data_file = directory_node.path / child_info["data"] if is_child_document else None
            child_index_file = subdir_path / child_info["index"] if is_child_directory else None

            if is_child_directory:
                child_node = DirectoryNode(
                    name=child_name,
                    path=subdir_path,
                    index_file=child_index_file,
                    data_file=child_data_file
                )
            elif is_child_document:
                child_node = DocumentNode(
                    name=child_name,
                    path=directory_node.path,
                    data_file=child_data_file
                )
            else:
                raise ValueError(f"无法识别的子节点类型: {child_name}")

            # 添加到当前目录的子节点列表(同时反向追溯parent)
            directory_node.add_child(child_node)

            # 处理子节点的模板
            self._set_node_template(child_node, child_info)

            # 对子目录进行递归解析（现在模板已经设置完成）
            if is_child_directory:
                # 加载子目录的索引文件
                with open(child_index_file, 'r', encoding='utf-8') as f:
                    child_dir_data = json.load(f)
                # 递归调用，此时子节点的模板已经设置好了
                self._parse_directory(child_node, child_dir_data)

    # 修改wiki_indexer.py中的_get_all_documents方法，使其包含目录节点
    def get_all_documents(self) -> List[WikiNode]:
        """获取所有资料文件节点，包括有data的目录节点"""
        if not self.root_node:
            raise RuntimeError("请先调用build_index()构建索引")

        documents = []
        self._collect_documents(self.root_node, documents)
        return documents

    def _collect_documents(self, node: WikiNode, documents: List[WikiNode]) -> None:
        """递归收集所有资料文件节点，包括有data的目录节点"""
        # 如果是文档节点，直接添加
        if node.is_document():
            documents.append(node)
        # 如果是目录节点且有data文件，也添加到文档列表
        elif node.is_directory() and node.data_file:
            documents.append(node)

        # 递归处理子节点
        if node.is_directory():
            for child in node.children:
                self._collect_documents(child, documents)


if __name__ == "__main__":

    # 创建索引管理器并构建索引
    indexer = WikiIndexer(locale="zh")
    root_node = indexer.build_index()
    print("成功构建Wiki索引")

    # 获取所有资料文件并渲染
    documents = indexer.get_all_documents()
    print(f"找到 {len(documents)} 个资料文件")

    for doc in documents:
        if "card" not in doc.name:
            continue
        print(f"\n渲染资料: {doc.name}")
        try:
            content = doc.render()
            # 这里可以添加上传到Wiki.js的代码
            # 示例：仅打印前100个字符
            print(f"渲染结果:\n{content[:100]}")
            doc_path = doc.path / doc.data_file
            template_file_suffix = doc.template.template_path.suffix
            rel_path = doc_path.relative_to(pathUtil.getDataDir())
            tmp_path = pathUtil.getTmpDir() / rel_path
            tmp_path.parent.mkdir(parents=True, exist_ok=True)
            target_file = tmp_path.with_suffix(template_file_suffix)
            print(target_file)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            print(f"渲染失败: {str(e)}")



