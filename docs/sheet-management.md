# Sheet 管理

## 1. 创建和复制 Sheet

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接')

    # 创建新 Sheet（在指定位置）
    new_sheet = s.create_sheet(title='新Sheet', index=0)
    print(f"新Sheet链接: {new_sheet.link}")

    # 复制当前 Sheet
    copied_sheet = s.copy(title='副本')
    print(f"复制后的Sheet链接: {copied_sheet.link}")
```

## 2. 获取 Sheet 信息

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 获取当前 Sheet 信息
    info = s.get_sheet_info()
    print(f"行数: {info['rowCount']}, 列数: {info['columnCount']}")

    # 获取所有 Sheet 信息
    sheets = s.get_sheets_info()
    for sheet in sheets:
        print(f"Sheet标题: {sheet.title}, ID: {sheet.sheetId}")

    # 获取工作簿标题
    workbook_title = s.get_workbook_title()
    print(f"工作簿标题: {workbook_title}")

    # 获取表头
    header = s.get_header()
    print(f"表头: {header}")
```

## 3. 属性和状态

```python
from fastfeishu.core import FeiShuSheet

if __name__ == '__main__':
    s = FeiShuSheet('飞书链接', readonly=True)

    # 检查是否只读
    print(s.is_readonly())  # True

    # 获取基础属性
    print(s.sheet_token)   # Sheet Token
    print(s.sheet_id)      # Sheet ID
    print(s.link)          # 当前链接

    # 获取原始请求对象（高级用法）
    raw_req = s.raw_request
```

---
