import re
from enum import Enum, unique
from typing import Dict, List, Any, Optional, Tuple


@unique
class EnumElementMark(str, Enum):
    ELEMENT_EARTH = "${eE01}"
    ELEMENT_WATER = "${ew01}"
    ELEMENT_FIRE = "${eF01}"
    ELEMENT_AIR = "${eA01}"
    ELEMENT_COMMON = "${eC01}"
    ELEMENT_ARBITRARY_01 = "${eR01}"
    ELEMENT_ARBITRARY_02 = "${eR02}"
    ELEMENT_ARBITRARY_03 = "${eR03}"
    ELEMENT_ARBITRARY_04 = "${eR04}"
    ELEMENT_ARBITRARY_05 = "${eR05}"
    ELEMENT_ARBITRARY_06 = "${eR06}"
    ELEMENT_ARBITRARY_07 = "${eR07}"
    ELEMENT_ARBITRARY_08 = "${eR08}"
    ELEMENT_ARBITRARY_09 = "${eR09}"
    ELEMENT_ARBITRARY_10 = "${eR10}"

@unique
class EnumEffectType(str, Enum):
    EFFECT_TYPE_PERMANENT = "永久"
    EFFECT_TYPE_LAUNCH = "启动"
    EFFECT_TYPE_QUICK = "快速"
    EFFECT_TYPE_UNKNOWN = "未知"

@unique
class EnumEffectLocation(str, Enum):
    EFFECT_LOCATION_ABILITY_ZONE = "晋升区"
    EFFECT_LOCATION_BACKPACK = "背包"
    EFFECT_LOCATION_MATERIAL = "素材"

@unique
class EnumIntelKeyword(str, Enum):
    KEYWORD_INTEL_UNLOCK = "解锁"
    KEYWORD_INTEL_MASTER = "精通"

class EffectFormatter:
    def __init__(self):
        self.name: str = ""
        self.type: str = ""
        self.location: str = ""
        self.consumption: str = ""
        self.text: str = ""

    @staticmethod
    def _check_effect_location(a_part: str) -> tuple[str, Optional[str]]:
        """
        分离a_part和self.location，处理形如a_part(self.location)的格式
        参数:
            a_part: 可能包含(self.location)的a部分字符串
        返回:
            元组 (a_main, self.location)，其中self.location可能为None
        """
        # 匹配中英文括号中的内容
        pattern = re.compile(r'^(.+?)\s*[(\uff08](.*?)[)\uff09]\s*$')
        match = pattern.match(a_part)

        if match:
            return match.group(1).strip(), match.group(2).strip()
        else:
            return a_part.strip(), None

    def get_color_by_type(self) -> Tuple[str, str]:
        if self.type == EnumEffectType.EFFECT_TYPE_PERMANENT:
            return "e0e7ff", "3b82f6"  # 永久效果：靛蓝色系（稳定感）
        elif self.type == EnumEffectType.EFFECT_TYPE_LAUNCH:
            return "dbeafe", "1e40af"  # 启动效果：蓝色系（主色调，醒目）
        elif self.type == EnumEffectType.EFFECT_TYPE_QUICK:
            return "fee2e2", "dc2626"  # 快速效果：红色系（迅捷、紧急感）
        elif self.type == EnumEffectType.EFFECT_TYPE_UNKNOWN:
            return "f3f4f6", "6b7280"  # 未知效果：灰色系（中性、不确定）
        else:
            raise ValueError(f"Invalid effect type {self.type}")

    def parse_from_lines(self, lines: List[str]) -> 'EffectFormatter':
        first_line = lines[0]
        
        # 按 '/' 分割并去除每个部分的空白
        parts = [part.strip() for part in first_line.split('/') if part.strip()]

        # 先处理公共的文本内容（根据不同情况调整lines的切片）
        text_lines = lines[1:] if len(parts) in (2, 3) else lines
        self.text = '\n'.join(text_lines).strip()

        # 初始化默认值
        self.type = EnumEffectType.EFFECT_TYPE_UNKNOWN
        self.consumption = None
        self.name = "未知"

        # 根据parts长度进行赋值
        if len(parts) == 2:
            self.type, self.name = parts
        elif len(parts) == 3:
            self.type, self.consumption, self.name = parts

        # 最后统一处理位置检查（无论哪种情况都需要执行）
        self.type, self.location = self._check_effect_location(self.type)

        return self

    def to_dict(self) -> Dict:
        type_color, type_text_color = self.get_color_by_type()
        return {
            'name': self.name,
            'type': self.type,
            'type_color': type_color,
            'type_text_color': type_text_color,
            'location': self.location,
            'consumption': self.consumption,
            'text': self.text,
        }

class KeywordFormatter:
    def __init__(self):
        self.keyword: str = ""
        self.text: str = ""

    def parse_from_lines(self, lines: List[str]) -> 'KeywordFormatter':
        colon_pattern = re.compile(r'[:：]')
        keyword_reflection = {
            EnumIntelKeyword.KEYWORD_INTEL_UNLOCK: "unlock",
            EnumIntelKeyword.KEYWORD_INTEL_MASTER: "master"
        }
        # 检查是否包含任何类型的冒号
        if colon_pattern.search(lines[0]):
            # 使用冒号分割，只分割第一个冒号
            parts = colon_pattern.split(lines[0], 1)
            key = parts[0].strip()
            value = parts[1].strip()
            if key in keyword_reflection:
                self.keyword = keyword_reflection[key]
                self.text = value
            else:
                raise ValueError(f"Invalid keyword {key}")

        return self

    def to_dict(self) -> Dict:
        return {
            self.keyword: self.text
        }

class TextFormatter:
    def __init__(self):
        self.blocks: List[str] = []

    def parse_from_text(self, text: str):
        pattern = r'<[bn]\d+>'
        parts = re.split(pattern, text)
        tags = re.findall(pattern, text)
        current_block = []
        for tag, content in zip(tags, parts[1:]):
            content_stripped = content.strip()
            if not content_stripped:
                continue
            if tag.startswith('<b'):
                if current_block:
                    self.blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(content_stripped)
            else:
                current_block.append(content_stripped)

        if current_block:
            self.blocks.append('\n'.join(current_block))

        return self

    def to_dict(self) -> Dict:
        result = {}
        effects = []
        for current_block in self.blocks:
            lines = [line.strip() for line in current_block.split('\n') if line.strip()]
            line_count = len(lines)

            # 处理单行块，支持英文冒号和中文冒号
            if line_count == 1:
                result.update(KeywordFormatter().parse_from_lines(lines).to_dict())
            # 处理多行块
            else:
                effects.append(EffectFormatter().parse_from_lines(lines).to_dict())
        if effects:
            result['effects'] = effects
        return result

# 测试代码
if __name__ == "__main__":
    test_text = """
    <b00>解锁：${eE01}${eR01}
    <b00>启动 / ${eE01} / 祈愿
    <n02>${tR01}：选以下1个效果发动，
    <n02>· 为1个植物累积2点采集进度
    <n02>· 弃置你已解锁造物的1个素材，将其对应弃牌堆返回牌堆洗切
    <n20>
    <b00>精通：${mS03}
    <b00>快速（背包） / 重击
    <n02>对目标造成3点伤害
    <n02>· 若目标已被标记，额外造成2点伤害
    """

    # test_text = "<n02> \n<n02>直到本轮结束前其他玩家需要消耗的元素翻倍；其他玩家可以在各自回合中选以下1个可适用的效果适用，以终止对其影响\n<n02><探究> · 本回合不能进入探索区\n<n02><破立> · 立即受到3点伤害\n<n16> "

    # 先分割为块
    f = TextFormatter().parse_from_text(test_text)
    print("块分割结果：")
    for i, block in enumerate(f.blocks, 1):
        print(f"块{i}：")
        print(block)
        print()

    # 解析块内容
    import json
    print(json.dumps(f.to_dict(), indent=2, ensure_ascii=False))