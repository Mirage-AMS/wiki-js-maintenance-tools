# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/11/12 16:40
# @file         : wiki_relation_register.py
# @Desc         : 用于在wiki原始数据之间创建互相关
# -----------------------------------------

# import from official
import json
from pathlib import Path

# import from third-party

# import from self-defined
from com.util import pathUtil

class RelationInitializer():
    def __init__(self):
        self.save_path = pathUtil.getSrcDir() / "card_relation_register.json"
        self.node_dict = {}
        self.relation_list = []

    def add_node(self):
        ROLE_LIST = []
        for dlcIdx, total in (("01", 12), ("02", 13)):
            for idx in range(total):
                strIdx = str(idx + 1).zfill(2)
                ROLE_LIST.append(f"card_rol{dlcIdx}_ri_{strIdx}.json")
        CARD_LIST = []
        for dlcIdx, total in (("01", 24), ("02", 26)):
            for idx in range(total):
                strIdx = str(idx + 1).zfill(2)
                CARD_LIST.append(f"card_rol{dlcIdx}_ro_{strIdx}.json")

        node = {"type": "card", "dir": "/card/role"}
        for card in ROLE_LIST:
            self.node_dict[card] = node
        for card in CARD_LIST:
            self.node_dict[card] = node

    def add_relation(self):
        dlcIdx = "01"
        for idx in range(12):
            roleIdx = str(idx + 1).zfill(2)
            for idj in range(2):
                cardIdx = str(idx * 2 + idj + 1).zfill(2)
                relation = {
                    "from": f"card_rol{dlcIdx}_ri_{roleIdx}.json",
                    "to": f"card_rol{dlcIdx}_ro_{cardIdx}.json",
                    "type": "bidirectional"
                }
                self.relation_list.append(relation)

    def run(self):
        self.add_node()
        self.add_relation()
        ret = {
            "nodes": self.node_dict,
            "relations": self.relation_list
        }
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(ret, f, indent=4, ensure_ascii=False)


class RelationConnector():
    def __init__(self,
                 register_path: Path = pathUtil.getSrcDir() / "card_relation_register.json",
                 locale: str = "zh"):
        self.data_dir = pathUtil.getDataDir() / locale
        with open(register_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.node_dict = self.data["nodes"]
        self.relation_list = self.data["relations"]

    def is_node_validated(self, node):
        return True if node in self.node_dict else False

    def connect(self, from_node: str, to_node: str):
        from_node_dir = "." + self.node_dict[from_node]["dir"]
        from_node_type = self.node_dict[from_node]["type"]
        to_node_dir = "." + self.node_dict[to_node]["dir"]
        to_node_type = self.node_dict[to_node]["type"]

        from_node_data_path = self.data_dir / from_node_dir / from_node
        with open(from_node_data_path, 'r', encoding='utf-8') as f:
            from_node_data = json.load(f)

        to_node_data_path = self.data_dir / to_node_dir / to_node
        with open(to_node_data_path, 'r', encoding='utf-8') as f:
            to_node_data = json.load(f)

        # 处理不同类型的节点
        if to_node_type == "card":
            related_cards = from_node_data.get("related_cards", [])
            # 处理过程
            new_card_relation = {
                "path": "/" + to_node_data["path"],
                "card_name": to_node_data["card"]["card_name"],
                "brief_description": to_node_data["card"]["card_basic_info"],
                "card_thumbnail_url": to_node_data["card"]["card_thumbnail_url"],
            }
            if new_card_relation not in related_cards:
                related_cards.append(new_card_relation)
            # 完成处理
            from_node_data["related_cards"] = related_cards
        else:
            raise NotImplementedError

        with open(from_node_data_path, 'w', encoding='utf-8') as f:
            json.dump(from_node_data, f, indent=4, ensure_ascii=False)



    def run(self):
        for relation in self.relation_list:
            from_node = relation["from"]
            to_node = relation["to"]
            connection_type = relation["type"]

            if not self.is_node_validated(from_node):
                raise ValueError(f"from node: {from_node} is invalid.")
            if not self.is_node_validated(to_node):
                raise ValueError(f"to node: {to_node} is invalid.")

            self.connect(from_node, to_node)
            if connection_type == "bidirectional":
                self.connect(to_node, from_node)



if __name__ == "__main__":
    RelationConnector().run()
