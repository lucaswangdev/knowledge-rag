"""
Knowledge-RAG Skill 测试脚本

使用方式:
1. 确保 Knowledge-RAG 服务已启动 (http://localhost:8000)
2. 复制 config.example.json 为 config.json 并配置
3. 运行: python test_skill.py
"""

import sys
import json
from skill import KnowledgeRAGSkill


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_health_check(skill: KnowledgeRAGSkill):
    """测试健康检查"""
    print_section("1. 健康检查")

    if skill.check_health():
        print("✅ RAG 服务运行正常")
        return True
    else:
        print("❌ RAG 服务不可用")
        print("\n请先启动 Knowledge-RAG 服务:")
        print("  cd /path/to/knowledge-rag")
        print("  ./start.sh")
        return False


def test_search(skill: KnowledgeRAGSkill):
    """测试语义搜索"""
    print_section("2. 语义搜索测试")

    test_queries = [
        "字节跳动是谁创立的？",
        "创业初期最重要的是什么？",
        "如何进行产品验证？"
    ]

    for idx, query in enumerate(test_queries, 1):
        print(f"测试 {idx}/{len(test_queries)}: {query}")
        print("-" * 70)

        result = skill.search(query, top_k=3)

        if result.get('success'):
            data = result['data']
            print(f"✅ 找到 {len(data.get('results', []))} 个结果")

            formatted = skill.format_search_results(result)
            print("\n" + formatted)
        else:
            print(f"❌ 搜索失败: {result.get('message', 'Unknown error')}")

        print()


def test_chat(skill: KnowledgeRAGSkill):
    """测试 RAG 问答"""
    print_section("3. RAG 问答测试")

    test_questions = [
        "字节跳动的创始人是谁？",
        "根据知识库，天使轮融资需要注意什么？"
    ]

    for idx, question in enumerate(test_questions, 1):
        print(f"测试 {idx}/{len(test_questions)}: {question}")
        print("-" * 70)

        result = skill.chat(question, top_k=3)

        if result.get('success'):
            formatted = skill.format_chat_result(result)
            print("✅ 问答成功\n")
            print(formatted)
        else:
            print(f"❌ 问答失败: {result.get('message', 'Unknown error')}")

        print()


def test_trigger_keywords(skill: KnowledgeRAGSkill):
    """测试触发关键词"""
    print_section("4. 触发关键词测试")

    test_cases = [
        ("根据知识库，告诉我字节跳动的故事", True),
        ("查询文档中关于融资的内容", True),
        ("今天天气怎么样？", False),
        ("你好，请问你是谁？", False),
    ]

    for text, should_trigger in test_cases:
        triggered = skill.should_trigger(text)
        status = "✅" if triggered == should_trigger else "❌"

        print(f"{status} '{text}'")
        print(f"   预期触发: {should_trigger}, 实际触发: {triggered}")
        print()


def test_error_handling(skill: KnowledgeRAGSkill):
    """测试错误处理"""
    print_section("5. 错误处理测试")

    # 测试空查询
    print("测试1: 空查询")
    result = skill.search("", top_k=5)
    if not result.get('success'):
        print(f"✅ 正确处理错误: {result.get('message', 'Unknown')}")
    else:
        print("⚠️  应该返回错误，但返回了成功")
    print()

    # 测试无结果场景
    print("测试2: 查询不存在的内容")
    result = skill.search("xyzabc123不存在的内容", top_k=5)
    if result.get('success'):
        data = result['data']
        if not data.get('results'):
            print("✅ 正确处理无结果情况")
        else:
            print(f"⚠️  返回了 {len(data['results'])} 个结果")
    print()


def test_performance(skill: KnowledgeRAGSkill):
    """测试性能"""
    print_section("6. 性能测试")

    import time

    query = "字节跳动是什么公司？"
    times = []

    print(f"执行 5 次查询: '{query}'")
    print("-" * 70)

    for i in range(5):
        start = time.time()
        result = skill.search(query, top_k=5)
        end = time.time()

        elapsed = (end - start) * 1000  # 转换为毫秒
        times.append(elapsed)

        status = "✅" if result.get('success') else "❌"
        print(f"{status} 第 {i+1} 次: {elapsed:.2f}ms")

    print()
    print(f"平均响应时间: {sum(times)/len(times):.2f}ms")
    print(f"最快: {min(times):.2f}ms")
    print(f"最慢: {max(times):.2f}ms")


def test_config(skill: KnowledgeRAGSkill):
    """测试配置"""
    print_section("配置信息")

    config = skill.config

    print(f"Skill 名称: {config.get('skill_name')}")
    print(f"版本: {config.get('skill_version')}")
    print(f"API 地址: {config['api_config']['base_url']}")
    print(f"应用 ID: {config['auth']['app_id']}")
    print(f"默认 Top-K: {config['search_config']['default_top_k']}")
    print(f"相似度阈值: {config['search_config']['min_similarity_score']}")
    print(f"触发关键词数量: {len(config.get('trigger_keywords', []))}")


def main():
    """主测试函数"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║        Knowledge-RAG Skill for OpenClaw - 测试套件            ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # 加载配置
    try:
        skill = KnowledgeRAGSkill('config.json')
    except FileNotFoundError:
        print("❌ 错误: config.json 文件不存在")
        print("\n请先复制配置文件:")
        print("  cp config.example.json config.json")
        print("  vim config.json  # 修改 app_id 和 app_secret")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 错误: config.json 格式错误: {e}")
        sys.exit(1)

    # 显示配置
    test_config(skill)

    # 1. 健康检查
    if not test_health_check(skill):
        print("\n⚠️  由于服务不可用，跳过后续测试")
        sys.exit(1)

    # 2. 语义搜索测试
    test_search(skill)

    # 3. RAG 问答测试
    test_chat(skill)

    # 4. 触发关键词测试
    test_trigger_keywords(skill)

    # 5. 错误处理测试
    test_error_handling(skill)

    # 6. 性能测试
    test_performance(skill)

    # 总结
    print_section("测试完成")
    print("✅ 所有测试已完成")
    print("\n建议:")
    print("1. 检查上述测试结果，确保所有功能正常")
    print("2. 根据实际需求调整 config.json 中的参数")
    print("3. 集成到 OpenClaw 时，参考 skill.py 中的示例代码")


if __name__ == "__main__":
    main()
