# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/9/24 14:24
# @file         : keyword_replacer.py
# @Desc         :
# -----------------------------------------

# import from official
import re
from typing import Callable, Dict, List, Any
# import from third-party

# import from self-defined

class KeywordReplacer:
    """支持自定义替换逻辑的关键词替换器"""

    def __init__(self, replace_dict: Dict[str, Dict[str, tuple]]):
        self.replace_dict = replace_dict
        # 预编译所有正则表达式并生成固定占位符
        self.patterns = self._preprocess_patterns()

    def _preprocess_patterns(self) -> List[Dict[str, Any]]:
        """预处理替换模式，生成固定占位符和编译正则"""
        patterns = []
        pattern_id = 0

        # 按关键词长度降序处理
        keywords = sorted(self.replace_dict.keys(), key=lambda x: len(x), reverse=True)

        for keyword in keywords:
            contexts = self.replace_dict[keyword]
            # 按上下文长度降序
            sorted_contexts = sorted(contexts.items(), key=lambda x: len(x[0]), reverse=True)

            for context, replacement_data in sorted_contexts:
                match_text = context if context else keyword
                # 生成固定格式的占位符
                placeholder = f"__REPL_{pattern_id}__"
                # 编译正则
                regex = re.compile(re.escape(match_text))
                # 存储模式信息
                patterns.append({
                    'regex': regex,
                    'placeholder': placeholder,
                    'match_text': match_text,
                    'replacement_data': replacement_data
                })
                pattern_id += 1

        return patterns

    def replace(self, text: str, formatter: Callable[[str, tuple], str]) -> str:
        """
        执行替换操作

        参数:
            text: 需要处理的文本
            formatter: 替换格式化函数，接受(match_text, replacement_data)并返回替换后的字符串

        返回:
            替换后的文本
        """
        # 替换池：占位符与实际替换内容的映射
        replacement_pool = {}
        marked_text = text

        # 应用所有模式
        for pattern_info in self.patterns:
            regex = pattern_info['regex']
            placeholder = pattern_info['placeholder']
            match_text = pattern_info['match_text']
            replacement_data = pattern_info['replacement_data']

            # 找到所有匹配
            matches = list(regex.finditer(marked_text))
            # 从后往前处理
            for match in reversed(matches):
                start, end = match.span()

                # 检查是否已被替换
                is_replaced = any(
                    repl_placeholder in marked_text[start:end]
                    for repl_placeholder in replacement_pool.keys()
                )

                if not is_replaced:
                    # 使用提供的格式化函数生成替换内容
                    replacement = formatter(match_text, replacement_data) if replacement_data else match_text
                    # 存储替换关系
                    replacement_pool[placeholder] = replacement
                    # 用占位符替换
                    marked_text = marked_text[:start] + placeholder + marked_text[end:]

        # 替换所有占位符为实际内容
        final_text = marked_text
        for placeholder, replacement in replacement_pool.items():
            final_text = final_text.replace(placeholder, replacement)

        return final_text


# 示例用法
if __name__ == "__main__":
    # 关键词替换字典（固定不变）
    URL_DICT = {
        "永久": {
            "": ("/rule/rule_basic/rule_effect", "#h-11-永久类效果", "永久类效果"),
            "永久获得以下效果": ("/", "#", "永久获得效果"),
            "永久获得": ("/rule/rule_basic/rule_element", "#h-3-永久元素", "永久元素"),
            "永久不替换": None,
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
    }

    # 创建替换器实例（只需创建一次）
    replacer = KeywordReplacer(URL_DICT)


    # 定义HTML链接格式化函数
    def html_link_formatter(match_text: str, replacement_data: tuple) -> str:
        url, chap, tooltip = replacement_data
        return f'<a href="{url}{chap}" tooltip="{tooltip}">{match_text}</a>'


    # 定义纯文本格式化函数（另一种替换逻辑）
    def text_formatter(match_text: str, replacement_data: tuple) -> str:
        url, chap, tooltip = replacement_data
        return f'[{match_text}({url}{chap}): {tooltip}]'


    # 测试文本1 - 使用HTML格式化
    test_text1 = """
    这个效果是永久的。
    玩家可以永久获得以下效果，同时还能永久获得其他能力。
    这个永久不替换。
    """
    print("HTML替换结果:")
    print(replacer.replace(test_text1, html_link_formatter))

    # 测试文本2 - 使用纯文本格式化
    test_text2 = """
    启动技能需要消耗能量，快速技能则不需要。
    投掷骰子决定结果。
    """
    print("\n纯文本替换结果:")
    print(replacer.replace(test_text2, text_formatter))