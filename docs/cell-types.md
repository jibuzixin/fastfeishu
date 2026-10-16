# 单元格类型

支持写入特殊单元格类型，让单元格内容更丰富：

## 1. 基础类型

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import TextLink, Email, Formula, PlainText, Number, DateValue
from datetime import date, datetime

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 文本链接
    s.write('a1', [[TextLink('https://example.com', '点击访问')]])

    # 邮箱
    s.write('b1', [[Email('test@example.com')]])

    # 公式
    s.write('c1', [[Formula('=A1+B1')]])

    # 纯文本（显式）
    s.write('d1', [[PlainText('普通文本')]])

    # 数字（显式）
    s.write('e1', [[Number(123.45)]])

    # 日期（使用飞书日期格式）
    # DateValue(44562) 对应 2022-01-01
    s.write('f1', [[DateValue.from_date(date(2024, 3, 15))]])
    s.write('g1', [[DateValue.today()]])       # 今天
    s.write('h1', [[DateValue.now()]])          # 当前日期时间
    s.write('i1', [[DateValue.from_string("2024-03-15")]])
```

## 2. 富文本类型

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import RichText, SegmentStyle, StyleDirector

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 基础用法：构建富文本
    rich = (RichText.builder()
            .add_plain("状态：")
            .add_bold("成功")
            .add_plain("，共")
            .add_colored("100", "#00cc00")
            .add_plain("条")
            .build())
    s.write('a1', [[rich]])

    # 使用预设样式（Director）
    title = (RichText.builder()
             .add_plain("", StyleDirector.title())  # 标题样式
             .build())

    warning = (RichText.builder()
               .add_plain("警告", StyleDirector.warning())
               .build())

    # 拼接多个 RichText
    rich1 = RichText.builder().add_plain("Part1").build()
    rich2 = RichText.builder().add_bold("Part2").build()
    combined = (RichText.builder()
                .append_rich(rich1)
                .add_plain(" - ")
                .append_rich(rich2)
                .build())
```

## 3. @人和@文档

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import MentionUser, MentionDoc

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # @人（通过邮箱）
    s.write('a1', [[MentionUser(
        user_info='user@example.com',
        text_type='email',
        notify=True
    )]])

    # @文档
    s.write('b1', [[MentionDoc(
        file_token='doc_token',
        obj_type='doc'
    )]])
```

## 4. 下拉列表

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import MultipleValue

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 创建下拉列表
    s.write('a1', [[MultipleValue(['选项A', '选项B', '选项C'])]])

    # 包含布尔值的下拉列表
    s.write('b1', [[MultipleValue([True, False, '待定'])]])
```

## 5. 带样式的链接和邮箱

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import StyledLink, StyledEmail, SegmentStyle, TextSegment

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 带分段样式的链接
    s.write('a1', [[StyledLink(
        link='https://example.com',
        text='点击访问',
        segments=[
            TextSegment("访问", SegmentStyle(bold=True, foreColor="#ff0000").to_json()),
            TextSegment("页面", SegmentStyle(italic=True).to_json())
        ]
    )]])

    # 带样式的邮箱
    s.write('b1', [[StyledEmail(
        email='test@example.com',
        segments=[
            TextSegment("联系", SegmentStyle(bold=True).to_json()),
            TextSegment("我们", SegmentStyle(italic=True).to_json())
        ]
    )]])
```

## 6. 自动类型转换

```python
from fastfeishu.core import FeiShuSheet
from fastfeishu.models.type import CellTypeConverter

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 自动识别类型并转换
    cell = CellTypeConverter.auto_convert("https://example.com")  # 返回 NotTextLink
    cell2 = CellTypeConverter.auto_convert("test@example.com")      # 返回 Email
    cell3 = CellTypeConverter.auto_convert("=A1+B1")               # 返回 Formula
    cell4 = CellTypeConverter.auto_convert(123)                   # 返回 123（数字）
    cell5 = CellTypeConverter.auto_convert(True)                    # 返回 PlainText("True")

    # 批量转换列表
    data = ["https://example.com", "test@example.com", "=A1+B1", 123]
    cells = CellTypeConverter.from_list(data)

    # 批量转换二维表格
    table = [
        ["https://example.com", "test@example.com"],
        ["=A1+B1", 123]
    ]
    cells_table = CellTypeConverter.from_list_to_json(table)
    s.write('A1:D2', cells_table)
```

---
