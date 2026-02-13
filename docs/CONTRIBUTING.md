# 开发指南

## 快速开始

### 1️⃣ 一键设置开发环境

```bash
# 创建并激活虚拟环境
conda create -n feishu python=3.11 -y
conda activate feishu

# 进入项目目录
cd fastfeishu

# 运行一键安装脚本
./setup_dev.sh
```

### 2️⃣ 开始编写代码

编写你的功能代码，然后：

```bash
# 查看修改
git status
git diff

# 提交代码（会自动检查格式）
git add .
git commit -m "[feat] 你的功能描述"

# 推送代码（会自动运行单元测试）
git push origin dev
```

### 3️⃣ 测试自动化流程

当你执行 `git push` 时：

```
正在推送代码...
↓
运行 pre-push hook...
↓
执行单元测试（66个测试）
↓
测试通过 ✅ → 推送成功
测试失败 ❌ → 推送被阻止，修复问题后重试
```

## 自动化测试说明

### 本地测试（pre-push hook）

- **触发时机**: 执行 `git push` 时
- **测试内容**: 运行所有单元测试
- **测试时间**: 约 1-2 秒
- **失败处理**: 阻止推送，需要修复后重试

### CI 测试（GitHub Actions）

- **触发时机**: 创建 Pull Request 时
- **测试内容**: 在 Python 3.11 和 3.12 上运行单元测试
- **测试环境**: 干净的 Linux 环境
- **失败处理**: PR 无法合并，需要修复

## 手动运行测试

```bash
# 运行所有单元测试
pytest tests/unit -v -m unit

# 运行单个测试文件
pytest tests/unit/test_cell_style.py -v

# 查看测试覆盖率
pytest tests/unit -v -m unit --cov=fastfeishu --cov-report=term-missing
```

## 代码提交规范

### Commit Message 格式

```
[type] 简短描述

详细描述（可选）
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `[feat]` | 新功能 | `[feat] 增加批量下载图片功能` |
| `[fix]` | Bug修复 | `[fix] 修复列名映射异常` |
| `[perf]` | 性能优化 | `[perf] 优化 write_row 方法` |
| `[refactor]` | 代码重构 | `[refactor] 提取 helpers 模块` |
| `[docs]` | 文档更新 | `[docs] 更新 README.md` |
| `[test]` | 测试相关 | `[test] 增加单元测试` |
| `[chore]` | 构建/工具 | `[chore] 更新依赖版本` |

### 提交示例

```bash
# 好的提交
git commit -m "[feat] 增加批量下载图片功能"
git commit -m "[fix] 修复 write_row 在空值时的异常"
git commit -m "[test] 为 CellStyle 增加单元测试"

# 不好的提交
git commit -m "更新"
git commit -m "fix bug"
git commit -m "完成功能"
```

## 开发工作流

### 日常开发

```bash
# 1. 更新代码
git pull origin dev

# 2. 创建功能分支（可选）
git checkout -b feature/your-feature

# 3. 编写代码
# ... 编写你的代码 ...

# 4. 运行测试确保没有破坏现有功能
pytest tests/unit -v -m unit

# 5. 提交代码
git add .
git commit -m "[feat] 你的功能描述"

# 6. 推送代码（会自动运行测试）
git push origin dev
```

### 创建 Pull Request

```bash
# 1. 确保代码已推送到 dev 分支
git push origin dev

# 2. 在 GitHub 上创建 PR: dev → main
# 3. 等待 CI 测试通过
# 4. 代码审查通过后合并
```

## 常见问题

### Q1: 推送时测试失败怎么办？

```bash
# 查看测试失败原因
pytest tests/unit -v -m unit --tb=short

# 修复问题后重新推送
git push origin dev
```

### Q2: 如何跳过 pre-push 测试？

**不建议跳过**，但紧急情况下可以：

```bash
git push --no-verify origin dev
```

### Q3: 如何更新依赖？

```bash
# 更新项目依赖
pip install -r requirements.txt --upgrade
pip install -r requirements-dev.txt --upgrade

# 重新安装项目
pip install -e .
```

### Q4: pre-commit hook 没有生效？

```bash
# 重新安装 hooks
pre-commit install --hook-type pre-commit --hook-type pre-push

# 检查 hook 是否安装成功
ls -la .git/hooks/
```

## 测试覆盖率

当前测试覆盖率：**48%**（66个单元测试）

```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
fastfeishu/__init__.py                  1      0   100%
fastfeishu/core/sheet.py              250     95    62%
fastfeishu/core/operations.py         180     85    53%
fastfeishu/helpers.py                  45      8    82%
...
```

## 获取帮助

- 查看项目文档: `README.md`
- 查看代码规范: `CLAUDE.md`
- 提交 Issue: GitHub Issues
- 联系维护者: [维护者邮箱]

---

**记住**: 一键安装脚本 `./setup_dev.sh` 会帮你搞定所有配置，你只需要专注于写代码！🚀
