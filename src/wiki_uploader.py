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
import os
from typing import Callable, Optional, Dict
from pathlib import Path
from dotenv import load_dotenv
# import from third-party
# import from self-defined
from com.util import pathUtil
from com.graphql import WikiJSGraphQLClient
from src.wiki_node import DocumentNode
from src.wiki_indexer import WikiIndexer
from src.wiki_renderer import WikiRenderer, WikiPTLRenderer
from src.html_extractor import extract_html_parts


class WikiUploader:
    def __init__(self, locale: str = "zh", renderer: Optional[WikiRenderer] = None):
        """
        :param locale:
        :param renderer:
        :return:
        """
        self.locale = locale
        self.renderer = renderer

        # 读取环境变量
        load_dotenv(pathUtil.getEnvFile())
        wiki_url = os.getenv("WIKI_URL")
        wiki_api_token = os.getenv("WIKI_API_TOKEN")

        self.wiki_indexer = WikiIndexer(locale).build_index()
        self.wiki_client = WikiJSGraphQLClient(wiki_url, wiki_api_token)

    def _save(self, doc: DocumentNode, content: str) -> None:
        """
        保存文档到本地
        :param doc:
        :param content:
        :return:
        """
        doc_path = doc.path / doc.data_file
        template_suffix = doc.template.template_path.suffix
        rel_path = doc_path.relative_to(pathUtil.getDataDir())
        target_file = pathUtil.getTmpDir() / rel_path.with_suffix(template_suffix)
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"已保存文件: {target_file}")

    def _upload(self, doc: DocumentNode, content: str) -> None:
        """
        上传文档到Wiki.js
        :param doc:
        :param content:
        :return:
        """
        name = doc.name
        data = doc.data
        scriptJs = ""
        scriptCss = ""
        # path = doc.path.as_posix()
        template_suffix = doc.template.template_path.suffix


        wikijs_path = data.get("path")
        wikijs_tags = data.get("tags")
        wikijs_editor = "markdown"
        if template_suffix == ".html":
            wikijs_editor = "code"
            try:
                html_parts = extract_html_parts(content)
            except Exception:
                print("Failed to extract HTML parts, using the original content instead.")
                html_parts = {
                    'html': content,
                    'script': "",
                    'style': ""
                }
            content = html_parts['html']
            scriptJs = html_parts['script']
            scriptCss = html_parts['style']

        wikijs_title = name
        if data.get("card", {}).get("card_name", None):
            wikijs_title = data["card"]["card_name"]

        g_resp = self.wiki_client.get_page_by_path(locale=self.locale, path=wikijs_path)
        retry_num = 0
        while g_resp is None and retry_num <= 3:
            c_resp = self.wiki_client.create_page(
                title=wikijs_title,
                locale=self.locale,
                path=wikijs_path,
                content="initial",
                editor=wikijs_editor,
                tags=[],
            )
            if c_resp is None:
                raise Exception(f"Failed to create page: {name}")
            c_resp_result = c_resp.get("responseResult")
            if isinstance(c_resp_result, Dict):
                if not c_resp_result.get("succeeded", False):
                    c_resp_result_error_code = c_resp_result.get('errorCode')
                    c_resp_result_error_message = c_resp_result.get('message')
                    raise Exception(f"Failed to create page: {name}, code: {c_resp_result_error_code}, message: {c_resp_result_error_message}")

            print(f"已创建页面: {name}")
            g_resp = self.wiki_client.get_page_by_path(locale=self.locale, path=wikijs_path)
            retry_num += 1

        u_resp = self.wiki_client.update_page(
            page_id=g_resp.get("id"),
            content=content,
            scriptCss=scriptCss,
            scriptJs=scriptJs,
            editor=wikijs_editor,
            tags=wikijs_tags,
        )
        if u_resp is None:
            raise Exception(f"Failed to update page: {name}")
        if u_resp.get("responseResult").get("succeeded", False):
            print(f"已更新页面: {name}")
        else:
            raise Exception(f"Failed to update page: {name}, error: {u_resp.get('responseResult').get('message')}")

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

        documents = self.wiki_indexer.get_all_documents()
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
                self._save(doc, content)
                count_save += 1

            if is_upload:
                self._upload(doc, content)
                count_upload += 1
                print(f"已上传文件: {doc.name}")

        print(f"处理完成，共处理 {count_total} 中的 {count_process} 条文档，其中 {count_upload} 条成功上传，{count_save} 条保存至本地")
        return count_process


if __name__ == '__main__':
    def template_filter(doc: DocumentNode):
        if doc.path and "card" not in str(doc.path):
            return False
        if doc.name == "card":
            return False
        return True

    uploader = WikiUploader(renderer=WikiPTLRenderer())
    uploader.upload(
        is_upload=True,
        filter_func=template_filter
    )
