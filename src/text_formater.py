import re
from enum import Enum, unique
from typing import Dict, List, Any, Optional, Tuple


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
        return {
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'consumption': self.consumption,
            'text': self.text,
        }

class KeywordFormatter:
    def __init__(self):
        self.is_match: bool = False
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
                self.is_match = True
                self.keyword = keyword_reflection[key]
                self.text = value

        return self

    def to_dict(self) -> Optional[Dict]:
        ret = None
        if self.is_match:
            ret = {self.keyword: self.text}
        return ret

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

            # 处理A:B结构, 如果无法匹配则按照效果匹配
            keyword_result = KeywordFormatter().parse_from_lines(lines).to_dict()
            if keyword_result:
                result.update(keyword_result)
            else:
                effects.append(EffectFormatter().parse_from_lines(lines).to_dict())
        if effects:
            result['effects'] = effects
        return result

# 测试代码
if __name__ == "__main__":
    test_text = """
    <n02>单行文字内容
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

    test_text = "<n02> \n<n00>弃置1张手牌，选情报区弃牌堆1张情报卡牌获得\n<n00> \n<n00> <n00> <n24> "

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