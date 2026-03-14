"""
RAG系统向量检索质量评估脚本

使用方法:
    python evaluation/evaluate_retrieval.py

配置:
    - 测试用例文件: evaluation/test_cases.json
    - 评估报告输出: evaluation/reports/
"""

import json
import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
except ImportError:
    print("❌ 需要安装 numpy: pip install numpy")
    sys.exit(1)


class RetrievalEvaluator:
    """向量检索质量评估器"""

    def __init__(self, test_cases_file: str):
        """
        初始化评估器

        Args:
            test_cases_file: 测试用例JSON文件路径
        """
        if not os.path.exists(test_cases_file):
            print(f"❌ 测试用例文件不存在: {test_cases_file}")
            print(f"请先创建测试用例，参考: evaluation/test_cases_template.json")
            sys.exit(1)

        with open(test_cases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.test_cases = data.get('test_cases', [])
            self.metadata = data.get('metadata', {})

        if not self.test_cases:
            print(f"❌ 测试用例为空，请添加测试用例")
            sys.exit(1)

        self.results = defaultdict(list)
        print(f"✅ 加载了 {len(self.test_cases)} 个测试用例")

    def evaluate(self, retrieval_function, k_values: List[int] = [3, 5, 10]):
        """
        执行完整评估

        Args:
            retrieval_function: 检索函数，输入query和k，返回[(doc_id, score), ...]
            k_values: 要评估的K值列表

        Returns:
            评估结果字典
        """
        print("\n" + "="*70)
        print("🚀 开始评估向量检索质量")
        print("="*70)
        print(f"测试用例数: {len(self.test_cases)}")
        print(f"评估K值: {k_values}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        metrics = {}
        response_times = []
        failed_queries = []

        for i, test_case in enumerate(self.test_cases, 1):
            query = test_case['query']
            relevant_doc_ids = set(map(int, test_case['relevant_doc_ids']))
            relevance_scores = {
                str(k): int(v) for k, v in test_case.get('relevance_scores', {}).items()
            }

            print(f"[{i}/{len(self.test_cases)}] 评估: {query[:50]}...")

            try:
                # 执行检索并计时
                start_time = time.time()
                retrieved_docs = retrieval_function(query, max(k_values))
                response_time = (time.time() - start_time) * 1000  # ms
                response_times.append(response_time)

                # 提取文档ID
                if not retrieved_docs:
                    print(f"  ⚠️  无检索结果")
                    failed_queries.append(query)
                    continue

                retrieved_ids = [int(doc_id) for doc_id, _ in retrieved_docs]

                # 为每个K值计算指标
                for k in k_values:
                    top_k_ids = retrieved_ids[:k]

                    # Recall@K
                    recall = self._calculate_recall(top_k_ids, relevant_doc_ids)
                    self.results[f'recall@{k}'].append(recall)

                    # Precision@K
                    precision = self._calculate_precision(top_k_ids, relevant_doc_ids)
                    self.results[f'precision@{k}'].append(precision)

                    # NDCG@K
                    if relevance_scores:
                        ndcg = self._calculate_ndcg(top_k_ids, relevance_scores, k)
                        self.results[f'ndcg@{k}'].append(ndcg)

                # MRR
                mrr = self._calculate_mrr(retrieved_ids, relevant_doc_ids)
                self.results['mrr'].append(mrr)

                # Hit Rate
                hit = 1 if any(doc_id in relevant_doc_ids for doc_id in retrieved_ids[:max(k_values)]) else 0
                self.results[f'hit@{max(k_values)}'].append(hit)

                print(f"  ✓ Recall@5={recall:.2f}, Precision@3={precision:.2f}, 响应时间={response_time:.1f}ms")

            except Exception as e:
                print(f"  ❌ 评估失败: {e}")
                failed_queries.append(query)
                continue

        if not response_times:
            print("\n❌ 所有查询都失败了，请检查检索函数")
            return None

        # 聚合结果
        metrics = self._aggregate_results()
        metrics['performance'] = self._calculate_performance_metrics(response_times)
        metrics['summary'] = {
            'total_queries': len(self.test_cases),
            'successful_queries': len(response_times),
            'failed_queries': len(failed_queries),
            'failed_query_list': failed_queries
        }

        # 打印结果
        print("\n")
        self._print_results(metrics)

        # 保存详细报告
        self._save_report(metrics)

        return metrics

    def _calculate_recall(self, retrieved: List[int], relevant: set) -> float:
        """计算召回率"""
        if not relevant:
            return 0.0
        return len(set(retrieved) & relevant) / len(relevant)

    def _calculate_precision(self, retrieved: List[int], relevant: set) -> float:
        """计算精确率"""
        if not retrieved:
            return 0.0
        return len(set(retrieved) & relevant) / len(retrieved)

    def _calculate_mrr(self, retrieved: List[int], relevant: set) -> float:
        """计算MRR"""
        for i, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                return 1.0 / i
        return 0.0

    def _calculate_ndcg(self, retrieved: List[int], relevance_scores: Dict, k: int) -> float:
        """计算NDCG@K"""
        # DCG
        dcg = 0.0
        for i, doc_id in enumerate(retrieved[:k], 1):
            rel = int(relevance_scores.get(str(doc_id), 0))
            if rel > 0:
                dcg += rel / np.log2(i + 1)

        # IDCG
        ideal_scores = sorted(
            [int(score) for score in relevance_scores.values()],
            reverse=True
        )[:k]
        idcg = sum(score / np.log2(i + 2) for i, score in enumerate(ideal_scores) if score > 0)

        return dcg / idcg if idcg > 0 else 0.0

    def _aggregate_results(self) -> Dict:
        """聚合评估结果"""
        metrics = {}
        for metric_name, values in self.results.items():
            if values:
                metrics[metric_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }
        return metrics

    def _calculate_performance_metrics(self, response_times: List[float]) -> Dict:
        """计算性能指标"""
        return {
            'mean': float(np.mean(response_times)),
            'p50': float(np.percentile(response_times, 50)),
            'p95': float(np.percentile(response_times, 95)),
            'p99': float(np.percentile(response_times, 99)),
            'min': float(np.min(response_times)),
            'max': float(np.max(response_times))
        }

    def _print_results(self, metrics: Dict):
        """打印评估结果"""
        print("="*70)
        print("📊 评估结果总览")
        print("="*70)

        # 核心指标
        print("\n🎯 核心指标:")
        for k in [3, 5, 10]:
            if f'recall@{k}' in metrics:
                print(f"\n  Top-{k} 结果:")
                print(f"    Recall@{k}:    {metrics[f'recall@{k}']['mean']:.3f} ± {metrics[f'recall@{k}']['std']:.3f}")
                print(f"    Precision@{k}: {metrics[f'precision@{k}']['mean']:.3f} ± {metrics[f'precision@{k}']['std']:.3f}")
                if f'ndcg@{k}' in metrics:
                    print(f"    NDCG@{k}:      {metrics[f'ndcg@{k}']['mean']:.3f} ± {metrics[f'ndcg@{k}']['std']:.3f}")

        if 'mrr' in metrics:
            print(f"\n  MRR (平均倒数排名): {metrics['mrr']['mean']:.3f} ± {metrics['mrr']['std']:.3f}")

        # 性能指标
        perf = metrics['performance']
        print("\n⚡ 性能指标:")
        print(f"  平均响应时间:  {perf['mean']:.2f} ms")
        print(f"  中位数(P50):   {perf['p50']:.2f} ms")
        print(f"  P95:           {perf['p95']:.2f} ms")
        print(f"  P99:           {perf['p99']:.2f} ms")
        print(f"  最小/最大:     {perf['min']:.2f} / {perf['max']:.2f} ms")

        # 汇总统计
        summary = metrics.get('summary', {})
        print(f"\n📈 汇总统计:")
        print(f"  总查询数:      {summary.get('total_queries', 0)}")
        print(f"  成功查询:      {summary.get('successful_queries', 0)}")
        print(f"  失败查询:      {summary.get('failed_queries', 0)}")

        # 生产环境判定
        print("\n" + "="*70)
        print("✅ 生产环境标准判定")
        print("="*70)
        self._evaluate_production_readiness(metrics)

        print("\n" + "="*70 + "\n")

    def _evaluate_production_readiness(self, metrics: Dict):
        """评估是否满足生产环境要求"""
        checks = []

        # Recall@5
        recall5 = metrics.get('recall@5', {}).get('mean', 0)
        if recall5 >= 0.8:
            checks.append(("✅ Recall@5 ≥ 80%", "优秀", recall5 * 100))
        elif recall5 >= 0.6:
            checks.append(("⚠️  Recall@5 ≥ 60%", "合格", recall5 * 100))
        else:
            checks.append(("❌ Recall@5 < 60%", "需改进", recall5 * 100))

        # Precision@3
        precision3 = metrics.get('precision@3', {}).get('mean', 0)
        if precision3 >= 0.7:
            checks.append(("✅ Precision@3 ≥ 70%", "优秀", precision3 * 100))
        elif precision3 >= 0.5:
            checks.append(("⚠️  Precision@3 ≥ 50%", "合格", precision3 * 100))
        else:
            checks.append(("❌ Precision@3 < 50%", "需改进", precision3 * 100))

        # MRR
        mrr = metrics.get('mrr', {}).get('mean', 0)
        if mrr >= 0.7:
            checks.append(("✅ MRR ≥ 0.7", "优秀", mrr))
        elif mrr >= 0.5:
            checks.append(("⚠️  MRR ≥ 0.5", "合格", mrr))
        else:
            checks.append(("❌ MRR < 0.5", "需改进", mrr))

        # P95响应时间
        p95 = metrics['performance']['p95']
        if p95 < 50:
            checks.append(("✅ P95 < 50ms", "优秀", p95))
        elif p95 < 100:
            checks.append(("⚠️  P95 < 100ms", "合格", p95))
        else:
            checks.append(("❌ P95 ≥ 100ms", "需改进", p95))

        # 打印检查结果
        for check, level, value in checks:
            # 判断是否是响应时间指标（包含 "ms"）
            if "ms" in check:
                print(f"  {check}: {value:.2f}ms ({level})")
            elif isinstance(value, float) and value < 10:
                print(f"  {check}: {value:.3f} ({level})")
            else:
                print(f"  {check}: {value:.2f}% ({level})")

        # 总体评估
        pass_count = sum(1 for c, _, _ in checks if "✅" in c)
        warn_count = sum(1 for c, _, _ in checks if "⚠️" in c)
        fail_count = sum(1 for c, _, _ in checks if "❌" in c)

        print(f"\n  📊 总体评估: {pass_count} 项优秀, {warn_count} 项合格, {fail_count} 项需改进")

        if fail_count == 0 and pass_count >= 3:
            print("  🎉 系统表现优秀，推荐用于生产环境")
        elif fail_count == 0:
            print("  ✅ 系统表现合格，可用于生产环境")
        elif fail_count <= 1:
            print("  ⚠️  建议优化后再部署到生产环境")
        else:
            print("  ❌ 多项指标不达标，不建议用于生产环境")

    def _save_report(self, metrics: Dict):
        """保存详细报告"""
        # 创建报告目录
        report_dir = Path("evaluation/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        # 生成报告文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = report_dir / f"retrieval_evaluation_{timestamp}.json"

        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'metadata': self.metadata,
                'metrics': metrics
            }, f, indent=2, ensure_ascii=False)

        print(f"📄 详细报告已保存至: {report_path}")


def create_mock_retrieval_function():
    """创建模拟检索函数用于演示"""
    print("⚠️  使用模拟检索函数（仅供演示）")
    print("请在实际使用时替换为真实的检索函数\n")

    def mock_retrieval(query: str, k: int):
        """模拟检索函数"""
        import random
        # 模拟返回随机文档ID和分数
        doc_ids = list(range(1, 21))
        random.shuffle(doc_ids)
        results = [(doc_id, random.uniform(0.5, 0.99)) for doc_id in doc_ids[:k]]
        return sorted(results, key=lambda x: x[1], reverse=True)

    return mock_retrieval


def create_real_retrieval_function():
    """创建真实的检索函数"""
    print("✅ 使用真实的检索函数（Knowledge-RAG系统）\n")

    from app.services.knowledge_service import knowledge_service
    from app.services.db_service import db_router

    # 获取app_001的配置
    app_config = db_router.get_app_config("app_001")

    def real_retrieval(query: str, k: int):
        """真实检索函数"""
        try:
            result = knowledge_service.search(app_config, query, top_k=k)
            if result.get('results'):
                return [
                    (item['document_id'], item['similarity_score'])
                    for item in result['results']
                ]
        except Exception as e:
            print(f"  ⚠️  检索出错: {e}")
        return []

    return real_retrieval


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  RAG系统向量检索质量评估工具")
    print("="*70 + "\n")

    # 检查测试用例文件
    test_cases_file = "evaluation/test_cases.json"

    if not os.path.exists(test_cases_file):
        print(f"❌ 测试用例文件不存在: {test_cases_file}")
        print(f"\n请先创建测试用例:")
        print(f"  1. 复制模板: cp evaluation/test_cases_template.json {test_cases_file}")
        print(f"  2. 编辑测试用例，添加实际的查询和相关文档")
        print(f"  3. 重新运行此脚本\n")
        return

    # 初始化评估器
    evaluator = RetrievalEvaluator(test_cases_file)

    # 使用真实的检索函数
    try:
        retrieval_function = create_real_retrieval_function()
    except Exception as e:
        print(f"❌ 无法加载检索函数: {e}")
        print(f"请确保后端服务已启动，数据库已初始化\n")
        return

    # 执行评估
    metrics = evaluator.evaluate(retrieval_function, k_values=[3, 5, 10])

    if metrics:
        print("✅ 评估完成!")
        print("\n💡 后续步骤:")
        print("  1. 查看详细报告: evaluation/reports/")
        print("  2. 根据评估结果优化检索策略")
        print("  3. 重新评估，跟踪改进效果")


if __name__ == "__main__":
    main()
