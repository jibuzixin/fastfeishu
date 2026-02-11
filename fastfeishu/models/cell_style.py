from dataclasses import dataclass, field, asdict
from typing import Optional, Literal


@dataclass
class Font:
    """
    字体样式配置

    Attributes:
        bold: 是否加粗，默认 false
        italic: 是否斜体，默认 false
        fontSize: 字体大小，格式如 "10pt/1.5"。其中 10pt 表示字号（取值范围 [9,36]pt），1.5 为行距（固定 1.5px）
        clean: 是否清除字体格式，默认 false
    """
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    fontSize: Optional[str] = None  # 格式: "10pt/1.5"，字号范围 [9,36]pt
    clean: Optional[bool] = None

    def to_dict(self):
        """过滤掉未设置的值，只转化有值的属性为 Dict"""
        font_dict = asdict(self)
        return {k: v for k, v in font_dict.items() if v is not None}

    @classmethod
    def builder(cls):
        return Font.Builder()

    class Builder:
        def __init__(self):
            self.font = Font()

        def bold(self, bold: bool = True):
            """设置粗体"""
            self.font.bold = bold
            return self

        def italic(self, italic: bool = True):
            """设置斜体"""
            self.font.italic = italic
            return self

        def font_size(self, size: str):
            """
            设置字体大小

            Args:
                size: 字体大小，格式如 "10pt/1.5" 或 "12pt/1.2"
                      其中 10pt 表示字号（取值范围 [9,36]pt），1.5 为行距（固定 1.5px）

            Example:
                >>> Font.builder().font_size("14pt/1.5").build()
            """
            self.font.fontSize = size
            return self

        def clean(self, clean: bool = True):
            """是否清除字体样式"""
            self.font.clean = clean
            return self

        def build(self):
            return self.font


@dataclass
class CellStyle:
    """
    单元格样式配置

    支持设置字体、对齐、边框、颜色等多种样式属性。使用建造者模式创建样式对象。

    Attributes:
        font: 字体样式配置，Font 对象
        textDecoration: 文本装饰样式
            - 0: 默认样式，不加下划线和删除线
            - 1: 下划线
            - 2: 删除线
            - 3: 下划线和删除线
        formatter: 数字格式，支持的格式类型：
            - "@": 纯文本 (text)
            - "0": 数字 (1024)
            - "#,##0": 数字(千分位) (1,024)
            - "#,##0.00": 数字(千分位 小数点) (1,024.56)
            - "0%": 百分比 (10%)
            - "0.00%": 百分比(小数点) (10.24%)
            - "0.00E+00": 科学计数 (1.02E+03)
            - "¥#,##0": 人民币 (¥1,024)
            - "¥#,##0.00": 人民币(小数点) (¥1,024.56)
            - "$#,##0": 美元 ($1,024)
            - "$#,##0.00": 美元(小数点) ($1,024.56)
            - "yyyy/MM/dd": 日期 (2017/08/10)
            - "yyyy-MM-dd": 日期 (2017-08-10)
            - "HH:mm:ss": 时间 (23:24:25)
            - "yyyy/MM/dd HH:mm:ss": 日期时间 (2017/08/10 23:24:25)
        hAlign: 水平对齐方式
            - 0: 左对齐
            - 1: 中对齐
            - 2: 右对齐
        vAlign: 垂直对齐方式
            - 0: 上对齐
            - 1: 中对齐
            - 2: 下对齐
        foreColor: 前景色（字体颜色），十六进制颜色代码，如 "#000000"
        backColor: 背景色，十六进制颜色代码，如 "#21d11f"
        borderType: 边框类型
            - FULL_BORDER: 全边框，即四周都有边框
            - OUTER_BORDER: 外边框，只有外侧有边框
            - INNER_BORDER: 内边框，只有内部有边框
            - NO_BORDER: 无边框
            - LEFT_BORDER: 左边框，只有左侧有边框
            - RIGHT_BORDER: 右边框，只有右侧有边框
            - TOP_BORDER: 上边框，只有顶部有边框
            - BOTTOM_BORDER: 下边框，只有底部有边框
        borderColor: 边框颜色，十六进制颜色代码，如 "#ff0000"
        clean: 是否清除所有格式，默认 false

    Examples:
        >>> # 使用建造者模式创建样式
        >>> style = CellStyle.builder() \\
        ...     .font(Font.builder().bold().italic().font_size("12pt/1.5").build()) \\
        ...     .fore_color("#000000") \\
        ...     .back_color("#21d11f") \\
        ...     .text_decoration(1) \\
        ...     .h_align(1) \\
        ...     .v_align(1) \\
        ...     .border_type("FULL_BORDER") \\
        ...     .border_color("#ff0000") \\
        ...     .build()

        >>> # 转换为字典用于 API 调用
        >>> style_dict = style.to_dict()
    """
    font: Optional[Font] = None
    textDecoration: Optional[int] = None  # 0: 无, 1: 下划线, 2: 删除线, 3: 下划线和删除线
    formatter: Optional[str] = None
    hAlign: Optional[int] = None  # 0: 左对齐, 1: 居中, 2: 右对齐
    vAlign: Optional[int] = None  # 0: 顶部对齐, 1: 居中, 2: 底部对齐
    foreColor: Optional[str] = None  # 前景色（字体颜色），格式如 "#000000"
    backColor: Optional[str] = None  # 背景色，格式如 "#21d11f"
    borderType: Optional[str] = None  # 边框类型: "FULL_BORDER", "NO_BORDER" 等
    borderColor: Optional[str] = None  # 边框颜色，格式如 "#ff0000"
    clean: Optional[bool] = None  # 是否清除所有样式

    def to_dict(self):
        """
        将 CellStyle 对象转换为字典格式，用于 API 调用

        过滤掉未设置的值（None），仅保留有效的样式属性

        Returns:
            dict: 包含所有非 None 样式属性的字典
        """
        style_dict = asdict(self)
        result = {k: v for k, v in style_dict.items() if v is not None}

        # 如果有字体设置，递归处理
        if self.font:
            result['font'] = self.font.to_dict()

        return result

    @classmethod
    def builder(cls):
        return CellStyle.Builder()

    class Builder:
        def __init__(self):
            self.style = CellStyle()

        def font(self, font: Font):
            """设置字体样式"""
            self.style.font = font
            return self

        def text_decoration(self, decoration: Literal[0, 1, 2, 3]):
            """
            设置文本装饰

            Args:
                decoration:
                    - 0: 默认样式，不加下划线和删除线
                    - 1: 下划线
                    - 2: 删除线
                    - 3: 下划线和删除线

            Example:
                >>> CellStyle.builder().text_decoration(1).build()  # 添加下划线
            """
            self.style.textDecoration = decoration
            return self

        def formatter(self, formatter: str):
            """
            设置数字格式

            Args:
                formatter: 数字格式字符串，支持的格式类型：
                    - "@": 纯文本 (text)
                    - "0": 数字 (1024)
                    - "#,##0": 数字(千分位) (1,024)
                    - "#,##0.00": 数字(千分位 小数点) (1,024.56)
                    - "0%": 百分比 (10%)
                    - "0.00%": 百分比(小数点) (10.24%)
                    - "0.00E+00": 科学计数 (1.02E+03)
                    - "¥#,##0": 人民币 (¥1,024)
                    - "¥#,##0.00": 人民币(小数点) (¥1,024.56)
                    - "$#,##0": 美元 ($1,024)
                    - "$#,##0.00": 美元(小数点) ($1,024.56)
                    - "yyyy/MM/dd": 日期 (2017/08/10)
                    - "yyyy-MM-dd": 日期 (2017-08-10)
                    - "HH:mm:ss": 时间 (23:24:25)
                    - "yyyy/MM/dd HH:mm:ss": 日期时间 (2017/08/10 23:24:25)

            Example:
                >>> CellStyle.builder().formatter("#,##0.00").build()  # 千分位+两位小数
                >>> CellStyle.builder().formatter("¥#,##0.00").build()  # 人民币格式
            """
            self.style.formatter = formatter
            return self

        def h_align(self, align: Literal[0, 1, 2]):
            """
            设置水平对齐方式

            Args:
                align: 0-左对齐, 1-居中, 2-右对齐
            """
            self.style.hAlign = align
            return self

        def v_align(self, align: Literal[0, 1, 2]):
            """
            设置垂直对齐方式

            Args:
                align: 0-顶部对齐, 1-居中, 2-底部对齐
            """
            self.style.vAlign = align
            return self

        def fore_color(self, color: str):
            """
            设置前景色（文字颜色）

            Args:
                color: 十六进制颜色值，如 "#000000"
            """
            self.style.foreColor = color
            return self

        def back_color(self, color: str):
            """
            设置背景色

            Args:
                color: 十六进制颜色值，如 "#21d11f"
            """
            self.style.backColor = color
            return self

        def border_type(self, border_type: str):
            """
            设置边框类型

            Args:
                border_type: 边框类型，可选值：
                    - FULL_BORDER: 全边框，即四周都有边框
                    - OUTER_BORDER: 外边框，只有外侧有边框
                    - INNER_BORDER: 内边框，只有内部有边框
                    - NO_BORDER: 无边框
                    - LEFT_BORDER: 左边框，只有左侧有边框
                    - RIGHT_BORDER: 右边框，只有右侧有边框
                    - TOP_BORDER: 上边框，只有顶部有边框
                    - BOTTOM_BORDER: 下边框，只有底部有边框

            Example:
                >>> CellStyle.builder().border_type("FULL_BORDER").build()
            """
            self.style.borderType = border_type
            return self

        def border_color(self, color: str):
            """
            设置边框颜色

            Args:
                color: 十六进制颜色值，如 "#ff0000"
            """
            self.style.borderColor = color
            return self

        def clean(self, clean: bool = True):
            """
            是否清除所有样式

            Args:
                clean: True - 清除所有现有样式，False - 追加样式，默认 True

            Example:
                >>> CellStyle.builder().clean(True).build()  # 清除单元格所有样式
            """
            self.style.clean = clean
            return self

        def build(self):
            """构建 CellStyle 对象"""
            return self.style
