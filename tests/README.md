# 测试目录

本目录包含 fastfeishu 项目的所有测试。

## 📚 文档

完整的测试文档已移至 `docs/` 目录：

- **[测试指南](../docs/TESTING.md)** - 单元测试编写指南和最佳实践
- **[集成测试指南](../docs/INTEGRATION_TESTS.md)** - 集成测试编写指南和示例

## 🚀 快速开始

```bash
# 运行所有单元测试
pytest tests/unit -v -m unit

# 查看测试覆盖率
pytest tests/unit -m unit --cov=fastfeishu --cov-report=html

# 运行集成测试（需要配置环境变量）
pytest tests/integration -v -m integration
```

## 📁 目录结构

```
tests/
├── conftest.py              # Pytest 配置和共享 fixtures
├── unit/                    # 单元测试（不依赖外部服务）
│   ├── test_*.py           # 各模块的单元测试
│   └── ...
└── integration/             # 集成测试（需要真实 API）
    ├── test_*.py           # 各功能的集成测试
    └── ...
```

## 📖 更多信息

请查看完整文档：
- [测试指南](../docs/TESTING.md)
- [集成测试指南](../docs/INTEGRATION_TESTS.md)
