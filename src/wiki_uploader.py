# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/28 08:42
# @file         : wiki_uploader.py
# @Desc         :
# -----------------------------------------

# import from official
from typing import Callable, Optional
from pathlib import Path
# import from third-party

# import from self-defined
from com.util import pathUtil
from src.wiki_node import DocumentNode
from src.wiki_indexer import WikiIndexer
from src.wiki_renderer import WikiRenderer, WikiPTLRenderer


class WikiUploader:
    def __init__(self, locale: str = "zh", renderer: Optional[WikiRenderer] = None):
        """

        :param locale:
        """
        self.locale = locale
        self.indexer = WikiIndexer(locale).build_index()
        self.renderer = renderer

    def _get_target_file_path(self, doc: DocumentNode) -> Path:
        """计算目标文件的保存路径"""
        doc_path = doc.path / doc.data_file
        template_suffix = doc.template.template_path.suffix
        rel_path = doc_path.relative_to(pathUtil.getDataDir())
        return pathUtil.getTmpDir() / rel_path.with_suffix(template_suffix)

    def upload(
            self,
            is_save: bool = True,
            is_upload: bool = True,
            filter_func: Callable[[DocumentNode], bool] = lambda x: False
    ):
        """
        上传满足条件的文档
        :param is_save: 是否缓存在本地
        :param is_upload: 是否上传到Wiki.js
        :param filter_func: 上传过滤器, 默认不满足任何条件
        :return:
        """

        documents = self.indexer.get_all_documents()
        count_total = len(documents)
        count_process = 0
        count_upload = 0
        count_save = 0


        for doc in documents:

            # apply filter
            if not filter_func(doc):
                continue

            # 渲染文档内容
            content = doc.render(pre_renderer=self.renderer)
            count_process += 1

            if is_save:
                # 计算文件路径
                target_file = self._get_target_file_path(doc)

                # 确保目录存在
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # 写入文件
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                count_save += 1
                print(f"已保存文件: {target_file}")

            if is_upload:
                # TODO: 上传到Wiki.js
                count_upload += 1
                print(f"已上传文件: {doc.name}")

        print(f"处理完成，共处理 {count_total} 中的 {count_process} 条文档，其中 {count_upload} 条成功上传，{count_save} 条保存至本地")
        return count_process


if __name__ == '__main__':
    def template_filter(doc: DocumentNode):
        if "card" not in doc.name:
            return False
        return True

    uploader = WikiUploader(renderer=WikiPTLRenderer())
    uploader.upload(filter_func=template_filter)
