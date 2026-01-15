# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2026/1/15 10:23
# @file         : export_wiki_note.py
# @Desc         :
# -----------------------------------------

# import from official
import json
from pathlib import Path
# import from third-party
# import from self-defined
from com.util import pathUtil


# 数据根目录
ROOT_DATA_PATH: Path = pathUtil.getDataDir()  / 'zh' / 'card'
EXPORT_DIR: Path = pathUtil.getTmpDir() / 'zh' / "export"

def backup_wiki_note(export_dir: Path):
    record_dict = {}
    backup_json_path = EXPORT_DIR / "wiki_note.json"
    if backup_json_path.exists():
        with open(backup_json_path, encoding="utf-8") as f:
            content = f.read()
            record_dict = json.loads(content)

    for p in export_dir.rglob("*.json"):
        if "std" not in p.name:
            continue
        if p.name == "contents":
            continue
        with open(p, encoding="utf-8") as f:
            content = f.read()
            info = json.loads(content)
            card_name = info["card"]["card_name"]
            wiki_note = {
                "stat": info["stat"],
                "faq": info["faq"],
                "revise": info["revise"],
            }
            record_dict[card_name] = wiki_note

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(backup_json_path, mode="w+", encoding="utf-8") as f:
        json.dump(record_dict, f, indent=4, ensure_ascii=False)


def writeback_wiki_note(writeback_dir: Path):
    record_dict = {}
    backup_json_path = EXPORT_DIR / "wiki_note.json"
    if backup_json_path.exists():
        with open(backup_json_path, encoding="utf-8") as f:
            content = f.read()
            record_dict = json.loads(content)

    for p in writeback_dir.rglob("*.json"):
        if "std" not in p.name:
            continue
        if p.name == "contents":
            continue
        with open(p, encoding="utf-8") as f:
            content = f.read()
            info = json.loads(content)
            card_name = info["card"]["card_name"]

        if card_name in record_dict:
            info["stat"] = record_dict[card_name]["stat"]
            info["faq"] = record_dict[card_name]["faq"]
            info["revise"] = record_dict[card_name]["revise"]
            with open(p, mode="w+", encoding="utf-8") as wf:
                json.dump(info, wf, indent=4, ensure_ascii=False)
        else:
            raise ValueError(f"{card_name} not found in wiki_note.json")

if __name__ == "__main__":
    intl = ROOT_DATA_PATH / "intelligence"
    trad = ROOT_DATA_PATH / "trading"
    writeback_wiki_note(intl)
    writeback_wiki_note(trad)