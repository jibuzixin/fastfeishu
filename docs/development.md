# 开发者指南

如果你想参与项目开发，请查看以下文档：

## 📖 必读文档

- **[开发者贡献指南](CONTRIBUTING.md)** - 开发工作流、测试流程、代码规范
- **[项目架构指南](ARCHITECTURE.md)** - 架构设计、设计模式、模块说明

## 🛠️ 快速参考

### Git 提交规范

所有提交信息必须遵循约定式提交格式：

```bash
git commit -m "[feat] 新功能描述"
git commit -m "[fix] Bug修复描述"
git commit -m "[docs] 文档更新"
```

**提交类型**: `[feat]` `[fix]` `[perf]` `[refactor]` `[docs]` `[test]` `[chore]` `[style]`

详细说明请参考 **[开发者贡献指南](CONTRIBUTING.md)**。

### 自动化测试

本项目配置了 pre-push hook，执行 `git push` 时会自动运行单元测试：

- ✅ 测试通过 → 推送成功
- ❌ 测试失败 → 推送被阻止

```bash
# 手动运行测试
pytest tests/unit -v -m unit

# 查看测试覆盖率
pytest tests/unit -v -m unit --cov=fastfeishu --cov-report=term-missing
```

### CI/CD

本项目使用 GitHub Actions 进行持续集成：

- **触发时机**: Pull Request 到 main/dev 分支
- **测试环境**: Python 3.11 和 3.12
- **状态查看**: [GitHub Actions](https://github.com/jibuzixin/fastfeishu/actions)

## 🏗️ 架构原则

本项目遵循严格的分层架构（从底到高）：

```
helpers.py (纯工具函数，零依赖)
   ↓
models/ (数据模型层)
   ↓
core/ (核心业务逻辑层)
   ↓
utils/ (高级工具层)
```

**重要规则**：
- `helpers.py` 永远不应导入项目内其他模块
- 低层模块不应导入高层模块
- 避免循环依赖

详细说明请参考 **[项目架构指南](ARCHITECTURE.md)**。

---
