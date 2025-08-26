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


class WikiSynchronizer:
    def __init__(self, register_file: str = "deck_json_register.json"):
        self.register_file = pathUtil.getSrcDir() / register_file
        self.data_dir = pathUtil.getDataDir()
        self.register_dict: Optional[Dict] = None

        if not self.register_file.exists():
            raise FileNotFoundError(f"{self.register_file} not found")
        with open(self.register_file, 'r', encoding='utf-8') as f:
            self.register_dict = json.load(f)


    def sync(self, locale: str = "zh", card_json_dir: str = "card_json"):
        locale_dir = self.data_dir / locale
        card_json_dir = locale_dir / card_json_dir
        sync_dir = locale_dir / "card"

        for card_json_file, card_infos in self.register_dict.items():
            card_json_path = card_json_dir / card_json_file
            if not card_json_path.exists():
                raise FileNotFoundError(f"{card_json_path} not found")
            with open(card_json_path, 'r', encoding='utf-8') as f:
                card_json = json.load(f)
            if len(card_json) != len(card_infos):
                raise ValueError(f"{card_json_path} has {len(card_json)} cards, but {len(card_infos)} cards in register file")
            for idx in range(len(card_json)):
                card_info = card_infos[idx]
                target_dir = card_info["dir"]
                target_filename = card_info["file"]
                target_path = sync_dir / target_dir / target_filename
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)

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
    ws.sync()