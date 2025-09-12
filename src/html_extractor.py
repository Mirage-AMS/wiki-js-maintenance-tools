# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/9/1 18:21
# @file         : html_extractor.py
# @Desc         :
# -----------------------------------------

# import from official
from typing import Literal
# import from third-party
from bs4 import BeautifulSoup
import sass
# import from self-defined

def format_css(css_content: str, output_mode: Literal["expanded", "compressed", "nested", "compact"] = "compressed"):
    """
    格式化CSS代码
    :param css_content: CSS代码
    :param output_mode: expanded（格式化） compressed（压缩）、nested（嵌套格式）、compact（紧凑格式）
    :return:
    """
    # quick break
    if not isinstance(css_content, str) or css_content == "":
        return css_content

    try:
        formatted_css = sass.compile(
            string=css_content,
            output_style=output_mode,
        )
        return formatted_css.strip()
    except Exception as e:
        print(f"CSS格式化错误: {e}")
        return css_content


def extract_html_parts(html_content, main_div_identifier=None):
    """
    从完整的HTML内容中提取div、script和style部分
    - script部分保留完整标签
    - css部分只提取内容（不含style标签）

    参数:
        html_content: 完整的HTML字符串
        main_div_identifier: 主要div的标识字典，如{'id': 'main-content'}

    返回:
        包含三个部分的字典: html(div内容), script(带标签的脚本), css(样式内容)
    """
    # 尝试使用lxml解析器，如果失败则回退到html.parser
    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except Exception:
        soup = BeautifulSoup(html_content, 'html5lib')

    # 提取主要div块内容
    if main_div_identifier:
        main_div = soup.find('div', main_div_identifier)
    else:
        main_div = soup.find('div')

    if main_div:
        html_part = main_div.prettify(encoding="utf-8").decode("utf-8")
    else:
        raise ValueError("未找到主div块")

    # 提取script块（保留完整标签）
    script_part = ""
    script_tag = soup.find('script')
    if script_tag:
        script_part = str(script_tag)

    # 提取style块内容（不含标签）
    css_part = ""
    style_tag = soup.find('style')
    if style_tag:
        # 提取并清理CSS内容
        css_content = ''.join(map(str, style_tag.contents)).strip()
        css_part = format_css(css_content)

    # 验证提取结果
    extraction_result = {
        'html': html_part,
        'script': script_part,
        'style': css_part
    }

    # 简单验证提示
    for part, content in extraction_result.items():
        if not content and part != 'html':
            print(f"警告: 未提取到{part}部分内容")

    return extraction_result


# 使用示例
if __name__ == "__main__":
    # 测试用的渲染后HTML
    html_path = r"D:\1_program\git_repository\wiki-js-maintenance-tools\tmp\zh\card\accessory.html"
    with open(html_path, encoding='utf-8') as f:
        rendered_html = f.read()

    # 提取各部分（指定主要div的id）
    parts = extract_html_parts(rendered_html)

    # 输出结果
    print("HTML部分:")
    print(parts['html'])
    print("\nScript部分:")
    print(parts['script'])
    print("\nCSS部分:")
    print(parts['style'])
