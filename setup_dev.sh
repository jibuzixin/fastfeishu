#!/bin/bash

# ========================================
# fastfeishu 开发环境自动配置脚本
# ========================================
# 这个脚本会帮助你完成以下操作：
# 1. 检查 Python 环境
# 2. 安装项目依赖
# 3. 安装测试工具（pytest）
# 4. 配置 Git hooks（自动运行测试）
# ========================================

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} ${1}"
}

print_error() {
    echo -e "${RED}✗${NC} ${1}"
}

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  fastfeishu 开发环境配置工具${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 主函数
main() {
    print_header

    # 步骤 1: 检查 Python 环境
    print_step "步骤 1/4: 检查 Python 环境..."

    if ! command_exists python3; then
        print_error "未找到 Python3，请先安装 Python 3.11+"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "已找到 Python ${PYTHON_VERSION}"

    # 检查 Python 版本是否 >= 3.11
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        print_warning "推荐使用 Python 3.11+，当前版本为 ${PYTHON_VERSION}"
        read -p "是否继续安装？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "安装已取消"
            exit 1
        fi
    fi

    # 步骤 2: 安装项目依赖
    print_step "步骤 2/4: 安装项目依赖..."
    echo "   这可能需要几分钟，请耐心等待..."

    if [ -f "requirements.txt" ]; then
        print_step "   正在安装生产依赖..."
        python3 -m pip install --upgrade pip -q
        python3 -m pip install -r requirements.txt -q
        print_success "生产依赖安装完成"
    else
        print_warning "未找到 requirements.txt 文件"
    fi

    if [ -f "requirements-dev.txt" ]; then
        print_step "   正在安装开发依赖（包含 pytest 等测试工具）..."
        python3 -m pip install -r requirements-dev.txt -q
        print_success "开发依赖安装完成"
    else
        print_warning "未找到 requirements-dev.txt 文件"
    fi

    # 安装项目本身（可编辑模式）
    print_step "   正在安装 fastfeishu 包（可编辑模式）..."
    python3 -m pip install -e . -q
    print_success "fastfeishu 包安装完成"

    # 步骤 3: 安装 pre-commit
    print_step "步骤 3/4: 安装 pre-commit 工具..."
    echo "   pre-commit 会在你提交代码时自动运行格式检查"
    echo "   在你推送代码时自动运行单元测试"

    if ! command_exists pre-commit; then
        python3 -m pip install pre-commit -q
        print_success "pre-commit 安装完成"
    else
        print_success "pre-commit 已安装"
    fi

    # 步骤 4: 配置 Git hooks
    print_step "步骤 4/4: 配置 Git hooks..."

    if [ ! -d ".git" ]; then
        print_error "当前目录不是 Git 仓库，请在项目根目录运行此脚本"
        exit 1
    fi

    if [ -f ".pre-commit-config.yaml" ]; then
        print_step "   正在安装 Git hooks..."
        pre-commit install --hook-type pre-commit --hook-type pre-push
        print_success "Git hooks 配置完成"

        # 显示配置的 hooks 信息
        echo ""
        echo -e "${BLUE}已配置的 Git hooks:${NC}"
        echo "   • pre-commit: 代码提交时自动检查格式（行尾空格、YAML语法等）"
        echo "   • pre-push: 代码推送时自动运行单元测试"
    else
        print_warning "未找到 .pre-commit-config.yaml 文件"
    fi

    # 完成提示
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ 开发环境配置完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}接下来你可以：${NC}"
    echo "  1. 开始编写代码"
    echo "  2. 使用 'git commit' 提交代码（会自动检查格式）"
    echo "  3. 使用 'git push' 推送代码（会自动运行测试）"
    echo ""
    echo -e "${YELLOW}注意：${NC}"
    echo "  • 如果单元测试不通过，代码将无法推送"
    echo "  • 如果格式检查不通过，代码将无法提交"
    echo "  • 你可以手动运行 'pytest tests/unit -v' 来测试"
    echo ""
    echo -e "${BLUE}测试一下：${NC}"
    read -p "是否现在运行一次单元测试？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "运行单元测试..."
        if command_exists pytest; then
            pytest tests/unit -v -m unit --tb=short || true
        else
            print_error "pytest 未安装或不在 PATH 中"
        fi
    fi

    echo ""
    print_success "全部完成！祝你编码愉快 🚀"
    echo ""
}

# 执行主函数
main "$@"
