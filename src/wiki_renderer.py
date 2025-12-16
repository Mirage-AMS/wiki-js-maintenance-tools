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
from typing import Any, Match
# import from third-party
# import from self-defined
from src.keyword_replacer import KeywordReplacer

class WikiRenderer(ABC):
    @abstractmethod
    def render(self, content: Any, suffix: str=".html") -> Any:
        """
        渲染Wiki内容
        :param content:
        :param suffix:
        :return:
        """
        pass


class WikiPTLRenderer(WikiRenderer):
    # 其他常量
    IMAGE_EXTENSION = ".png"
    SUFFIX_MD = ".md"
    SUFFIX_HTML = ".html"
    ICON_PATTERN = re.compile(r"\$\{([a-z][A-Z][a-zA-Z0-9]{2})\}")
    # 路径常量
    IMAGE_STORAGE_PATH = "/assets/icon"

    IMAGE_DICT = {
        "eE01": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "地之元素"),
        "eW01": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "水之元素"),
        "eF01": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "火之元素"),
        "eA01": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "风之元素"),
        "eE05": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "地之元素"),
        "eW05": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "水之元素"),
        "eF05": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "火之元素"),
        "eA05": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "风之元素"),
        "eC01": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "万用元素"),
        "eR01": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "无色元素"),
        "eR02": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "无色元素"),
        "eR03": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "无色元素"),
        "eR04": ("/rule/rule_basic/rule_element", "#h-2-元素种类", "无色元素"),
        "tBgn": ("/rule/rule_basic/rule_basic_intro", "#h-124-开始阶段", "开始阶段"),
        "tDrw": ("/rule/rule_basic/rule_basic_intro", "#h-125-抽牌阶段", "抽牌阶段"),
        "tPrp": ("/rule/rule_basic/rule_basic_intro", "#h-126-准备阶段", "准备阶段"),
        "tAct": ("/rule/rule_basic/rule_basic_intro", "#h-127-行动阶段", "行动阶段"),
        "tEnd": ("/rule/rule_basic/rule_basic_intro", "#h-128-结束阶段", "结束阶段"),
    }

    # 关键词替换字典
    URL_DICT = {
        "解锁": {
            "解锁率": None,
            "解锁代价": None,
            "": ("/zh/rule/rule_basic/rule_ability", "#h-2-常规解锁", "常规解锁")
        },
        "永久": {
            "永久+": None,
            "永久-": None,
            "永久获得以下效果": None,
            "永久获得": None,
            "永久启用": None,
            "永久加入": None,
            "": ("/rule/rule_basic/rule_effect", "#h-11-永久类效果", "永久类效果"),
        },
        "启动": {
            "": ("/rule/rule_basic/rule_effect", "#h-12-启动类效果", "启动类效果")
        },
        "快速": {
            "": ("/rule/rule_basic/rule_effect", "#h-13-快速类效果", "快速类效果")
        },
        "骰子": {
            "": ("/rule/rule_basic/rule_exploration", "#h-7-投掷标准骰子", "投掷标准骰子")
        },
        "[复制效果]": {
            "": ("/rule/rule_advanced/rule_classified_effects", "#h-23-复制效果", "复制效果")
        }
    }

    def __init__(self):
        self.keyword_replacer = KeywordReplacer(self.URL_DICT)

    @classmethod
    def html_link_formatter(cls, match_text: str, replacement_data: tuple) -> str:
        url, chap, tooltip = replacement_data
        return f'<a href="{url}{chap}" title="{tooltip}">{match_text}</a>'

    def _render_keyword_content(self, content: str, suffix: str) -> str:
        keyword_replacer = self.keyword_replacer
        # 目前只替换html页面中的关键词
        if suffix == self.SUFFIX_HTML:
            content = keyword_replacer.replace(content, self.html_link_formatter)

        return content

    def _render_icon_content(self, content: str, suffix: str) -> str:
        """
        替换内容中的图标占位符为HTML img标签
        占位符格式: ${icon_name}
        替换后: <img src="path/to/icon_name.png" alt="icon_name">
        """
        # 闭包外预计算公共部分
        base_image_path = self.IMAGE_STORAGE_PATH
        image_ext = self.IMAGE_EXTENSION
        image_dict = self.IMAGE_DICT

        def replace_icon(match: Match[str]) -> str:
            image_name = match.group(1)
            image_path = f"{base_image_path}/{image_name}{image_ext}"
            _url, _chap, _tooltip = image_dict.get(image_name, ("/", "#", ""))
            if suffix == self.SUFFIX_MD or suffix == self.SUFFIX_HTML:
                return (f'<a href="{_url}{_chap}" title="{_tooltip}">'
                        f'<img src="{image_path}" alt="{image_name}" style="height: 1.2em; vertical-align: -0.20em; cursor: pointer;">'
                        f'</a>')
            else:
                raise ValueError(f"Unsupported file type: {suffix}")

        return self.ICON_PATTERN.sub(replace_icon, content)

    def render(self, content: Any, suffix: str = ".html") -> Any:
        processed = content
        # 先替换关键词
        processed = self._render_keyword_content(processed, suffix)
        # 再替换图标(图标是变量占位符代表的, 不可能二次替换出现问题)
        processed = self._render_icon_content(processed, suffix)
        return processed
