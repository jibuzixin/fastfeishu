"""
集成测试配置管理

统一管理所有集成测试使用的飞书表格链接。

使用方式：
    1. 在项目根目录创建 .env 文件，添加测试表格链接
    2. 或者直接在此文件中修改 DEFAULT_SHEETS 字典

环境变量优先级：
    环境变量 > .env 文件 > 代码中的默认值
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class TestSheet:
    """测试表格配置"""
    name: str  # 表格名称（用于标识）
    url: str   # 表格链接
    description: str  # 用途描述


class IntegrationTestConfig:
    """集成测试配置类"""

    # 默认测试表格配置
    # 实际使用时从环境变量 FS_TEST_MAIN_URL 读取
    DEFAULT_SHEETS: Dict[str, TestSheet] = {
        "main": TestSheet(
            name="main",
            url="https://li.feishu.cn/sheets/MmhVstjxEhDuY9tV0wEcrdiNnBh",
            description="主要测试表格，用于大部分读测试"
        ),
        "write_row_smart": TestSheet(
            name="write_row_smart",
            url="https://li.feishu.cn/sheets/MmhVstjxEhDuY9tV0wEcrdiNnBh?sheet=2JoFMu",
            description="用于 write_row_smart 测试"
        )
    }

    @classmethod
    def get_sheet_url(cls, sheet_name: str) -> str:
        """
        获取指定测试表格的 URL

        优先级：环境变量 > 默认配置

        Args:
            sheet_name: 表格名称（如 'main', 'batch_operations'）

        Returns:
            表格 URL

        Raises:
            ValueError: 如果表格未配置
        """
        # 环境变量名称：FS_TEST_{SHEET_NAME}_URL
        env_key = f"FS_TEST_{sheet_name.upper()}_URL"
        url = os.getenv(env_key)

        if url:
            return url

        # 如果环境变量不存在，使用默认配置
        if sheet_name in cls.DEFAULT_SHEETS:
            default_url = cls.DEFAULT_SHEETS[sheet_name].url
            # 检查是否是占位符
            if "YOUR_" in default_url:
                raise ValueError(
                    f"测试表格 '{sheet_name}' 未配置。\n"
                    f"请设置环境变量 {env_key} 或在 tests/integration/config.py 中修改默认值。"
                )
            return default_url

        raise ValueError(f"未知的测试表格名称: {sheet_name}")

    @classmethod
    def get_all_sheets(cls) -> Dict[str, str]:
        """获取所有配置的测试表格"""
        result = {}
        for name in cls.DEFAULT_SHEETS.keys():
            try:
                result[name] = cls.get_sheet_url(name)
            except ValueError:
                # 跳过未配置的表格
                pass
        return result

    @classmethod
    def is_configured(cls, sheet_name: str) -> bool:
        """检查指定表格是否已配置"""
        try:
            url = cls.get_sheet_url(sheet_name)
            return "YOUR_" not in url
        except ValueError:
            return False

    @classmethod
    def get_description(cls, sheet_name: str) -> str:
        """获取表格用途描述"""
        if sheet_name in cls.DEFAULT_SHEETS:
            return cls.DEFAULT_SHEETS[sheet_name].description
        return "未知表格"


# 便捷函数
def get_test_sheet_url(sheet_name: str = "main") -> str:
    """
    获取测试表格 URL（便捷函数）

    Args:
        sheet_name: 表格名称，默认 'main'

    Returns:
        表格 URL

    Example:
        >>> url = get_test_sheet_url("main")
        >>> sheet = FeiShuSheet(url)
    """
    return IntegrationTestConfig.get_sheet_url(sheet_name)


def list_available_sheets() -> None:
    """列出所有可用的测试表格"""
    print("=" * 60)
    print("可用的测试表格：")
    print("=" * 60)

    for name, sheet in IntegrationTestConfig.DEFAULT_SHEETS.items():
        is_configured = IntegrationTestConfig.is_configured(name)
        status = "✅ 已配置" if is_configured else "❌ 未配置"

        print(f"\n{name} - {status}")
        print(f"  描述: {sheet.description}")
        print(f"  标记名: {name.upper()}")

        if is_configured:
            try:
                url = IntegrationTestConfig.get_sheet_url(name)
                # 只显示部分 URL，保护隐私
                masked_url = url[:30] + "..." if len(url) > 30 else url
                print(f"  URL: {masked_url}")
            except ValueError:
                pass

    print("\n" + "=" * 60)
    print("配置方式：")
    print("  1. 在项目根目录创建 .env 文件")
    print("  2. 添加环境变量，例如：")
    print("     FS_TEST_MAIN_URL=https://li.feishu.cn/sheets/YOUR_SHEET_TOKEN")
    print("=" * 60)


if __name__ == "__main__":
    # 运行此文件可以查看当前配置状态
    list_available_sheets()
