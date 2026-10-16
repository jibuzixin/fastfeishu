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
    # 注意：带样式文本要用 add_with_style(text, style)，add_plain 只接受一个文本参数
    title = (RichText.builder()
             .add_with_style("报表标题", StyleDirector.title())
             .build())

    warning = (RichText.builder()
               .add_with_style("注意：数据可能不完整", StyleDirector.warning())
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

### 2.1 预设样式（StyleDirector）

不想手写样式时，直接用现成预设：

```python
from fastfeishu.models.type import StyleDirector, SegmentStyle

StyleDirector.title()        # 标题：黑色、加粗、24 号
StyleDirector.subtitle()     # 副标题：深灰、加粗、18 号
StyleDirector.body()         # 正文：灰色、12 号
StyleDirector.warning()      # 警告：红色、加粗
StyleDirector.success()      # 成功：绿色、加粗
StyleDirector.info()         # 信息：蓝色
StyleDirector.important()    # 重要：橙色、加粗斜体、14 号
StyleDirector.highlight()    # 高亮：黄色、加粗、16 号
StyleDirector.secondary()    # 次要：灰色、斜体、10 号
StyleDirector.deprecated()   # 废弃：灰色、删除线

# 在预设基础上继续微调（仅 title / warning / success 提供 builder 变体）
warn = StyleDirector.warning_builder().bold(False).build()
```

### 2.2 建造者模式 API 参考

不想用预设时，用 Builder 链式构造。两个入口：`SegmentStyle.builder()` 和 `RichText.builder()`。

**`SegmentStyle.builder()`**

| 方法 | 说明 | 示例 |
| --- | --- | --- |
| `bold(value=True)` | 加粗 | `.bold(True)` |
| `italic(value=True)` | 斜体 | `.italic(True)` |
| `strike_through(value=True)` | 删除线 | `.strike_through(True)` |
| `underline(value=True)` | 下划线 | `.underline(True)` |
| `color(color)` | 前景色 | `.color("#ff0000")` |
| `size(size)` | 字号（9-36） | `.size(20)` |
| `build()` | 构建 `SegmentStyle` | `.build()` |

**`RichText.builder()`**

| 方法 | 说明 | 示例 |
| --- | --- | --- |
| `add_plain(text)` | 追加普通文本 | `.add_plain("文本")` |
| `add_bold(text)` | 追加加粗文本 | `.add_bold("加粗")` |
| `add_italic(text)` | 追加斜体文本 | `.add_italic("斜体")` |
| `add_colored(text, color)` | 追加彩色文本 | `.add_colored("红色", "#ff0000")` |
| `add_with_style(text, style)` | 按 `SegmentStyle` 追加（**第二个参数是 SegmentStyle，不是 Builder**） | `.add_with_style("文本", StyleDirector.title())` |
| `add_text(text, style)` | 带样本文本 | `.add_text("文本", style)` |
| `append_rich(rich)` | 拼接已有 `RichText` | `.append_rich(other)` |
| `append_builder(builder)` | 拼接另一个 Builder | `.append_builder(other_builder)` |
| `extend_segments(segments)` | 批量追加分段 | `.extend_segments(segments)` |
| `build()` | 构建 `RichText` | `.build()` |

**用法选择**：快速开发用 `StyleDirector`；需要微调用 `SegmentStyle.builder()`；混合样本文本用 `RichText.builder()`；要造多个相似样式就把 Builder 复用到最后再 `build()`。

> 忘记 `build()` 会拿到未构建的 Builder 而非 `RichText`，写入前请确认已调用。

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

    # 批量转换列表（返回单元格类型对象）
    data = ["https://example.com", "test@example.com", "=A1+B1", 123]
    cells = CellTypeConverter.from_list(data)

    # 二维表格 → JSON（注意：元素不能混用裸数字，数字请显式包成 Number）
    table = [
        ["https://example.com", "test@example.com"],
        ["=A1+B1", Number(123)]
    ]
    cells_table = CellTypeConverter.from_list_to_json(table)
    s.write('A1:D2', cells_table)

    # 字典转换（单个 dict，不是 dict 列表）
    row = CellTypeConverter.from_dict({
        "name": "张三",
        "mail": "zhangsan@example.com",
        "link": "https://example.com",
    })
```

### 6.1 转换器 API

| 方法 | 作用 | 输出 | 状态 |
| --- | --- | --- | --- |
| `auto_convert(item, validate_email=True)` | 识别单个值类型 | `FeiShuCellType` 或原值 | ✅ |
| `auto_convert_to_json(item)` | 同上，直接转 JSON | `dict` | ✅ |
| `from_list(data)` | 一维列表批量转换 | `List[FeiShuCellType]` | ✅ |
| `from_list_to_json(data)` | 一维/二维列表转 JSON | `List[dict]` | ⚠️ 见下方注意 |
| `from_dict(data, validate_email=True)` | **单个字典**转换 | `dict` | ✅ |
| `from_dict_to_json(data)` | 同上，直接转 JSON | `dict` | ✅ |
| `from_table(table_data, validate_email=True)` | 二维列表转单元格类型 | `List[List[FeiShuCellType]]` | ❌ 见下方注意 |
| `from_table_to_json(table_data)` | 二维列表直接转 JSON | `List[List[dict]]` | ✅ |

> ⚠️ **已知问题（当前版本）**
>
> 1. `from_list_to_json` 遇到裸数字会抛 `AttributeError: 'int' object has no attribute 'to_json'`，因为 `auto_convert(123)` 返回的就是 `int`。纯数字列请显式写 `Number(123)`。
> 2. `from_table` 内部调用了不存在的 `from_list_to_type`，任何输入都会抛 `AttributeError`；暂时改用 `from_table_to_json`。
>
> 这两处是库的实现缺陷而非用法问题，已记录在项目待办中。

---
