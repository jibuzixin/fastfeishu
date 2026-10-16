# FastFeishu 建造者模式 - 快速入门指南

## 🎉 全新的建造者模式实现

FastFeishu v2.1 采用标准的建造者模式(Builder Pattern)，更规范、更安全、更强大！

---

## 📚 三种使用方式

### 方式1：使用 Builder（推荐⭐⭐⭐）

```python
from fastfeishu.models.type import SegmentStyleBuilder, StyledText

# 创建样式
builder = SegmentStyleBuilder()
style = builder.bold(True).color("#ff0000").size(20).build()

# 创建带样式的文本
text = StyledText("重要通知", style)
```

**优势**：
- ✅ 标准设计模式
- ✅ 可以复用 builder
- ✅ 链式调用优雅
- ✅ 无副作用，更安全

---

### 方式2：使用 Director（最简单⭐⭐⭐）

```python
from fastfeishu.models.type import StyleDirector, StyledText

# 直接使用预设样式
title = StyledText("标题", StyleDirector.title())
warning = StyledText("警告", StyleDirector.warning())
success = StyledText("成功", StyleDirector.success())
```

**优势**：
- ✅ 开箱即用
- ✅ 视觉一致
- ✅ 代码最简洁

---

### 方式3：传统方式（仍然支持）

```python
from fastfeishu.models.type import SegmentStyle, StyledText

# 直接实例化
style = SegmentStyle(bold=True, fore_color="#ff0000", font_size=20)
text = StyledText("重要通知", style)
```

---

## 🚀 快速开始

### 第一步：导入

```python
from fastfeishu.models.type import (
    # Builder 和 Director
    SegmentStyleBuilder, StyleDirector, RichTextBuilder,
    # 基础类型
    PlainText, Number, DateValue, StyledText,
    # 其他
    Email, TextLink, Formula, CellConverter
)
from datetime import date
```

### 第二步：选择方式

**场景1：创建简单样式**

```python
# 使用 Director（最快）
style = StyleDirector.warning()

# 或者用 Builder
style = SegmentStyleBuilder().bold(True).color("#ff0000").build()
```

**场景2：基于预设修改**

```python
# 使用 Director 的 Builder 方法
style = StyleDirector.title_builder().color("#0066ff").build()

# 或者直接用 Builder
style = (SegmentStyleBuilder()
         .bold(True)
         .size(24)
         .color("#0066ff")  # 自定义颜色
         .build())
```

**场景3：复用 Builder**

```python
builder = SegmentStyleBuilder()

# 创建多个样式
style1 = builder.bold(True).color("#ff0000").build()
style2 = builder.reset().italic(True).color("#00cc00").build()
style3 = builder.reset().underline(True).size(12).build()
```

---

## 📖 完整示例

### 示例1：创建带样式的表格标题

```python
from fastfeishu.models.type import StyledText, StyleDirector

# 使用 Director（推荐）
headers = [
    StyledText("姓名", StyleDirector.title()),
    StyledText("年龄", StyleDirector.title()),
    StyledText("邮箱", StyleDirector.title()),
]

# 转换为 JSON
header_row = [h.to_json() for h in headers]
```

### 示例2：使用 Builder 创建自定义样式

```python
from fastfeishu.models.type import SegmentStyleBuilder, StyledText

# 创建 Builder
builder = SegmentStyleBuilder()

# 链式调用
custom_style = (builder
                .bold(True)
                .italic(True)
                .color("#ff6600")
                .size(18)
                .build())

text = StyledText("自定义样式", custom_style)
```

### 示例3：复用 Builder 创建多个样式

```python
from fastfeishu.models.type import SegmentStyleBuilder, StyledText

builder = SegmentStyleBuilder()

# 警告样式
warning_style = builder.bold(True).color("#ff0000").build()
text1 = StyledText("警告", warning_style)

# 重置后创建成功样式
success_style = builder.reset().bold(True).color("#00cc00").build()
text2 = StyledText("成功", success_style)

# 重置后创建提示样式
info_style = builder.reset().italic(True).color("#0066ff").build()
text3 = StyledText("提示", info_style)
```

### 示例4：富文本 Builder

```python
from fastfeishu.models.type import RichTextBuilder, SegmentStyleBuilder

# 创建富文本
builder = RichTextBuilder()
rich = (builder
        .add_plain("处理状态：")
        .add_bold("成功")
        .add_plain("，共处理 ")
        .add_colored("100", "#00cc00")
        .add_plain(" 条记录")
        .build())

# 或者使用自定义样式
custom_builder = SegmentStyleBuilder().bold(True).size(20)
rich2 = (RichTextBuilder()
         .add_plain("重要：")
         .add_with_style("请注意", custom_builder)
         .build())
```

### 示例5：基于预设修改

```python
from fastfeishu.models.type import StyleDirector, StyledText

# 使用 Director 的 Builder 方法
blue_title = StyleDirector.title_builder().color("#0066ff").build()
text = StyledText("蓝色标题", blue_title)

# 或者基于警告样式修改
large_warning = StyleDirector.warning_builder().size(24).build()
text2 = StyledText("大号警告", large_warning)
```

---

## 🎨 预设样式（Director）

### 所有可用样式

```python
from fastfeishu.models.type import StyleDirector

# 直接使用（返回 SegmentStyle）
StyleDirector.title()       # 标题：黑色、加粗、24号
StyleDirector.subtitle()    # 副标题：深灰、加粗、18号
StyleDirector.body()        # 正文：灰色、12号
StyleDirector.warning()     # 警告：红色、加粗
StyleDirector.success()     # 成功：绿色、加粗
StyleDirector.info()        # 信息：蓝色
StyleDirector.important()   # 重要：橙色、加粗斜体、14号
StyleDirector.highlight()   # 高亮：黄色、加粗、16号
StyleDirector.secondary()   # 次要：灰色、斜体、10号
StyleDirector.deprecated()  # 废弃：灰色、删除线

# 获取 Builder（可以继续修改）
StyleDirector.title_builder()    # 返回标题样式的 Builder
StyleDirector.warning_builder()  # 返回警告样式的 Builder
StyleDirector.success_builder()  # 返回成功样式的 Builder
```

---

## 🔧 Builder API 参考

### SegmentStyleBuilder

| 方法 | 说明 | 示例 |
|------|------|------|
| `bold(value=True)` | 设置加粗 | `.bold(True)` |
| `italic(value=True)` | 设置斜体 | `.italic(True)` |
| `strike_through(value=True)` | 设置删除线 | `.strike_through(True)` |
| `underline(value=True)` | 设置下划线 | `.underline(True)` |
| `color(color)` | 设置颜色 | `.color("#ff0000")` |
| `size(size)` | 设置字体大小(9-36) | `.size(20)` |
| `reset()` | 重置builder | `.reset()` |
| `build()` | 构建最终对象 | `.build()` |

### RichTextBuilder

| 方法 | 说明 | 示例 |
|------|------|------|
| `add_text(text, style)` | 添加带样式文本 | `.add_text("文本", style)` |
| `add_plain(text)` | 添加普通文本 | `.add_plain("文本")` |
| `add_bold(text)` | 添加加粗文本 | `.add_bold("加粗")` |
| `add_italic(text)` | 添加斜体文本 | `.add_italic("斜体")` |
| `add_colored(text, color)` | 添加彩色文本 | `.add_colored("红色", "#ff0000")` |
| `add_with_style(text, builder)` | 使用Builder添加 | `.add_with_style("文本", builder)` |
| `reset()` | 重置builder | `.reset()` |
| `build()` | 构建最终对象 | `.build()` |

---

## 💡 最佳实践

### ✅ 推荐做法

```python
# 1. 简单场景：使用 Director
style = StyleDirector.warning()

# 2. 需要修改：使用 Director Builder
style = StyleDirector.title_builder().color("#0066ff").build()

# 3. 完全自定义：使用 Builder
style = (SegmentStyleBuilder()
         .bold(True)
         .color("#ff6600")
         .size(20)
         .build())

# 4. 多个样式：复用 Builder
builder = SegmentStyleBuilder()
style1 = builder.bold(True).build()
style2 = builder.reset().italic(True).build()
```

### ❌ 避免做法

```python
# ❌ 不要忘记调用 build()
builder = SegmentStyleBuilder().bold(True)  # 这还是 Builder，不是 Style
text = StyledText("文本", builder)  # 错误！

# ✅ 应该调用 build()
style = SegmentStyleBuilder().bold(True).build()
text = StyledText("文本", style)

# ❌ 不要为每个样式创建新 Builder（如果样式相似）
builder1 = SegmentStyleBuilder().bold(True).color("#ff0000").build()
builder2 = SegmentStyleBuilder().bold(True).color("#00cc00").build()

# ✅ 应该复用 Builder
builder = SegmentStyleBuilder()
style1 = builder.bold(True).color("#ff0000").build()
style2 = builder.reset().bold(True).color("#00cc00").build()
```

---

## 📊 建造者模式 vs 传统方式

| 特性 | 建造者模式 | 传统方式 |
|------|-----------|---------|
| **代码风格** | 链式调用 | 构造函数参数 |
| **可复用性** | ⭐⭐⭐⭐⭐ 可复用 builder | ⭐⭐ 不可复用 |
| **安全性** | ⭐⭐⭐⭐⭐ 无副作用 | ⭐⭐⭐ 可能有副作用 |
| **易用性** | ⭐⭐⭐⭐ 需要 build() | ⭐⭐⭐⭐⭐ 直接使用 |
| **设计模式** | ⭐⭐⭐⭐⭐ 标准模式 | ⭐⭐⭐ 传统方式 |

---

## 🎯 使用场景建议

| 场景 | 推荐方式 |
|------|---------|
| 快速开发 | Director |
| 需要微调 | Director Builder |
| 完全自定义 | Builder |
| 创建多个相似样式 | 复用 Builder |
| 混合样式文本 | RichTextBuilder |

---

## 🚀 从这里开始

### 30秒快速上手

```python
from fastfeishu.models.type import StyleDirector, StyledText, DateValue, CellConverter
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

---

## 📚 更多示例

- 基础演示：`examples/cell_types_demo.py`
- 建造者模式详解：`examples/builder_pattern_demo.py`
- 真实场景：`examples/real_world_scenarios.py`
- 版本对比：`examples/version_comparison.py`

运行示例：

```bash
python examples/builder_pattern_demo.py
```

---

## 🤔 常见问题

### Q1: 为什么要用建造者模式？

**A**: 建造者模式有以下优势：
- ✅ 标准设计模式，团队协作更规范
- ✅ 可以复用 Builder，减少重复代码
- ✅ 构建过程和表示分离，更安全
- ✅ 无副作用，不会意外修改对象

### Q2: Builder 和 Director 有什么区别？

**A**:
- **Builder**: 提供灵活的构建方法，适合自定义
- **Director**: 封装常用构建过程，提供预设样式，适合快速开发

### Q3: 可以不用 Builder 吗？

**A**: 可以！传统方式仍然支持：
```python
style = SegmentStyle(bold=True, fore_color="#ff0000")
```

### Q4: 忘记调用 build() 怎么办？

**A**: 会报错。记住：Builder 要调用 `.build()` 才能得到最终对象。

---

## 💪 下一步

1. ✅ 运行示例代码熟悉用法
2. ✅ 优先使用 Director（预设样式）
3. ✅ 需要自定义时使用 Builder
4. ✅ 掌握 Builder 的复用技巧

开始使用吧！🎉
