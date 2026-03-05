#!/usr/bin/env python3
"""
集成测试配置验证脚本

快速检查集成测试配置是否正确。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def check_env_file():
    """检查 .env 文件是否存在"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    if os.path.exists(env_path):
        print("✅ .env 文件存在")
        return True
    else:
        print("⚠️  .env 文件不存在")
        print("   建议: cp .env.example .env")
        return False


def check_dotenv_installed():
    """检查 python-dotenv 是否安装"""
    try:
        import dotenv
        print("✅ python-dotenv 已安装")
        return True
    except ImportError:
        print("❌ python-dotenv 未安装")
        print("   安装: pip install python-dotenv")
        return False


def check_integration_config():
    """检查集成测试配置"""
    try:
        from tests.integration.config import (
            IntegrationTestConfig,
            list_available_sheets
        )

        print("\n" + "=" * 60)
        print("集成测试配置状态：")
        print("=" * 60)

        list_available_sheets()

        # 检查至少有一个表格配置
        configured_count = sum(
            1 for name in IntegrationTestConfig.DEFAULT_SHEETS.keys()
            if IntegrationTestConfig.is_configured(name)
        )

        print("\n" + "=" * 60)
        if configured_count > 0:
            print(f"✅ 配置检查通过！已配置 {configured_count} 个测试表格")
            return True
        else:
            print("⚠️  没有配置任何测试表格")
            print("   至少需要配置 FS_TEST_MAIN_URL 才能运行集成测试")
            return False

    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_connection():
    """测试飞书 API 连接"""
    from tests.integration.config import IntegrationTestConfig

    if not IntegrationTestConfig.is_configured("main"):
        print("\n⚠️  跳过连接测试（main 表格未配置）")
        return True

    try:
        from fastfeishu.core import FeiShuSheet

        print("\n" + "=" * 60)
        print("测试飞书 API 连接...")
        print("=" * 60)

        url = IntegrationTestConfig.get_sheet_url("main")
        sheet = FeiShuSheet(url, readonly=True)

        # 尝试获取表格信息
        info = sheet.get_sheet_info()
        print(f"✅ 连接成功！")
        print(f"   表格标题: {info.get('title', 'N/A')}")
        print(f"   行数: {info['rowCount']}")
        print(f"   列数: {info['columnCount']}")

        # 尝试读取表头
        header = sheet.get_header()
        print(f"   表头: {header[:5]}{'...' if len(header) > 5 else ''}")

        return True

    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        print("\n请检查：")
        print("  1. FS_APP_ID 和 FS_APP_SECRET 是否正确")
        print("  2. FS_TEST_MAIN_URL 是否正确")
        print("  3. 飞书应用是否有权限访问该表格")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("FastFeishu 集成测试配置验证")
    print("=" * 60)

    all_pass = True

    # 1. 检查 .env 文件
    print("\n[1/4] 检查 .env 文件...")
    check_env_file()  # 不强制要求

    # 2. 检查依赖
    print("\n[2/4] 检查依赖...")
    if not check_dotenv_installed():
        all_pass = False

    # 3. 检查配置
    print("\n[3/4] 检查集成测试配置...")
    if not check_integration_config():
        all_pass = False

    # 4. 测试连接（可选）
    print("\n[4/4] 测试飞书 API 连接...")
    if not test_connection():
        all_pass = False

    # 总结
    print("\n" + "=" * 60)
    if all_pass:
        print("🎉 所有检查通过！可以运行集成测试了")
        print("\n运行集成测试:")
        print("  pytest tests/integration -v -m integration")
    else:
        print("⚠️  部分检查失败，请根据上述提示修复问题")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
