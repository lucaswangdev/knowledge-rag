"""
Knowledge-RAG Skill for OpenClaw
企业级私有知识库 RAG 检索技能

作者: Knowledge-RAG Team
版本: 1.0.0
日期: 2026-03-14
"""

import requests
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class SearchResult:
    """搜索结果"""
    chunk_text: str
    document_id: int
    document_title: str
    similarity_score: float
    chunk_index: int


@dataclass
class ChatResult:
    """问答结果"""
    answer: str
    sources: List[SearchResult]
    session_id: Optional[int] = None


class KnowledgeRAGSkill:
    """Knowledge-RAG Skill 主类"""

    def __init__(self, config_path: str = "config.json"):
        """
        初始化 RAG Skill

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.base_url = self.config['api_config']['base_url']
        self.timeout = self.config['api_config']['timeout']
        self.retry = self.config['api_config']['retry']
        self.app_id = self.config['auth']['app_id']
        self.app_secret = self.config['auth']['app_secret']

    def should_trigger(self, user_input: str) -> bool:
        """
        判断是否需要调用 RAG

        Args:
            user_input: 用户输入

        Returns:
            是否触发 RAG 检索
        """
        # 检查触发关键词
        keywords = self.config.get('trigger_keywords', [])
        for keyword in keywords:
            if keyword in user_input:
                return True

        # 这里可以集成更复杂的意图识别逻辑
        # 例如：使用分类器判断是否是专业知识问题
        return False

    def search(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        语义搜索

        Args:
            query: 查询内容
            top_k: 返回结果数量

        Returns:
            搜索结果字典
        """
        if top_k is None:
            top_k = self.config['search_config']['default_top_k']

        url = f"{self.base_url}/api/v1/knowledge/search"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
            "data": {
                "query": query,
                "top_k": top_k
            }
        }

        for attempt in range(self.retry):
            try:
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == self.retry - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "message": "RAG 服务请求失败"
                    }
                continue

    def chat(
        self,
        query: str,
        session_id: Optional[int] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        RAG 问答

        Args:
            query: 问题内容
            session_id: 会话ID（用于多轮对话）
            top_k: 参考文档数量

        Returns:
            问答结果字典
        """
        if top_k is None:
            top_k = self.config['chat_config']['default_top_k']

        url = f"{self.base_url}/api/v1/knowledge/chat"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
            "data": {
                "query": query,
                "top_k": top_k
            }
        }

        if session_id is not None:
            payload['data']['session_id'] = session_id

        for attempt in range(self.retry):
            try:
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == self.retry - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "message": "RAG 服务请求失败"
                    }
                continue

    def format_search_results(self, result: Dict[str, Any]) -> str:
        """
        格式化搜索结果

        Args:
            result: API 返回的搜索结果

        Returns:
            格式化后的文本
        """
        if not result.get('success'):
            return self.config['response_template']['error']

        data = result.get('data', {})
        results = data.get('results', [])

        if not results:
            return self.config['response_template']['no_results']

        # 过滤低相似度结果
        min_score = self.config['search_config']['min_similarity_score']
        filtered = [r for r in results if r['similarity_score'] >= min_score]

        if not filtered:
            return self.config['response_template']['no_results']

        # 格式化输出
        output = []
        for idx, r in enumerate(filtered, 1):
            output.append(
                f"{idx}. 《{r['document_title']}》\n"
                f"   相似度: {r['similarity_score']*100:.1f}%\n"
                f"   内容: {r['chunk_text'][:100]}..."
            )

        return "\n\n".join(output)

    def format_chat_result(self, result: Dict[str, Any]) -> str:
        """
        格式化问答结果

        Args:
            result: API 返回的问答结果

        Returns:
            格式化后的文本
        """
        if not result.get('success'):
            return self.config['response_template']['error']

        data = result.get('data', {})
        answer = data.get('answer', '')
        sources = data.get('sources', [])

        if not sources:
            return answer

        # 格式化来源
        sources_text = []
        for idx, s in enumerate(sources, 1):
            sources_text.append(
                f"{idx}. 《{s['document_title']}》- 相似度: {s['similarity_score']*100:.1f}%"
            )

        template = self.config['response_template']['with_sources']
        return template.format(
            answer=answer,
            sources='\n'.join(sources_text)
        )

    def check_health(self) -> bool:
        """
        检查 RAG 服务健康状态

        Returns:
            服务是否健康
        """
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    """示例：如何在 OpenClaw 中使用 RAG Skill"""

    # 1. 初始化 Skill
    skill = KnowledgeRAGSkill('config.json')

    # 2. 检查服务健康状态
    if not skill.check_health():
        print("❌ RAG 服务不可用，请先启动 Knowledge-RAG 服务")
        return

    print("✅ RAG 服务连接成功\n")

    # 3. 模拟用户提问
    user_questions = [
        "字节跳动是谁创立的？",
        "根据知识库，告诉我创业初期最重要的是什么？",
        "天使轮融资需要注意什么？"
    ]

    for question in user_questions:
        print(f"💬 用户: {question}")
        print("-" * 60)

        # 判断是否需要使用 RAG
        if skill.should_trigger(question):
            print("🔍 触发关键词，使用 RAG 检索...\n")

            # 方式1: 使用搜索接口
            search_result = skill.search(question, top_k=3)
            print("📚 搜索结果:")
            print(skill.format_search_results(search_result))
            print()

            # 方式2: 使用问答接口（推荐）
            chat_result = skill.chat(question, top_k=3)
            print("💡 RAG 回答:")
            print(skill.format_chat_result(chat_result))

        else:
            print("🤖 OpenClaw 直接回答（不使用 RAG）")
            # 这里调用 OpenClaw 自己的回答逻辑

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
