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
        self.root_path = pathUtil.getDataDir() / locale
        self.root_index_file = self.root_path / root_index
        self.root_node: Optional[DirectoryNode] = None

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

        # 处理根目录的模板
        if "template" in root_data:
            self.root_node.set_template(root_data["template"])

        # 递归解析子节点
        self._parse_directory(self.root_node, root_data)

        return self

    def _parse_directory(self, directory_node: DirectoryNode, dir_data: Dict[str, Any]) -> None:
        """递归解析目录节点

        Args:
            directory_node: 目录节点
            dir_data: 目录索引文件中的数据
        """
        if "children" not in dir_data:
            return

        for child_name, child_info in dir_data["children"].items():
            # 子节点是目录
            if "index" in child_info:
                child_path = directory_node.path / child_name
                child_index_file = child_path / child_info["index"]

                # 创建子目录节点
                child_node = DirectoryNode(
                    name=child_name,
                    path=child_path,
                    index_file=child_index_file
                )

                # 设置子目录的模板
                if "template" in child_info:
                    child_node.set_template(child_info["template"])
                elif directory_node.template:
                    child_node.template = directory_node.template

                # 读取子目录索引文件并递归解析
                with open(child_index_file, 'r', encoding='utf-8') as f:
                    child_dir_data = json.load(f)

                self._parse_directory(child_node, child_dir_data)
                directory_node.add_child(child_node)

            # 子节点是资料文件
            elif "data" in child_info:
                child_node = DocumentNode(
                    name=child_name,
                    path=directory_node.path,
                    data_file=child_info["data"]
                )

                # 确定使用的模板 - 优先使用自身指定的模板，否则使用父目录的模板
                if "template" in child_info:
                    template_path = directory_node.path / child_info["template"]
                    child_node.set_template(Template(template_path))
                elif directory_node.template:
                    child_node.set_template(directory_node.template)

                directory_node.add_child(child_node)

    def get_all_documents(self) -> List[DocumentNode]:
        """获取所有资料文件节点

        Returns:
            资料文件节点列表
        """
        if not self.root_node:
            raise RuntimeError("请先调用build_index()构建索引")

        documents = []
        self._collect_documents(self.root_node, documents)
        return documents

    def _collect_documents(self, node: WikiNode, documents: List[DocumentNode]) -> None:
        """递归收集所有资料文件节点"""
        if node.is_document():
            documents.append(node)
        elif node.is_directory():
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



