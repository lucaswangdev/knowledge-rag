#!/bin/bash

echo "🚀 Knowledge-RAG 启动脚本"
echo "=========================="
echo ""

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，请先安装uv:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv已安装"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    uv venv --python 3.11
fi

echo "✓ 虚拟环境就绪"

# 同步依赖
echo "📦 同步依赖..."
uv sync

echo "✓ 依赖已同步"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在，从.env.example复制..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件配置数据库连接"
fi

echo "✓ 环境配置就绪"
echo ""

# 运行测试
echo "🧪 运行测试..."
uv run pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有测试通过！"
    echo ""
    echo "🌐 启动开发服务器..."
    echo "   访问 http://localhost:8000/docs 查看API文档"
    echo ""
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo ""
    echo "❌ 测试失败，请检查错误信息"
    exit 1
fi
