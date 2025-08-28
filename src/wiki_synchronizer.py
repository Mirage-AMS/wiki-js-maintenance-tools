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
from typing import Dict, Optional
from pathlib import Path
# import from third-party

# import from self-defined
from com.util import pathUtil
from src.text_formater import TextFormatter


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
        card_index = str(idx+1).zfill(2)
        card_image_url = f"/image/{card_json_file_prefix}_{str(card_index)}.jpg"

        # ---------------------------------------------------------------------------
        card_design_tag = ["卡牌"]
        # 处理卡牌元素
        element_mappings = {
            "card_element_num_earth": "${eE01}",
            "card_element_num_water": "${eW01}",
            "card_element_num_fire": "${eF01}",
            "card_element_num_air": "${eA01}"
        }
        card_element_list = [
            marker for key, marker in element_mappings.items()
            if card_design_info.get(key)
        ]
        card_element_mark = "".join(card_element_list)

        # 处理卡牌标签
        tag_keys = ["card_resource_tag_1", "card_resource_tag_2", "card_resource_tag_3"]
        card_tags = [str(card_design_info.get(key)) for key in tag_keys
                     if card_design_info.get(key) not in (None, "")]
        card_design_tag.extend(card_tags)
        card_tag = " · ".join(card_tags)

        # 处理属性标签
        card_level = card_design_info.get("card_level", None)
        card_resource_type = card_design_info.get("card_resource_type", None)
        if card_level is not None:
            card_design_tag.append(card_level)
        if card_resource_type is not None:
            card_design_tag.append(card_resource_type)
        card_items = [card_level, card_resource_type, card_tag]
        card_attribute = " / ".join([str(item) for item in card_items if item not in (None, "")])

        # 处理卡牌效果并更新
        undisposed_card_info_effect = card_design_info.get("card_info_effect") or ""
        disposed_card_info_effect = TextFormatter().parse_from_text(undisposed_card_info_effect).to_dict()

        # ---------------------------------------------------------------------------
        # 统一更新
        info = {
            "card_element_mark": card_element_mark,
            "card_image_url": card_image_url,
            "card_attribute": card_attribute,
            "card_tag": card_tag,
            **disposed_card_info_effect
        }
        card_design_info.update(info)

        # final update
        saved_info["card"] = card_design_info
        saved_info["tags"] = list(set(saved_info["tags"]).union(set(card_design_tag)))

    def sync(self, design_dir: str = "card_json", force_sync: bool = False):
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
            if len(card_design_infos) != len(card_infos):
                raise ValueError(f"{card_design_path} has {len(card_design_infos)} cards, but {len(card_infos)} cards in register file")
            for idx in range(len(card_design_infos)):
                card_register_info = card_infos[idx]
                target_dir = card_register_info["dir"]
                target_filename = card_register_info["file"]
                target_path = sync_dir / target_dir / target_filename

                # load saved info (or init it)
                saved_info = self.load_card_info(target_path, force_sync)

                # --特殊处理-----------------------------------
                self.dispose_card_info(card_json_file, idx, card_design_infos[idx], saved_info)
                # -------------------------------------------

                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(saved_info, f, indent=4, ensure_ascii=False)

        # sync contents.json
        self.sync_content()

    def sync_content(self):
        sync_dir = self.data_dir / self.locale / "card"

        for each_dir in sync_dir.iterdir():
            if each_dir.is_file():
                continue
            content_file_name = each_dir / f"contents.json"
            content = {"children": {}}
            for each_file in each_dir.iterdir():
                if not each_file.is_file():
                    continue
                if each_file.name == "contents.json":
                    continue
                if each_file.suffix != ".json":
                    continue
                content["children"][each_file.stem] = {
                    "data": each_file.name
                }

            with open(content_file_name, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)



if __name__ == '__main__':
    ws = WikiSynchronizer()
    ws.sync(force_sync=True)