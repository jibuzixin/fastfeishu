# FastFeishu 类型系统 - 快速入门指南（建造者模式版）

## 📚 目录
- [基础使用](#基础使用)
- [样式系统](#样式系统)
- [日期处理](#日期处理)
- [批量转换](#批量转换)
- [实战案例](#实战案例)

---

## 基础使用

### 1. 简单数据类型

```python
from fastfeishu.models.type import PlainText, Number, Email, TextLink

# 纯文本
text = PlainText("这是文本").to_json()  # 返回: "这是文本"

# 数字
num = Number(123.45).to_json()  # 返回: 123.45

# 邮箱
email = Email("user@example.com").to_json()  # 返回: "user@example.com"

# 链接
link = TextLink("https://feishu.cn", "飞书官网").to_json()
# 返回: {'type': 'url', 'link': 'https://feishu.cn', 'text': '飞书官网'}
```

---

## 样式系统

### 2. 使用预设样式 Director（推荐⭐⭐⭐）

```python
from fastfeishu.models.type import StyledText, StyleDirector

# 方式1：使用 Director（最简单！）
title = StyledText("标题", StyleDirector.title())
warning = StyledText("警告", StyleDirector.warning())
success = StyledText("成功", StyleDirector.success())
important = StyledText("重要", StyleDirector.important())

# 可用预设：
# - StyleDirector.title()       # 标题（黑色、加粗、24号）
# - StyleDirector.subtitle()    # 副标题（深灰、加粗、18号）
# - StyleDirector.warning()     # 警告（红色、加粗）
# - StyleDirector.success()     # 成功（绿色、加粗）
# - StyleDirector.info()        # 信息（蓝色）
# - StyleDirector.important()   # 重要（橙色、加粗斜体、14号）
# - StyleDirector.highlight()   # 高亮（黄色、加粗、16号）
# - StyleDirector.secondary()   # 次要（灰色、斜体、10号）
# - StyleDirector.deprecated()  # 废弃（灰色、删除线）
```

### 3. 使用 Builder 创建样式（推荐⭐⭐⭐）

```python
from fastfeishu.models.type import SegmentStyleBuilder, StyledText

# 方式2：使用 Builder（灵活！）
builder = SegmentStyleBuilder()
style = builder.bold(True).color("#ff0000").size(20).build()
text = StyledText("自定义样式", style)

# 链式调用
style = (SegmentStyleBuilder()
         .bold(True)
         .italic(True)
         .color("#ff0000")
         .size(20)
         .build())
text = StyledText("链式调用", style)
```

### 4. 基于预设修改

```python
from fastfeishu.models.type import StyleDirector, StyledText

# 使用 Director 的 Builder 方法
blue_title = StyleDirector.title_builder().color("#0066ff").build()
text = StyledText("蓝色标题", blue_title)

# 或者修改其他样式
large_warning = StyleDirector.warning_builder().size(24).build()
text2 = StyledText("大号警告", large_warning)
```

### 5. 复用 Builder

```python
from fastfeishu.models.type import SegmentStyleBuilder

# Builder 可以复用
builder = SegmentStyleBuilder()

# 创建多个样式
style1 = builder.bold(True).color("#ff0000").build()
style2 = builder.reset().italic(True).color("#00cc00").build()
style3 = builder.reset().underline(True).size(12).build()
```

---

## 日期处理

### 6. 日期快捷方法（推荐⭐⭐⭐）

```python
from fastfeishu.models.type import DateValue
from datetime import date, datetime, timedelta

# 最简单的方式
today = DateValue.today()  # 今天
now = DateValue.now()  # 现在（含时间）

# 从Python对象创建
date_val = DateValue.from_date(date(2024, 3, 15))
datetime_val = DateValue.from_datetime(datetime(2024, 3, 15, 14, 30))

# 从字符串创建
date1 = DateValue.from_string("2024-03-15")
date2 = DateValue.from_string("2024/03/15 14:30", "%Y/%m/%d %H:%M")

# 日期计算
tomorrow = DateValue.from_date(date.today() + timedelta(days=1))
last_week = DateValue.from_date(date.today() - timedelta(days=7))
```

---

## 批量转换

### 7. 自动识别类型（最省事⭐⭐⭐）

```python
from fastfeishu.models.type import CellConverter
from datetime import date

# 一维列表：自动识别类型！
data = [
    "文本",
    123,
    "user@example.com",  # 自动识别为邮箱
    "https://feishu.cn",  # 自动识别为链接
    "=SUM(A1:A10)",  # 自动识别为公式
    date.today(),  # 自动识别为日期
]
converted = CellConverter.from_list(data)

# 二维表格：批量处理
table = [
    ["姓名", "年龄", "邮箱", "入职日期"],
    ["张三", 25, "zhangsan@example.com", date(2023, 1, 15)],
    ["李四", 30, "lisi@example.com", date(2022, 6, 20)],
]
table_converted = CellConverter.from_table(table)
```

---

## 实战案例

### 案例1：简单表格（推荐新手）

```python
from fastfeishu.models.type import CellConverter
from datetime import date

# 最简单的方式：直接传数据，自动转换！
data = [
    ["产品名称", "价格", "库存", "更新日期"],
    ["iPhone 15", 5999, 100, date(2024, 3, 1)],
    ["MacBook Pro", 12999, 50, date(2024, 3, 5)],
]

# 一行代码完成转换
result = CellConverter.from_table(data)

# result 可以直接用于飞书API
```

### 案例2：带样式的表格（推荐进阶）

```python
from fastfeishu.models.type import (
    PlainText, Number, StyledText, DateValue,
    StyleDirector, SegmentStyleBuilder
)
from datetime import date

# 表头：使用 Director
headers = [
    StyledText("姓名", StyleDirector.title()).to_json(),
    StyledText("绩效", StyleDirector.title()).to_json(),
    StyledText("状态", StyleDirector.title()).to_json(),
]

# 数据行：使用 Builder
builder = SegmentStyleBuilder()
name_style = builder.bold(True).size(14).build()

row1 = [
    StyledText("张三", name_style).to_json(),
    Number(95.5).to_json(),
    StyledText("优秀", StyleDirector.success()).to_json(),
]

row2 = [
    StyledText("李四", name_style).to_json(),
    Number(58.0).to_json(),
    StyledText("不及格", StyleDirector.warning()).to_json(),
]

# 组合
table = [headers, row1, row2]
```

### 案例3：复杂表格（推荐高级）

```python
from fastfeishu.models.type import (
    StyledText, Number, Email, Formula,
    DateValue, MentionUser, StyleDirector,
    SegmentStyleBuilder
)
from datetime import date

# 完整的员工信息表
def create_employee_row(emp_id, name, email_addr, hire_date, score):
    # 使用 Builder 创建姓名样式
    builder = SegmentStyleBuilder()
    name_style = builder.bold(True).size(14).build()

    # 根据分数决定样式（使用 Director）
    if score >= 90:
        score_style = StyleDirector.success()
        status_text = "优秀"
        status_style = StyleDirector.success()
    elif score >= 60:
        score_style = StyleDirector.info()
        status_text = "良好"
        status_style = StyleDirector.info()
    else:
        score_style = StyleDirector.warning()
        status_text = "需改进"
        status_style = StyleDirector.warning()

    return [
        PlainText(emp_id).to_json(),
        StyledText(name, name_style).to_json(),
        Email(email_addr).to_json(),
        DateValue.from_date(hire_date).to_json(),
        StyledText(str(score), score_style).to_json(),
        Formula('=IF(E2>=90,"优秀",IF(E2>=60,"良好","需改进"))').to_json(),
        StyledText(status_text, status_style).to_json(),
    ]

# 使用
row = create_employee_row(
    "EMP001",
    "张三",
    "zhangsan@company.com",
    date(2023, 1, 15),
    95.5
)
```

### 案例4：富文本（混合样式）

```python
from fastfeishu.models.type import RichTextBuilder, SegmentStyleBuilder

# 使用 RichTextBuilder
builder = RichTextBuilder()
rich = (builder
        .add_plain("处理状态：")
        .add_bold("成功")
        .add_plain("，共处理 ")
        .add_colored("100", "#00cc00")
        .add_plain(" 条记录")
        .build())

cell = rich

# 使用自定义样式
custom_builder = SegmentStyleBuilder().bold(True).size(20)
rich2 = (RichTextBuilder()
         .add_plain("重要：")
         .add_with_style("请注意", custom_builder)
         .build())
```

---

## 🎯 最佳实践

### ✅ 推荐做法

```python
# 1. 简单数据：用批量转换
data = ["文本", 123, "user@example.com"]
result = CellConverter.from_list(data)

# 2. 需要样式：用 Director（预设）
text = StyledText("标题", StyleDirector.title())

# 3. 自定义样式：用 Builder
style = SegmentStyleBuilder().bold(True).color("#ff0000").build()

# 4. 基于预设修改：用 Director Builder
style = StyleDirector.title_builder().color("#0066ff").build()

# 5. 日期处理：用快捷方法
today = DateValue.today()

# 6. 多个相似样式：复用 Builder
builder = SegmentStyleBuilder()
style1 = builder.bold(True).build()
style2 = builder.reset().italic(True).build()
```

### ❌ 避免做法

```python
# ❌ 不要忘记调用 build()
builder = SegmentStyleBuilder().bold(True)  # 这还是Builder！
text = StyledText("文本", builder)  # 错误！

# ✅ 记得调用 build()
style = SegmentStyleBuilder().bold(True).build()
text = StyledText("文本", style)

# ❌ 不要手写日期数值
date = DateValue(44562)  # 谁知道这是哪天？

# ✅ 应该用快捷方法
date = DateValue.from_string("2024-03-15")  # 清晰明了！

# ❌ 不要每次都创建新Builder（如果样式相似）
style1 = SegmentStyleBuilder().bold(True).color("#ff0000").build()
style2 = SegmentStyleBuilder().bold(True).color("#00cc00").build()

# ✅ 应该复用Builder
builder = SegmentStyleBuilder()
style1 = builder.bold(True).color("#ff0000").build()
style2 = builder.reset().bold(True).color("#00cc00").build()
```

---

## 🔥 三种使用模式

### 模式1：极简模式（适合快速开发）

```python
from fastfeishu.models.type import CellConverter

# 直接传数据，自动转换
data = [["姓名", "年龄"], ["张三", 25]]
result = CellConverter.from_table(data)
```

### 模式2：预设模式（适合规范项目）

```python
from fastfeishu.models.type import StyledText, StyleDirector

# 使用 Director 预设样式，保持一致性
title = StyledText("标题", StyleDirector.title())
warning = StyledText("警告", StyleDirector.warning())
```

### 模式3：建造者模式（适合完全自定义）

```python
from fastfeishu.models.type import SegmentStyleBuilder, StyledText

# 使用 Builder 完全控制每个细节
builder = SegmentStyleBuilder()
style = builder.bold(True).italic(True).color("#ff6600").size(18).build()
text = StyledText("自定义", style)
```

---

## 📖 常用API速查

| 功能 | 代码 |
|------|------|
| **基础类型** | |
| 纯文本 | `PlainText("文本")` |
| 数字 | `Number(123)` |
| 今天日期 | `DateValue.today()` |
| 现在时间 | `DateValue.now()` |
| 邮箱 | `Email("user@example.com")` |
| 链接 | `TextLink("url", "文本")` |
| 公式 | `Formula("=SUM(A1:A10)")` |
| **样式系统** | |
| Builder | `SegmentStyleBuilder().bold(True).build()` |
| 标题样式 | `StyleDirector.title()` |
| 警告样式 | `StyleDirector.warning()` |
| 成功样式 | `StyleDirector.success()` |
| 基于预设修改 | `StyleDirector.title_builder().color("#0066ff").build()` |
| **批量转换** | |
| 自动转换 | `CellConverter.from_list(data)` |
| 批量转换 | `CellConverter.from_table(table)` |
| **富文本** | |
| 富文本Builder | `RichTextBuilder().add_bold("文本").build()` |

---

## 🚀 从这里开始

1. **第一次使用** → 从"案例1：简单表格"开始
2. **需要样式** → 学习"样式系统"部分，使用 Director
3. **自定义样式** → 学习 Builder 用法
4. **处理日期** → 看"日期处理"部分
5. **提高效率** → 用"批量转换"功能

### 30秒快速上手

```python
from fastfeishu.models.type import (
    StyleDirector, StyledText, DateValue, CellConverter
)
from datetime import date

# 1. 使用 Director 创建样式（最简单）
title = StyledText("销售报表", StyleDirector.title())

# 2. 使用快捷日期方法
today = DateValue.today()

# 3. 批量转换数据
data = [
    ["姓名", "销售额", "日期"],
    ["张三", 10000, date.today()],
    ["李四", 15000, date.today()],
]
table = CellConverter.from_table(data)

print("✅ 完成！数据可以直接传给飞书API")
```

祝你使用愉快！ 🎉
