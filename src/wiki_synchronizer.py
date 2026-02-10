# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/26 15:33
# @file         : wiki_synchronizer.py
# @Desc         :
# -----------------------------------------

# import from official
import json
from typing import Dict, Optional, List
from pathlib import Path
# import from third-party

# import from self-defined
from com.util import pathUtil
from src.text_formater import TextFormatter

CARD_CONTENTS_REFLECTION = {
    "exploration": {
        "name": "探索区卡牌",
        "description": "探索区的资源卡牌",
        "color": "#3498db",  # 明亮的蓝色 - 代表探索、冒险和未知领域
    },
    "intelligence": {
        "name": "情报区卡牌",
        "description": "情报区的情报和事件卡牌",
        "color": "#9b59b6",  # 紫色 - 代表智慧、神秘和信息
    },
    "trading": {
        "name": "交易区卡牌",
        "description": "交易区的商品卡牌",
        "color": "#f1c40f",  # 金色/黄色 - 代表财富、交易和价值
    },
    "role": {
        "name": "角色专属",
        "description": "角色和角色专属卡牌",
        "color": "#e74c3c",  # 红色 - 代表个性、活力和独特身份
    },
    "accessory": {
        "name": "其他卡牌",
        "description": "其它配件卡牌",
        "color": "#2ecc71",  # 绿色 - 代表补充、辅助和多样性
    },
}


def parse_package_info(path: str) -> str:
    """
    解析卡牌包信息
    :param path:
    :return:
    """
    reflect_dict = {
        "std": "基础包",
        "dlc01": "卡牌扩展包01",
        "dlc02": "卡牌扩展包02",
        "rol01": "角色扩展包01",
        "rol02": "角色扩展包02",
        "rol03": "角色扩展包03",
    }
    for k, v in reflect_dict.items():
        if k in path:
            return v
    raise ValueError(f"未识别的卡包：{path}")


def parse_match_info(path: str) -> str:
    """
    解析竞技环境信息
    :param path:
    :return:
    """
    reflect_dict = {
        # A
        "std01_ac": "A",
        "std01_co": "A",
        "std01_ma": "A",
        # B
        "std02_ac": "B",
        "std02_co": "B",
        "std02_ma": "B",
        # C
        "dlc01_ac": "C",
        "dlc01_co": "C",
        "dlc01_ma": "C",
        # D
        "dlc02_ac": "D",
        "dlc02_co": "D",
        "dlc02_ma": "D",
    }
    env = "∞"
    for k, v in reflect_dict.items():
        if k in path:
            return v
    return env


class WikiSynchronizer:
    def __init__(self, locale: str = "zh", register_file: str = "deck_json_register.json"):
        self.locale = locale
        self.register_file = pathUtil.getSrcDir() / register_file
        self.data_dir = pathUtil.getDataDir()
        self.register_dict: Optional[Dict] = None

        if not self.register_file.exists():
            raise FileNotFoundError(f"{self.register_file} not found")
        with open(self.register_file, 'r', encoding='utf-8') as f:
            self.register_dict = json.load(f)

    @staticmethod
    def init_card_json(path: str):
        saved_info = {
            "path": path,
            "tags": [],
            "stat": {
                "win-rate": None,
                "unlock-rate": None,
                "keep-rate": None,
            },
            "faq": [],
            "revise": [],
            "card": {},
        }
        return saved_info

    def load_card_info(self, target_path: Path, force_sync: bool) -> Dict:
        rel_path = target_path.relative_to(self.data_dir / self.locale)
        info_path = rel_path.as_posix().replace(".json", "")

        if not target_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding='utf-8') as f:
                f.write("{}")

        with open(target_path, "r+", encoding='utf-8') as f:
            saved_info = json.load(f)
            if saved_info is None or saved_info == {} or force_sync:
                saved_info = self.init_card_json(info_path)

        return saved_info

    @staticmethod
    def dispose_card_info(card_json_file: str, idx: int, card_design_info: Dict, saved_info: Dict):
        # ---------------------------------------------------------------------------
        # 处理卡牌图片并更新
        card_json_file_prefix = card_json_file.split(".")[0]
        card_main_picture = card_design_info.get("card_picture_path", "image_in_progress_1.jpg")
        card_main_picture = card_main_picture.split("/")[-1].replace(".png", ".jpg")
        card_index = str(idx+1).zfill(2)
        card_image_url = f"/assets/image/{card_json_file_prefix}_{str(card_index)}.jpg"
        card_thumbnail_url = f"/assets/thumbnail/{card_main_picture}"

        # ---------------------------------------------------------------------------
        card_design_tag = ["卡牌"]

        # # 等级值
        card_level = card_design_info.get("card_level", None)
        if isinstance(card_level, str) and card_level.startswith("_"):      # 修正规则/角色的场景
            card_level = None

        # # 类型列表
        card_type_info = card_design_info.get("card_resource_type", None)
        if isinstance(card_level, str):
            card_design_tag.append(card_level)
        card_types = []
        if isinstance(card_type_info, str):
            card_types = [_each.strip() for _each in card_type_info.split("·")]
            for each in card_types:
                card_design_tag.append(each.strip())

        # # 卡牌标签列表
        tag_keys = ["card_resource_tag_1", "card_resource_tag_2", "card_resource_tag_3"]
        card_tags = [str(card_design_info.get(key)) for key in tag_keys
                     if card_design_info.get(key) not in (None, "")]
        card_design_tag.extend(card_tags)
        card_tag_info = " · ".join(card_tags)

        # # 基础信息
        card_items = [card_level, card_type_info, card_tag_info]
        card_basic_info = " / ".join([str(item) for item in card_items if item not in (None, "")])

        # # 卡牌元素
        element_mappings = {
            "card_element_num_earth": "${eE01}",
            "card_element_num_water": "${eW01}",
            "card_element_num_fire": "${eF01}",
            "card_element_num_air": "${eA01}"
        }
        element_num_mappings = {"低级": 1, "中级": 2, "高级": 4, "传奇": 8}
        card_element_marks = [
            marker for key, marker in element_mappings.items()
            if card_design_info.get(key)
        ]
        card_element_mark_info = "".join(card_element_marks)
        card_element_num = 0
        if len(card_element_marks) > 0:
            card_element_num = element_num_mappings[card_level] if card_level in element_num_mappings else 0
            card_element_tooltip = card_design_info.get("card_element_tooltip", "")
            if card_element_tooltip and card_element_tooltip != "":
                card_element_num = int(card_element_tooltip)

        # 处理卡牌效果并更新
        undisposed_card_info_effect = card_design_info.get("card_info_effect") or ""
        if "角色" in card_types:  # 角色卡牌特殊处理
            undisposed_card_info_effect = undisposed_card_info_effect.replace("特色：", "特色/")
        disposed_card_info_effect = TextFormatter().parse_from_text(undisposed_card_info_effect).to_dict()

        # 事件卡牌特殊处理
        if "事件" in card_types:
            effects = disposed_card_info_effect.get("effects", [])
            for effect in effects:
                effect["name"] = "事件"
                effect["type"] = "启动"
        elif "规则" in card_types:
            effects = disposed_card_info_effect.get("effects", [])
            for effect in effects:
                effect["name"] = "规则"
                effect["type"] = "规则"

        # ---------------------------------------------------------------------------
        # 统一更新
        info = {
            # 卡包信息
            "card_package_info": parse_package_info(saved_info["path"]),
            "card_match_info": parse_match_info(saved_info["path"]),
            # 图片链接
            "card_image_url": card_image_url,
            "card_thumbnail_url": card_thumbnail_url,
            # 基础信息 (显示在卡名下方)
            "card_basic_info": card_basic_info,
            # 元素标记（类型, 数目）
            "card_element_marks": card_element_marks,
            "card_element_mark_num": card_element_num,
            "card_element_mark_info": card_element_mark_info,
            # 卡牌等级 (处理过的)
            "card_level_info": card_level,
            # 卡牌类型
            "card_types": card_types,
            "card_type_info": card_type_info,
            # 标签信息
            "card_tags": card_tags,
            "card_tag_info": card_tag_info,
            **disposed_card_info_effect
        }
        card_design_info.update(info)

        # final update
        saved_info["card"] = card_design_info
        saved_info["tags"] = card_design_tag + [
            tag for tag in saved_info["tags"]
            if tag not in set(card_design_tag)
        ]

    def sync_card(self, design_dir: str = "card_json", force_sync: bool = False):
        """
        同步卡牌的设计资料到Wiki资料
        :param design_dir: 设计文件夹
        :param force_sync: 是否强制同步
        :return:
        """
        locale = self.locale
        locale_dir = self.data_dir / locale
        design_dir = locale_dir / design_dir
        sync_dir = locale_dir / "card"

        for card_json_file, card_infos in self.register_dict.items():
            card_design_path = design_dir / card_json_file
            if not card_design_path.exists():
                raise FileNotFoundError(f"{card_design_path} not found")
            with open(card_design_path, 'r', encoding='utf-8') as f:
                card_design_infos = json.load(f)
            card_design_infos = [each for each in card_design_infos if each.get("card_num") > 0]
            if len(card_design_infos) != len(card_infos):
                raise ValueError(f"{card_design_path} has {len(card_design_infos)} cards, but {len(card_infos)} cards in register file")

            image_idx = 0
            for idx in range(len(card_design_infos)):
                card_register_info = card_infos[idx]
                card_design_info = card_design_infos[idx]
                target_dir = card_register_info["dir"]
                target_filename = card_register_info["file"]
                target_path = sync_dir / target_dir / target_filename

                # load saved info (or init it)
                saved_info = self.load_card_info(target_path, force_sync)

                # --特殊处理-----------------------------------
                card_num = card_design_info.get("card_num", 0)
                self.dispose_card_info(card_json_file, image_idx, card_design_info, saved_info)
                image_idx += card_num
                # -------------------------------------------

                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(saved_info, f, indent=4, ensure_ascii=False)

    def _create_contents_json(self, each_dir):
        """创建并写入contents.json文件，返回数据和bucket"""
        contents_file_name = each_dir / "contents.json"
        contents_json = {
            "template": "card_contents_template.html",
            "children": {}
        }

        # 处理目录中的JSON文件
        bucket = self._process_json_files(each_dir, contents_json)

        # 写入contents.json
        with open(contents_file_name, 'w', encoding='utf-8') as f:
            json.dump(contents_json, f, indent=4, ensure_ascii=False)

        return contents_json, bucket

    @staticmethod
    def _process_json_files(each_dir, contents_json):
        """处理目录中的JSON文件，提取数据并填充到contents_json"""
        bucket = []
        idx = 0

        # 核心修改：筛选+自定义排序JSON文件
        json_files = []
        for each_file in each_dir.iterdir():
            if (each_file.is_file()
                    and each_file.name != "contents.json"
                    and each_file.suffix == ".json"):
                json_files.append(each_file)

        # 自定义排序规则：std优先于dlc
        def sort_key(file_path):
            file_name = file_path.stem.lower()  # 转小写避免大小写干扰
            if "_std" in file_name:
                return 0, file_name
            elif "_dlc" in file_name:
                return 1, file_name
            else:
                return 2, file_name

        # 按自定义规则排序文件列表
        json_files.sort(key=sort_key)

        # 遍历排序后的JSON文件
        for each_file in json_files:
            # 更新contents_json
            contents_json["children"][each_file.stem] = {
                "template": "card_intelligence_template.html",
                "data": each_file.name,
            }

            # 读取并处理JSON数据
            idx += 1
            with open(each_file, 'r', encoding='utf-8') as f:
                each_data = json.load(f)
                bucket.append({
                    "id": idx,
                    "url": "/" + each_data["path"],
                    "match": each_data["card"]["card_match_info"],
                    "name": each_data["card"]["card_name"],
                    "level": each_data["card"]["card_level_info"],
                    "type": each_data["card"]["card_types"],
                    "attribute": each_data["card"]["card_tags"],
                    "image": each_data["card"]["card_thumbnail_url"],
                })

        return bucket

    @staticmethod
    def _create_card_content_data(each_dir, bucket, sync_dir):
        """创建卡牌内容数据结构"""
        content_info = CARD_CONTENTS_REFLECTION[each_dir.name]
        content_path = f"card/{each_dir.name}"

        content_data = {
            "title": content_info["name"],
            "path": content_path,
            "tags": ["目录"],
            "contents": {
                "filename": each_dir.name + ".json",
                "data": bucket
            }
        }

        dir_result = {
            "title": content_info["name"],
            "path": "/" + content_path,
            "description": content_info["description"],
            "color": content_info["color"],
            "itemCount": len(bucket),
        }

        return content_data, dir_result

    @staticmethod
    def _write_card_json(sync_dir, card_content_data):
        """生成并写入最终的card.json文件"""
        card_content_json = {
            "title": "卡牌目录",
            "path": "card",
            "tags": ["目录"],
            "contents": {
                "filename": "card.json",
                "data": card_content_data
            }
        }

        target_file = sync_dir.parent / "card.json"
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(card_content_json, f, indent=4, ensure_ascii=False)

    def sync_contents(self):
        """同步卡牌内容的主函数"""
        sync_dir = self.data_dir / self.locale / "card"
        card_content_data = []

        # 处理每个卡牌目录
        for each_dir in sync_dir.iterdir():
            if each_dir.is_file():
                continue

            # 创建contents.json数据并写入文件
            contents_json, bucket = self._create_contents_json(each_dir)

            # 生成卡牌内容数据
            content_data, dir_result = self._create_card_content_data(each_dir, bucket, sync_dir)

            # 特殊处理角色目录下的卡牌, 在预览目录只上传角色主目录, 不上传角色相关卡
            if each_dir.name == "role":
                content_data["contents"]["data"] = [
                    item for item in content_data["contents"]["data"]
                    if "_ri_" in item["url"]
                ]

            # 写入XXX.json文件
            target_bucket_file = sync_dir / f"{each_dir.name}.json"
            with open(target_bucket_file, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, indent=4, ensure_ascii=False)

            card_content_data.append(dir_result)

        # 生成最终的card.json文件
        self._write_card_json(sync_dir, card_content_data)

    def sync(self, design_dir: str = "card_json", force_sync: bool = False):
        # sync card
        self.sync_card(design_dir, force_sync)

        # sync contents.json
        self.sync_contents()

if __name__ == '__main__':
    ws = WikiSynchronizer()
    ws.sync(force_sync=False)