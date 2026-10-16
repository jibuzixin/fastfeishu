# FastFeishu 类型系统 v2.0 - 功能说明

## 🎉 新增功能总览

### 1. **链式调用** - 让代码更流畅
```python
style = (SegmentStyle()
         .set_bold(True)
         .set_color("#ff0000")
         .set_size(20))
```

### 2. **预设样式主题** - 保持视觉一致性
```python
# 10种预设样式主题
StylePresets.TITLE       # 标题
StylePresets.WARNING     # 警告
StylePresets.SUCCESS     # 成功
StylePresets.IMPORTANT   # 重要
# ... 更多
```

### 3. **日期辅助函数** - 简化日期处理
```python
DateValue.today()                          # 今天
DateValue.now()                            # 现在
DateValue.from_string("2024-03-15")        # 从字符串
DateValue.from_date(date.today())          # 从date对象
```

### 4. **富文本支持** - 混合多种样式
```python
rich = (RichText()
        .add_plain("普通文本 ")
        .add_bold("加粗文本 ")
        .add_colored("彩色文本", "#ff0000"))
```

### 5. **批量转换工具** - 自动识别类型
```python
# 自动识别：文本、数字、邮箱、链接、公式、日期
data = ["文本", 123, "user@example.com", date.today()]
converted = CellConverter.from_list(data)
```

### 6. **数据验证** - 更安全
```python
Email("user@example.com")        # 自动验证邮箱格式
Email("invalid", validate=False)  # 可选跳过验证
```

---

## 📦 完整功能列表

### 基础数据类型

| 类型 | 类名 | 示例 |
|------|------|------|
| 纯文本 | `PlainText` | `PlainText("文本")` |
| 数字 | `Number` | `Number(123.45)` |
| 日期 | `DateValue` | `DateValue.today()` |
| 带样式文本 | `StyledText` | `StyledText("文本", style)` |

### 链接和邮箱

| 类型 | 类名 | 示例 |
|------|------|------|
| 无文本链接 | `NotTextLink` | `NotTextLink("https://...")` |
| 带文本链接 | `TextLink` | `TextLink("url", "文本")` |
| 分段样式链接 | `StyledLink` | `StyledLink("url", segments=[...])` |
| 普通邮箱 | `Email` | `Email("user@example.com")` |
| 分段样式邮箱 | `StyledEmail` | `StyledEmail("email", segments=[...])` |

### @功能

| 类型 | 类名 | 示例 |
|------|------|------|
| @人 | `MentionUser` | `MentionUser("email", notify=True)` |
| @文档 | `MentionDoc` | `MentionDoc("token", obj_type="sheet")` |

### 公式和下拉

| 类型 | 类名 | 示例 |
|------|------|------|
| 公式 | `Formula` | `Formula("=SUM(A1:A10)")` |
| 下拉列表 | `MultipleValue` | `MultipleValue([1, "选项", True])` |

### 高级功能

| 功能 | 类名 | 说明 |
|------|------|------|
| 富文本 | `RichText` | 混合多种样式 |
| 批量转换 | `CellConverter` | 自动识别类型 |
| 样式系统 | `SegmentStyle` | 支持链式调用 |
| 预设主题 | `StylePresets` | 10种预设样式 |

---

## 🎨 预设样式主题详解

### 所有可用主题

```python
StylePresets.TITLE       # 标题：黑色、加粗、24号
StylePresets.SUBTITLE    # 副标题：深灰、加粗、18号
StylePresets.BODY        # 正文：灰色、12号
StylePresets.WARNING     # 警告：红色、加粗
StylePresets.SUCCESS     # 成功：绿色、加粗
StylePresets.INFO        # 信息：蓝色
StylePresets.IMPORTANT   # 重要：橙色、加粗斜体、14号
StylePresets.HIGHLIGHT   # 高亮：黄色、加粗、16号
StylePresets.SECONDARY   # 次要：灰色、斜体、10号
StylePresets.DEPRECATED  # 废弃：灰色、删除线
```

### 使用方式

```python
# 方式1：直接使用
text = StyledText("标题", StylePresets.TITLE)

# 方式2：基于预设修改
custom = StylePresets.custom(StylePresets.TITLE).set_color("#0066ff")
text = StyledText("蓝色标题", custom)

# 方式3：完全自定义
style = (SegmentStyle()
         .set_bold(True)
         .set_color("#ff0000")
         .set_size(20))
text = StyledText("自定义", style)
```

---

## 📅 日期处理完整指南

### 所有可用方法

```python
from datetime import date, datetime, timedelta

# 快捷方法
DateValue.today()                    # 今天日期
DateValue.now()                      # 当前时间

# 从Python对象创建
DateValue.from_date(date(2024, 3, 15))              # 从date
DateValue.from_datetime(datetime(2024, 3, 15, 14, 30))  # 从datetime

# 从字符串创建
DateValue.from_string("2024-03-15")                      # 默认格式
DateValue.from_string("2024/03/15", "%Y/%m/%d")         # 自定义格式
DateValue.from_string("2024/03/15 14:30", "%Y/%m/%d %H:%M")  # 含时间

# 日期计算
tomorrow = DateValue.from_date(date.today() + timedelta(days=1))
last_week = DateValue.from_date(date.today() - timedelta(days=7))
```

---

## 🔄 批量转换工具使用

### 自动识别规则

```python
CellConverter.auto_convert_to_json("文本")  # → PlainText
CellConverter.auto_convert_to_json(123)  # → Number
CellConverter.auto_convert("user@example.com")  # → Email
CellConverter.auto_convert("https://feishu.cn")  # → NotTextLink
CellConverter.auto_convert_to_json("=SUM(A1:A10)")  # → Formula
CellConverter.auto_convert(date.today())  # → DateValue
CellConverter.auto_convert_to_json([1, 2, 3])  # → MultipleValue
```

### 批量转换

```python
# 一维列表
data = ["文本", 123, "user@example.com"]
converted = CellConverter.from_list(data)

# 二维表格
table = [
    ["姓名", "年龄", "邮箱"],
    ["张三", 25, "zhangsan@example.com"],
]
converted = CellConverter.from_table(table)

# 字典
data_dict = {"name": "张三", "age": 25}
converted = CellConverter.from_dict(data_dict)
```

---

## 🎯 三种使用模式

### 模式1：极简模式（推荐新手）

```python
# 特点：最简单，自动转换
from fastfeishu.models.type import CellConverter

data = [["姓名", "年龄"], ["张三", 25]]
result = CellConverter.from_table(data)
```

**适用场景**：
- 快速原型开发
- 数据格式简单
- 不需要特殊样式

### 模式2：预设模式（推荐进阶）

```python
# 特点：使用预设样式，保持一致性
from fastfeishu.models.type import StyledText, StylePresets

title = StyledText("标题", StylePresets.TITLE)
warning = StyledText("警告", StylePresets.WARNING)
success = StyledText("成功", StylePresets.SUCCESS)
```

**适用场景**：
- 团队协作项目
- 需要视觉一致性
- 常规样式需求

### 模式3：完全自定义（推荐高级）

```python
# 特点：完全控制，灵活定制
from fastfeishu.models.type import SegmentStyle, StyledText

style = (SegmentStyle()
         .set_bold(True)
         .set_italic(True)
         .set_color("#ff6600")
         .set_size(18))
text = StyledText("自定义", style)
```

**适用场景**：
- 特殊样式需求
- 复杂排版
- 品牌定制化

---

## 📖 最佳实践

### ✅ 推荐做法

```python
# 1. 简单数据用批量转换
data = ["文本", 123, "user@example.com"]
result = CellConverter.from_list(data)

# 2. 常规样式用预设主题
title = StyledText("标题", StylePresets.TITLE)

# 3. 日期用快捷方法
today = DateValue.today()

# 4. 自定义样式用链式调用
style = SegmentStyle().set_bold(True).set_color("#ff0000")
```

### ❌ 避免做法

```python
# ❌ 不要手写日期数值
date = DateValue(44562)

# ✅ 应该用快捷方法
date = DateValue.from_string("2024-03-15")

# ❌ 不要重复定义相同样式
style1 = SegmentStyle(bold=True, fore_color="#ff0000")
style2 = SegmentStyle(bold=True, fore_color="#ff0000")

# ✅ 应该用预设主题
text1 = StyledText("警告1", StylePresets.WARNING)
text2 = StyledText("警告2", StylePresets.WARNING)
```

---

## 🚀 快速开始

### 5分钟上手

```python
# 1. 导入
from fastfeishu.models.type import (
    PlainText, Number, DateValue, StyledText,
    StylePresets, CellConverter
)
from datetime import date

# 2. 创建简单数据
text = PlainText("文本").to_json()
number = Number(123).to_json()
today = DateValue.today().to_json()

# 3. 使用预设样式
title = StyledText("标题", StylePresets.TITLE).to_json()
warning = StyledText("警告", StylePresets.WARNING).to_json()

# 4. 批量转换（最简单！）
data = [
    ["姓名", "年龄", "入职日期"],
    ["张三", 25, date(2023, 1, 15)],
    ["李四", 30, date(2022, 6, 20)],
]
result = CellConverter.from_table(data)

# 5. 结果可直接用于飞书API
# 将 result 传递给飞书API的写入接口
```

---

## 📚 示例文件

项目包含3个完整示例：

1. **cell_types_demo.py** - 基础类型演示
2. **advanced_features_demo.py** - 高级功能演示（10个演示场景）
3. **real_world_scenarios.py** - 真实场景演示
   - 销售数据报表
   - 产品库存报表
   - 员工绩效报表
   - 通知消息生成

### 运行示例

```bash
# 基础演示
python examples/cell_types_demo.py

# 高级功能演示
python examples/advanced_features_demo.py

# 真实场景演示
python examples/real_world_scenarios.py
```

---

## 💡 常见问题

### Q1: 如何选择使用模式？

**A:** 根据项目需求：
- 新手/快速开发 → 极简模式（批量转换）
- 团队项目/需要一致性 → 预设模式
- 特殊需求/高度定制 → 完全自定义

### Q2: 预设样式可以修改吗？

**A:** 可以，使用 `StylePresets.custom()` 方法：
```python
custom = StylePresets.custom(StylePresets.TITLE).set_color("#0066ff")
```

### Q3: 批量转换会识别所有类型吗？

**A:** 会自动识别：
- 文本、数字、布尔值
- 邮箱（含@和.）
- URL（http/https开头）
- 公式（=开头）
- 日期对象
- 列表（下拉列表）

### Q4: 如何处理复杂的日期格式？

**A:** 使用 `from_string` 并指定格式：
```python
DateValue.from_string("15/03/2024", "%d/%m/%Y")
DateValue.from_string("2024年3月15日", "%Y年%m月%d日")
```

### Q5: 富文本适用于什么场景？

**A:** 适用于需要在一个单元格内混合多种样式的场景：
- 状态消息（"处理完成，共100条记录"）
- 通知文本（"【重要】会议通知"）
- 进度信息（"已完成 80% 剩余 20%"）

---

## 🔧 技术细节

### 数据验证

```python
# 邮箱验证
Email("user@example.com")          # ✓ 通过
Email("invalid")                   # ✗ 抛出 ValueError
Email("invalid", validate=False)   # ✓ 跳过验证

# 字体大小验证
SegmentStyle(font_size=20)         # ✓ 通过（9-36）
SegmentStyle(font_size=50)         # ✗ 抛出 ValueError

# 下拉列表验证
MultipleValue([1, "选项"])         # ✓ 通过
MultipleValue(["a,b"])             # ✗ 抛出 ValueError（不能含逗号）
```

### 自动过滤None值

```python
style = SegmentStyle(bold=True, italic=None)
style.to_json()
# 结果: {'bold': True}  # italic=None被自动过滤
```

### 链式调用返回self

```python
style = (SegmentStyle()
         .set_bold(True)      # 返回self
         .set_color("#ff0000") # 返回self
         .set_size(20))       # 返回self
```

---

## 📞 获取帮助

- 查看示例代码：`examples/` 目录
- 阅读快速入门：`docs/QUICK_START.md`
- 查看API文档：代码注释中包含详细说明

---

**版本**: v2.0
**最后更新**: 2024-03-13
**作者**: FastFeishu Team
