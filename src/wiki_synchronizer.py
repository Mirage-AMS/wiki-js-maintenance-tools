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
# import from third-party

# import from self-defined
from com.util import pathUtil
from src.text_formater import TextFormatter


class WikiSynchronizer:
    def __init__(self, register_file: str = "deck_json_register.json"):
        self.register_file = pathUtil.getSrcDir() / register_file
        self.data_dir = pathUtil.getDataDir()
        self.register_dict: Optional[Dict] = None

        if not self.register_file.exists():
            raise FileNotFoundError(f"{self.register_file} not found")
        with open(self.register_file, 'r', encoding='utf-8') as f:
            self.register_dict = json.load(f)

    @staticmethod
    def init_card_json(path: str):
        return {
            "path": path,
            "data": {}
        }

    def sync(self, locale: str = "zh", design_dir: str = "card_json", force_sync: bool = False):
        """
        同步卡牌的设计资料到Wiki资料
        :param locale: 语言
        :param design_dir: 设计文件夹
        :param force_sync: 是否强制同步
        :return:
        """
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
                card_info = card_infos[idx]
                card_design_info = card_design_infos[idx]

                # --特殊处理-----------------------------------
                undisposed_card_info_effect = card_design_info.get("card_info_effect") or ""
                disposed_card_info_effect = TextFormatter().parse_from_text(undisposed_card_info_effect).to_dict()
                card_design_info.update(disposed_card_info_effect)
                # -------------------------------------------
                target_dir = card_info["dir"]
                target_filename = card_info["file"]
                target_path = sync_dir / target_dir / target_filename
                rel_path = target_path.relative_to(locale_dir)
                print(target_path)
                with open(target_path, "r+", encoding='utf-8') as f:
                    saved_info = json.load(f)
                    if saved_info is None or saved_info == {} or force_sync:
                        save_path = rel_path.as_posix().replace(".json", "")
                        saved_info = self.init_card_json(save_path)

                saved_info["data"] = card_design_info

                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(saved_info, f, indent=4, ensure_ascii=False)

        self.sync_content(locale)

    def sync_content(self, locale: str = "zh"):
        sync_dir = self.data_dir / locale / "card"

        for each_dir in sync_dir.iterdir():
            if each_dir.is_file():
                continue
            content_file_name = each_dir / f"content.json"
            content = {"children": {}}
            for each_file in each_dir.iterdir():
                if not each_file.is_file():
                    continue
                if each_file.name == "content.json":
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