"""
FastFeishu 类型系统 - 建造者模式实现

使用 dataclass 和内部 Builder 类来构建飞书单元格类型。

优势：
1. 构建过程和表示分离
2. Builder 作为内部类，无需单独管理
3. 通过 .builder() 方法获取 Builder
4. 所有类型继承 FeiShuCellType，统一使用 .to_json()
5. 符合设计模式最佳实践

使用方式：
    # 使用 Builder
    style = SegmentStyle.builder().bold(True).color("#ff0000").build()
    text = StyledText("文本", style)

    # 使用 Director（预设样式）
    style = StyleDirector.title()

    # 直接实例化（仍然支持）
    style = SegmentStyle(bold=True, foreColor="#ff0000")
"""
from abc import ABC
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union, Literal, Any
from datetime import datetime, date
import re


# ============================================================================
# 基础类
# ============================================================================

class FeiShuCellType(ABC):
    """飞书单元格类型基类，所有类型请参考 fastfeishu.models.type.CellTypeConverter.auto_convert"""
    def to_json(self):
        """转换为JSON格式，子类需要实现"""
        raise NotImplementedError("子类必须实现 to_json 方法")


# ============================================================================
# 样式系统 - 产品类和建造者
# ============================================================================

@dataclass
class SegmentStyle:
    """局部样式配置（产品类）

    注意：推荐通过 SegmentStyle.builder() 构建

    Args:
        bold: 是否加粗
        italic: 是否斜体
        strikeThrough: 是否含有删除线
        underline: 是否含有下划线
        foreColor: 字体颜色，16进制rgb颜色，如 "#ff00ff"
        fontSize: 字体大小，最小9，最大36

    Example:
        # 推荐：使用Builder
        style = SegmentStyle.builder().bold(True).color("#ff0000").build()

        # 或者：直接实例化
        style = SegmentStyle(bold=True, foreColor="#ff0000")
    """

    bold: Optional[bool] = None
    italic: Optional[bool] = None
    strikeThrough: Optional[bool] = None
    underline: Optional[bool] = None
    foreColor: Optional[str] = None
    fontSize: Optional[int] = None

    def __post_init__(self):
        """验证参数"""
        if self.fontSize is not None and (self.fontSize < 9 or self.fontSize > 36):
            raise ValueError("字体大小必须在9-36之间")

    def to_json(self):
        """转换为JSON格式，自动过滤None值"""
        style_dict = asdict(self)
        return {k: v for k, v in style_dict.items() if v is not None}

    @classmethod
    def builder(cls):
        """获取Builder"""
        return cls.Builder()

    class Builder:
        """样式建造者"""

        def __init__(self):
            self._bold: Optional[bool] = None
            self._italic: Optional[bool] = None
            self._strike_through: Optional[bool] = None
            self._underline: Optional[bool] = None
            self._fore_color: Optional[str] = None
            self._font_size: Optional[int] = None

        def bold(self, value: bool = True):
            """设置加粗"""
            self._bold = value
            return self

        def italic(self, value: bool = True):
            """设置斜体"""
            self._italic = value
            return self

        def strike_through(self, value: bool = True):
            """设置删除线"""
            self._strike_through = value
            return self

        def underline(self, value: bool = True):
            """设置下划线"""
            self._underline = value
            return self

        def color(self, color: str):
            """设置颜色

            Args:
                color: 16进制颜色值，如 "#ff0000"
            """
            self._fore_color = color
            return self

        def size(self, size: int):
            """设置字体大小

            Args:
                size: 字体大小，必须在9-36之间
            """
            if size < 9 or size > 36:
                raise ValueError("字体大小必须在9-36之间")
            self._font_size = size
            return self

        def build(self):
            """构建最终的SegmentStyle对象"""
            return SegmentStyle(
                bold=self._bold,
                italic=self._italic,
                strikeThrough=self._strike_through,
                underline=self._underline,
                foreColor=self._fore_color,
                fontSize=self._font_size
            )


class StyleDirector:
    """样式导演类（Director）

    提供预设样式的快捷方法

    Example:
        # 使用预设样式
        title = StyleDirector.title()
        warning = StyleDirector.warning()

        # 基于预设修改
        custom = StyleDirector.title_builder().color("#0066ff").build()
    """

    @staticmethod
    def title():
        """标题样式：黑色、加粗、24号"""
        return SegmentStyle.builder().bold(True).size(24).color("#000000").build()

    @staticmethod
    def subtitle():
        """副标题样式：深灰、加粗、18号"""
        return SegmentStyle.builder().bold(True).size(18).color("#333333").build()

    @staticmethod
    def body():
        """正文样式：灰色、12号"""
        return SegmentStyle.builder().size(12).color("#666666").build()

    @staticmethod
    def warning():
        """警告样式：红色、加粗"""
        return SegmentStyle.builder().bold(True).color("#ff0000").build()

    @staticmethod
    def success():
        """成功样式：绿色、加粗"""
        return SegmentStyle.builder().bold(True).color("#00cc00").build()

    @staticmethod
    def info():
        """信息样式：蓝色"""
        return SegmentStyle.builder().color("#0066ff").build()

    @staticmethod
    def important():
        """重要标记：橙色、加粗斜体、14号"""
        return SegmentStyle.builder().bold(True).italic(True).color("#ff6600").size(14).build()

    @staticmethod
    def highlight():
        """高亮样式：黄色、加粗、16号"""
        return SegmentStyle.builder().bold(True).color("#ffaa00").size(16).build()

    @staticmethod
    def secondary():
        """次要信息：灰色、斜体、10号"""
        return SegmentStyle.builder().italic(True).color("#999999").size(10).build()

    @staticmethod
    def deprecated():
        """废弃标记：灰色、删除线"""
        return SegmentStyle.builder().strike_through(True).color("#999999").build()

    # 提供Builder方法，方便基于预设修改
    @staticmethod
    def title_builder():
        """返回标题样式的Builder，可以继续修改"""
        return SegmentStyle.builder().bold(True).size(24).color("#000000")

    @staticmethod
    def warning_builder():
        """返回警告样式的Builder，可以继续修改"""
        return SegmentStyle.builder().bold(True).color("#ff0000")

    @staticmethod
    def success_builder():
        """返回成功样式的Builder，可以继续修改"""
        return SegmentStyle.builder().bold(True).color("#00cc00")


@dataclass
class TextSegment:
    """文本片段（用于链接和邮箱的分段样式）

    Args:
        text: 文本内容
        segmentStyle: 样式配置（可选）
    """

    text: str
    segmentStyle: Optional[dict] = None

    def to_json(self):
        """转换为JSON格式"""
        result = {"text": self.text}
        if self.segmentStyle:
            result["segmentStyle"] = self.segmentStyle
        return result


# ============================================================================
# 基础数据类型
# ============================================================================

@dataclass
class PlainText(FeiShuCellType):
    """纯文本（字符串）"""

    text: str

    def to_json(self):
        return self.text


@dataclass
class Number(FeiShuCellType):
    """数字"""

    value: Union[int, float]

    def to_json(self):
        return self.value


class DateValue(FeiShuCellType):
    """日期值

    整数部分为自1899年12月30日以来的天数
    小数部分为该时间占24小时的份额

    注意：需要先调用设置单元格样式接口将单元格设置为日期格式

    Example:
        DateValue(44562)  # 2022-01-01

        # 推荐：使用快捷方法
        DateValue.today()
        DateValue.now()
        DateValue.from_date(date.today())
        DateValue.from_string("2024-03-15")
    """

    # 飞书日期基准：1899年12月30日
    BASE_DATE = datetime(1899, 12, 30)

    def __init__(self, value: Union[int, float]):
        self.value = value

    def to_json(self):
        return self.value

    @classmethod
    def from_date(cls, d: date):
        """从Python date对象创建"""
        if isinstance(d, datetime):
            d = d.date()
        days = (d - cls.BASE_DATE.date()).days
        return cls(days)

    @classmethod
    def from_datetime(cls, dt: datetime):
        """从Python datetime对象创建（包含时间）"""
        delta = dt - cls.BASE_DATE
        value = delta.days + delta.seconds / 86400
        return cls(value)

    @classmethod
    def today(cls):
        """获取今天的日期"""
        return cls.from_date(date.today())

    @classmethod
    def now(cls):
        """获取当前日期和时间"""
        return cls.from_datetime(datetime.now())

    @classmethod
    def from_string(cls, date_str: str, format: str = "%Y-%m-%d"):
        """从字符串创建日期"""
        if '%H' in format or '%M' in format or '%S' in format:
            dt = datetime.strptime(date_str, format)
            return cls.from_datetime(dt)
        else:
            d = datetime.strptime(date_str, format).date()
            return cls.from_date(d)


@dataclass
class StyledText(FeiShuCellType):
    """带局部样式的文本

    Args:
        text: 文本内容
        style: 样式配置

    Example:

        # 使用Director
        text = StyledText("标题", StyleDirector.title())
    """

    text: str
    style: SegmentStyle

    def to_json(self):
        result = {"text": self.text, "type": "text"}
        if self.style:
            result["segmentStyle"] = self.style
        return result


# ============================================================================
# 链接相关
# ============================================================================

@dataclass
class NotTextLink(FeiShuCellType):
    """无文本的链接"""

    link: str

    def to_json(self):
        return self.link


@dataclass
class TextLink(FeiShuCellType):
    """带文本的链接"""

    link: str
    text: str = '链接'

    def to_json(self):
        return {
            'type': 'url',
            'link': self.link,
            'text': self.text
        }


@dataclass
class StyledLink(FeiShuCellType):
    """[带分段样式的链接](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-types-supported-by-sheets#1e3a4bbb)

    Note:
        - foreColor字段不生效，固定为蓝色
        - underline字段不生效，固定含有下划线

    Example:
        {
            "text": "文本",

            "link": "http://www.dd.com",

            "type": "url",

            "texts": [
                {
                    "text": "文",

                    "segmentStyle": {
                        "bold": true,
                        "italic": true,
                        "strikeThrough": true,
                        "underline": true,
                        "foreColor": "#ffffff",
                        "fontSize": 20
                    }
                },
                {
                    "text": "本",

                    "segmentStyle": {
                        "bold": true,
                        "italic": false,
                        "strikeThrough": true,
                        "underline": true,
                        "foreColor": "#ffffff",
                        "fontSize": 10
                    }
                }
            ]
        }
    """

    link: str
    text: Optional[str] = None
    segments: Optional[List[TextSegment]] = None

    def to_json(self):
        result = {
            'type': 'url',
            'link': self.link
        }
        if self.text:
            result['text'] = self.text
        if self.segments:
            result['texts'] = [seg.to_json() for seg in self.segments]
        return result


# ============================================================================
# 邮箱相关
# ============================================================================

class Email(FeiShuCellType):
    """邮箱"""

    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def __init__(self, email: str, validate: bool = True):
        if validate and not self.EMAIL_PATTERN.match(email):
            raise ValueError(f"无效的邮箱地址: {email}")
        self.text = email

    def to_json(self):
        return self.text


@dataclass
class StyledEmail(FeiShuCellType):
    """带分段样式的邮箱

    注意：
    - foreColor字段不生效，固定为蓝色
    - underline字段不生效，固定含有下划线
    """

    email: str
    segments: Optional[List[TextSegment]] = None
    validate: bool = True

    def __post_init__(self):
        if self.validate and not Email.EMAIL_PATTERN.match(self.email):
            raise ValueError(f"无效的邮箱地址: {self.email}")

    def to_json(self):
        result = {
            'type': 'url',
            'text': self.email
        }
        if self.segments:
            result['texts'] = [seg.to_json() for seg in self.segments]
        return result


# ============================================================================
# @人和@文档
# ============================================================================

@dataclass
class MentionUser(FeiShuCellType):
    """@人"""

    user_info: str
    text_type: Literal["email", "openId", "unionId"] = "email"
    notify: bool = True
    grant_read_permission: bool = False
    style: Optional[SegmentStyle] = None

    def to_json(self):
        result = {
            "type": "mention",
            "text": self.user_info,
            "textType": self.text_type,
            "notify": self.notify,
            "grantReadPermission": self.grant_read_permission
        }
        if self.style:
            result["segmentStyle"] = self.style.to_json()
        return result


@dataclass
class MentionDoc(FeiShuCellType):
    """@文档"""

    file_token: str
    obj_type: Literal["sheet", "doc", "slide", "bitable", "mindnote"]
    style: Optional[SegmentStyle] = None

    def to_json(self):
        result = {
            "type": "mention",
            "textType": "fileToken",
            "text": self.file_token,
            "objType": self.obj_type
        }
        if self.style:
            result["segmentStyle"] = self.style.to_json()
        return result


# ============================================================================
# 公式和下拉列表
# ============================================================================

@dataclass
class Formula(FeiShuCellType):
    """公式"""

    formula: str

    def to_json(self):
        return {
            'type': 'formula',
            'text': self.formula
        }


@dataclass
class MultipleValue(FeiShuCellType):
    """下拉列表"""

    values: List[Union[bool, str, int, float]]

    def __post_init__(self):
        for val in self.values:
            if isinstance(val, str) and ',' in val:
                raise ValueError(f"下拉列表的字符串值不能包含逗号: {val}")

    def to_json(self):
        return {
            "type": "multipleValue",
            "values": self.values
        }


# ============================================================================
# 富文本 - 使用建造者模式
# ============================================================================

class RichText(FeiShuCellType):
    """富文本类型（产品类）

    支持在一个单元格内混合多种样式的文本

    注意：推荐通过 RichText.builder() 构建

    Example:
        # 推荐：使用Builder
        rich = (RichText.builder()
                .add_plain("状态：")
                .add_bold("成功")
                .build())

        # 或者：直接实例化（不推荐）
        segments = [
            {"text": "Part1", "type": "text"},
            {"text": "Part2", "type": "text", "segmentStyle": {"bold": True}}
        ]
        rich = RichText(segments)
    """

    def __init__(self, segments: List[dict]):
        if not isinstance(segments, list):
            raise ValueError("segments 必须是列表")
        if len(segments) == 0:
            raise ValueError("富文本不能为空")
        self._segments = segments

    def to_json(self):
        """转换为JSON格式

        如果只有一个片段，返回dict；否则返回list
        """
        if len(self._segments) == 1:
            return self._segments[0]
        return self._segments

    def get_segments(self):
        """获取内部片段列表（用于拼接）"""
        return self._segments.copy()

    @classmethod
    def builder(cls):
        """获取Builder"""
        return cls.Builder()

    class Builder:
        """富文本建造者

        Example:
            # 基础用法
            rich = (RichText.builder()
                    .add_plain("状态：")
                    .add_bold("成功")
                    .add_plain("，共")
                    .add_colored("100", "#00cc00")
                    .add_plain("条")
                    .build())

            # 拼接已构建的富文本
            rich1 = RichText.builder().add_plain("Part1").build()
            rich2 = RichText.builder().add_bold("Part2").build()
            combined = (RichText.builder()
                        .append_rich(rich1)
                        .add_plain(" - ")
                        .append_rich(rich2)
                        .build())
        """

        def __init__(self):
            self._segments: List[dict] = []

        def add_text(self, text: str, style: Optional[SegmentStyle] = None):
            """添加带样式的文本片段"""
            segment = {"text": text, "type": "text"}
            if style:
                segment["segmentStyle"] = style.to_json()
            self._segments.append(segment)
            return self

        def add_plain(self, text: str):
            """添加普通文本"""
            return self.add_text(text, None)

        def add_bold(self, text: str):
            """添加加粗文本"""
            return self.add_text(text, SegmentStyle.builder().bold(True).build())

        def add_italic(self, text: str):
            """添加斜体文本"""
            return self.add_text(text, SegmentStyle.builder().italic(True).build())

        def add_colored(self, text: str, color: str):
            """添加彩色文本"""
            return self.add_text(text, SegmentStyle.builder().color(color).build())

        def add_with_style(self, text: str, style: SegmentStyle):
            """使用样式对象添加文本"""
            return self.add_text(text, style)

        # ============= 拼接功能 =============

        def append_rich(self, rich: 'RichText'):
            """拼接一个已构建的 RichText 对象

            Args:
                rich: RichText 对象

            Returns:
                self，支持链式调用

            Example:
                rich1 = RichText.builder().add_plain("Part1").build()
                rich2 = RichText.builder().add_bold("Part2").build()

                combined = (RichText.builder()
                            .append_rich(rich1)
                            .add_plain(" + ")
                            .append_rich(rich2)
                            .build())
            """
            if not isinstance(rich, RichText):
                raise ValueError("参数必须是 RichText 实例")
            self._segments.extend(rich.get_segments())
            return self

        def append_builder(self, builder: 'RichText.Builder'):
            """拼接另一个Builder的内容

            Args:
                builder: 另一个 RichText.Builder 实例

            Returns:
                self，支持链式调用

            Example:
                builder1 = RichText.builder().add_plain("Part1")
                builder2 = RichText.builder().add_bold("Part2")

                combined = (RichText.builder()
                            .append_builder(builder1)
                            .add_plain(" + ")
                            .append_builder(builder2)
                            .build())
            """
            if not isinstance(builder, RichText.Builder):
                raise ValueError("参数必须是 RichText.Builder 实例")
            self._segments.extend(builder._segments)
            return self

        def extend_segments(self, segments: List[dict]):
            """批量添加文本片段

            Args:
                segments: 片段列表，每个片段是一个字典

            Returns:
                self，支持链式调用

            Example:
                segments = [
                    {"text": "Part1", "type": "text"},
                    {"text": "Part2", "type": "text", "segmentStyle": {"bold": True}}
                ]
                rich = RichText.builder().extend_segments(segments).build()
            """
            if not isinstance(segments, list):
                raise ValueError("参数必须是列表")
            self._segments.extend(segments)
            return self

        def build(self):
            """构建最终的 RichText 对象"""
            if len(self._segments) == 0:
                raise ValueError("富文本不能为空")
            return RichText(self._segments.copy())


# ============================================================================
# 批量转换工具
# ============================================================================

class CellTypeConverter:
    """批量转换工具

    自动识别数据类型并转换为对应的飞书单元格类型

    提供两种转换方式：
    1. 转换为 FeiShuCellType 对象（可进一步操作）
    2. 转换为 JSON 格式（直接用于API调用）

    使用示例：
    # 方式1: 直接获取 JSON（适合直接调用 API）
    json_data = CellConverter.auto_convert("test@example.com")
    # 返回: "test@example.com"

    # 方式2: 获取 FeiShuCellType 对象（更灵活）
    email_obj = CellConverter.auto_convert_to_type("test@example.com")
    # 返回: Email 对象，可以进一步操作

    # 批量转换为对象
    data = ["text", 123, "https://example.com"]
    objects = CellConverter.from_list_to_type(data)
    # 返回: [PlainText, Number, NotTextLink] 对象列表

    # 批量转换为 JSON
    json_list = CellConverter.from_list(data)
    # 返回: ["text", 123, "https://example.com"] JSON 列表
    """

    @staticmethod
    def auto_convert(item: any, validate_email: bool = True) -> FeiShuCellType | Any | None:
        """自动识别并转换单个数据为 FeiShuCellType 对象

        Args:
            item: 要转换的数据
            validate_email: 是否验证邮箱格式

        Returns:
            FeiShuCellType: 对应的飞书单元格类型对象

        Example:
            # 转换为对象，可以进一步操作
            cell = CellTypeConverter.auto_convert_to_type("test@example.com")
            # cell 是 Email 对象

            # 转换后再修改
            number = CellTypeConverter.auto_convert_to_type(100)
            json_data = number.to_json()  # 手动转 JSON
        """
        if item is None:
            return None

        # 如果已经是 FeiShuCellType，直接返回
        if isinstance(item, FeiShuCellType):
            return item

        # 数字（注意排除布尔类型）
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            return item

        # 布尔值
        if isinstance(item, bool):
            return PlainText(str(item))

        # 字符串类型处理
        if isinstance(item, str):
            # 邮箱检测
            if '@' in item and '.' in item and Email.EMAIL_PATTERN.match(item):
                try:
                    return Email(item, validate=validate_email)
                except ValueError:
                    raise ValueError(f"<{item}> 是一个非法的邮箱格式，请检查后再转换")

            # 链接检测
            if item.startswith(('http://', 'https://', 'ftp://')):
                return NotTextLink(item)

            # 公式检测
            if item.startswith('='):
                return Formula(item)

            # 普通文本
            return item

        # 日期类型（注意要在 datetime 之前检测）
        if isinstance(item, datetime):
            return DateValue.from_datetime(item)

        if isinstance(item, date):
            return DateValue.from_date(item)

        # 列表转下拉列表
        if isinstance(item, list):
            try:
                return MultipleValue(item)
            except ValueError:
                raise ValueError(f"{item} 数组在转化为下拉列表时失败，请检查数据")

        # 如果是 dict 并且是图片类型
        if isinstance(item, dict) and item.get('type') == 'embed-image':
            return FeiShuCellImage(**item)

        # 其他类型
        return item

    @staticmethod
    def auto_convert_to_json(item: any, validate_email: bool = True):
        """自动识别并转换单个数据为 JSON 格式

        Args:
            item: 要转换的数据
            validate_email: 是否验证邮箱格式

        Returns:
            转换后的 JSON 数据

        Example:
            # 直接转换为 JSON
            json_data = CellTypeConverter.auto_convert("test@example.com")
        """
        cell_type = CellTypeConverter.auto_convert(item, validate_email)
        return cell_type.to_json()

    @staticmethod
    def from_list(data: List[any], validate_email: bool = True) -> List[FeiShuCellType]:
        """批量转换一维列表为 FeiShuCellType 对象列表

        Args:
            data: 要转换的一维列表
            validate_email: 是否验证邮箱格式

        Returns:
            FeiShuCellType 对象列表
        """
        return [CellTypeConverter.auto_convert(item, validate_email) for item in data]

    @staticmethod
    def from_list_to_json(data: List[any], validate_email: bool = True):
        """批量转换一维列表为 JSON 格式

        Args:
            data: 要转换的一维列表
            validate_email: 是否验证邮箱格式

        Returns:
            JSON 数据列表
        """
        return [CellTypeConverter.auto_convert_to_json(item, validate_email) for item in data]

    @staticmethod
    def from_table(table_data: List[List[any]], validate_email: bool = True) -> List[List[FeiShuCellType]]:
        """批量转换二维表格数据为 FeiShuCellType 对象二维列表

        Args:
            table_data: 要转换的二维表格数据
            validate_email: 是否验证邮箱格式

        Returns:
            FeiShuCellType 对象二维列表
        """
        return [
            CellTypeConverter.from_list_to_type(row, validate_email)
            for row in table_data
        ]

    @staticmethod
    def from_table_to_json(table_data: List[List[any]], validate_email: bool = True):
        """批量转换二维表格数据为 JSON 格式

        Args:
            table_data: 要转换的二维表格数据
            validate_email: 是否验证邮箱格式

        Returns:
            JSON 数据二维列表
        """
        return [
            CellTypeConverter.from_list(row, validate_email)
            for row in table_data
        ]

    @staticmethod
    def from_dict(data: dict, validate_email: bool = True) -> dict:
        """转换字典数据为包含 FeiShuCellType 对象的字典

        Args:
            data: 要转换的字典
            validate_email: 是否验证邮箱格式

        Returns:
            包含 FeiShuCellType 对象的字典
        """
        return {
            key: CellTypeConverter.auto_convert(value, validate_email)
            for key, value in data.items()
        }

    @staticmethod
    def from_dict_to_json(data: dict, validate_email: bool = True):
        """转换字典数据为 JSON 格式

        Args:
            data: 要转换的字典
            validate_email: 是否验证邮箱格式

        Returns:
            JSON 数据字典
        """
        return {
            key: CellTypeConverter.auto_convert_to_json(value, validate_email)
            for key, value in data.items()
        }

@dataclass
class FeiShuCellImage(FeiShuCellType):
    """使用 read_images 方法读取后的返回值"""

    fileToken: str
    link: str
    width: int
    height: int
    type: str
    text: str = ''  # 占位，一直为空

    def to_json(self):
        """将对象转换为字典，方便 json.dumps 序列化"""
        return {
            'fileToken': self.fileToken,
            'link': self.link,
            'width': self.width,
            'height': self.height,
            'type': self.type,
            'text': self.text
        }
