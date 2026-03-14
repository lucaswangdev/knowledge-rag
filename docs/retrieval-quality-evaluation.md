# RAG 系统向量检索质量评估框架

## 📋 目录

1. [评估指标体系](#评估指标体系)
2. [测试数据集设计](#测试数据集设计)
3. [评估实施方案](#评估实施方案)
4. [自动化评估脚本](#自动化评估脚本)
5. [生产环境标准](#生产环境标准)
6. [当前项目评估](#当前项目评估)
7. [改进建议](#改进建议)

---

## 📊 评估指标体系

### 核心指标（必须评估）

#### 1. Recall@K（召回率）
**定义：** Top-K 结果中包含相关文档的比例

```python
Recall@K = 相关文档出现在 Top-K 结果中的数量 / 总相关文档数量

示例：
- 查询："什么是RAG？"
- 相关文档总数：5
- Top-3 结果中包含：2 个相关文档
- Recall@3 = 2/5 = 0.4 (40%)
```

**重要性：** ⭐⭐⭐⭐⭐
**生产标准：**
- Recall@5 ≥ 80%（优秀）
- Recall@5 ≥ 60%（合格）
- Recall@5 < 40%（需改进）

---

#### 2. Precision@K（精确率）
**定义：** Top-K 结果中相关文档的比例

```python
Precision@K = Top-K 结果中相关文档数量 / K

示例：
- Top-3 结果：[相关, 不相关, 相关]
- Precision@3 = 2/3 = 0.67 (67%)
```

**重要性：** ⭐⭐⭐⭐⭐
**生产标准：**
- Precision@3 ≥ 70%（优秀）
- Precision@3 ≥ 50%（合格）
- Precision@3 < 30%（需改进）

---

#### 3. MRR (Mean Reciprocal Rank)
**定义：** 第一个相关结果的排名倒数的平均值

```python
RR = 1 / 第一个相关文档的排名
MRR = average(RR1, RR2, ..., RRn)

示例：
查询1：第一个相关文档在位置 1 → RR = 1/1 = 1.0
查询2：第一个相关文档在位置 3 → RR = 1/3 = 0.33
查询3：第一个相关文档在位置 2 → RR = 1/2 = 0.5
MRR = (1.0 + 0.33 + 0.5) / 3 = 0.61
```

**重要性：** ⭐⭐⭐⭐
**生产标准：**
- MRR ≥ 0.7（优秀）
- MRR ≥ 0.5（合格）
- MRR < 0.3（需改进）

---

#### 4. NDCG@K (Normalized Discounted Cumulative Gain)
**定义：** 考虑排序质量的评估指标

```python
DCG@K = Σ (rel_i / log2(i + 1))  # i 从 1 到 K
NDCG@K = DCG@K / IDCG@K

示例：
Top-3 结果的相关性分数：[3, 0, 2]（3=高度相关，2=相关，1=弱相关，0=不相关）
DCG@3 = 3/log2(2) + 0/log2(3) + 2/log2(4)
      = 3/1 + 0/1.58 + 2/2
      = 3 + 0 + 1 = 4.0

理想排序：[3, 2, 0]
IDCG@3 = 3 + 2/1.58 + 0 = 4.26
NDCG@3 = 4.0 / 4.26 = 0.94
```

**重要性：** ⭐⭐⭐⭐
**生产标准：**
- NDCG@5 ≥ 0.8（优秀）
- NDCG@5 ≥ 0.6（合格）
- NDCG@5 < 0.4（需改进）

---

### 辅助指标（推荐评估）

#### 5. Hit Rate@K（命中率）
**定义：** 至少有一个相关文档出现在 Top-K 的查询比例

```python
Hit@K = 至少有一个相关文档的查询数 / 总查询数

示例：
- 100 个查询
- 85 个查询在 Top-5 中至少有 1 个相关文档
- Hit@5 = 85/100 = 0.85 (85%)
```

**生产标准：** Hit@5 ≥ 90%

---

#### 6. F1-Score@K
**定义：** Precision 和 Recall 的调和平均

```python
F1@K = 2 × (Precision@K × Recall@K) / (Precision@K + Recall@K)
```

**生产标准：** F1@5 ≥ 0.6

---

#### 7. 查询响应时间
**定义：** 向量检索的平均响应时间

**生产标准：**
- P50 < 20ms（优秀）
- P95 < 50ms（合格）
- P99 < 100ms（可接受）

---

#### 8. 语义相似度分数
**定义：** 检索结果与查询的平均余弦相似度

```python
Average Similarity = Σ cosine_similarity(query, result_i) / K
```

**生产标准：**
- Top-3 平均相似度 ≥ 0.75（优秀）
- Top-3 平均相似度 ≥ 0.60（合格）

---

## 🧪 测试数据集设计

### 1. 标准测试集结构

```json
{
  "test_cases": [
    {
      "id": "test_001",
      "query": "什么是RAG检索增强生成？",
      "query_type": "定义型",
      "difficulty": "简单",
      "relevant_doc_ids": [1, 5, 12],
      "relevance_scores": {
        "1": 3,  // 高度相关
        "5": 2,  // 相关
        "12": 1  // 弱相关
      },
      "expected_top_3": [1, 5, 12],
      "domain": "AI技术"
    },
    {
      "id": "test_002",
      "query": "如何优化向量数据库的检索性能？",
      "query_type": "方法型",
      "difficulty": "中等",
      "relevant_doc_ids": [3, 7, 15, 23],
      "relevance_scores": {
        "3": 3,
        "7": 3,
        "15": 2,
        "23": 1
      },
      "expected_top_3": [3, 7, 15],
      "domain": "数据库优化"
    }
  ]
}
```

### 2. 测试集规模建议

| 阶段 | 测试用例数 | 覆盖范围 |
|------|-----------|---------|
| **最小可行** | 20-30 | 核心场景 |
| **基础评估** | 50-100 | 主要领域 |
| **完整评估** | 200-500 | 全面覆盖 |
| **生产级** | 1000+ | 持续监控 |

### 3. 查询类型覆盖

| 查询类型 | 占比 | 示例 |
|---------|------|------|
| **定义型** | 30% | "什么是RAG？"、"解释向量数据库" |
| **方法型** | 25% | "如何提升检索精度？"、"怎样优化性能？" |
| **对比型** | 15% | "RAG和微调的区别"、"比较向量数据库" |
| **列举型** | 15% | "RAG的优势有哪些？"、"常见问题包括" |
| **原因型** | 10% | "为什么使用向量检索？"、"性能下降原因" |
| **复杂型** | 5% | 多意图、长查询、模糊查询 |

### 4. 难度分级

- **简单 (40%)**：直接匹配、高频词汇、单一意图
- **中等 (40%)**：需要语义理解、同义词、多种表述
- **困难 (20%)**：复杂逻辑、领域专业、反问句

---

## 🔬 评估实施方案

### 阶段一：冷启动评估（最小数据集）

**目标：** 快速验证基本功能
**数据量：** 10-20 个文档 + 20-30 个查询

```python
# 测试步骤
1. 准备 10-20 个代表性文档（覆盖主要领域）
2. 设计 20-30 个典型查询
3. 人工标注相关文档
4. 运行评估脚本
5. 计算核心指标（Recall@5, Precision@3, MRR）
```

**通过标准：**
- Recall@5 ≥ 60%
- Precision@3 ≥ 40%
- MRR ≥ 0.4

---

### 阶段二：基准评估（中等数据集）

**目标：** 建立性能基准
**数据量：** 100-500 个文档 + 50-100 个查询

```python
# 测试内容
1. 覆盖所有查询类型
2. 包含不同难度级别
3. 测试边界情况
4. 性能压力测试
```

**通过标准：**
- Recall@5 ≥ 70%
- Precision@3 ≥ 50%
- MRR ≥ 0.5
- NDCG@5 ≥ 0.6
- P95 响应时间 < 50ms

---

### 阶段三：生产评估（完整数据集）

**目标：** 生产环境验证
**数据量：** 1000+ 个文档 + 200-500 个查询

```python
# 评估维度
1. 功能性：覆盖所有业务场景
2. 性能：大规模数据下的响应时间
3. 稳定性：长时间运行的一致性
4. 可扩展性：数据增长后的表现
```

**通过标准：**（见生产环境标准章节）

---

## 💻 自动化评估脚本

### 完整评估脚本

```python
# evaluation/evaluate_retrieval.py
import json
import time
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

class RetrievalEvaluator:
    """向量检索质量评估器"""

    def __init__(self, test_cases_file: str):
        """
        初始化评估器

        Args:
            test_cases_file: 测试用例JSON文件路径
        """
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            self.test_cases = json.load(f)['test_cases']

        self.results = defaultdict(list)

    def evaluate(self, retrieval_function, k_values: List[int] = [3, 5, 10]):
        """
        执行完整评估

        Args:
            retrieval_function: 检索函数，输入query和k，返回[(doc_id, score), ...]
            k_values: 要评估的K值列表

        Returns:
            评估结果字典
        """
        print("🚀 开始评估向量检索质量...\n")

        metrics = {}
        response_times = []

        for test_case in self.test_cases:
            query = test_case['query']
            relevant_doc_ids = set(test_case['relevant_doc_ids'])
            relevance_scores = test_case.get('relevance_scores', {})

            # 执行检索并计时
            start_time = time.time()
            retrieved_docs = retrieval_function(query, max(k_values))
            response_time = (time.time() - start_time) * 1000  # ms
            response_times.append(response_time)

            # 提取文档ID
            retrieved_ids = [doc_id for doc_id, _ in retrieved_docs]

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

            # MRR (只需计算一次)
            mrr = self._calculate_mrr(retrieved_ids, relevant_doc_ids)
            self.results['mrr'].append(mrr)

            # Hit Rate
            hit = 1 if any(doc_id in relevant_doc_ids for doc_id in retrieved_ids[:max(k_values)]) else 0
            self.results[f'hit@{max(k_values)}'].append(hit)

        # 聚合结果
        metrics = self._aggregate_results()
        metrics['performance'] = self._calculate_performance_metrics(response_times)

        # 打印结果
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
            dcg += rel / np.log2(i + 1)

        # IDCG (理想排序)
        ideal_scores = sorted(
            [int(score) for score in relevance_scores.values()],
            reverse=True
        )[:k]
        idcg = sum(score / np.log2(i + 2) for i, score in enumerate(ideal_scores))

        return dcg / idcg if idcg > 0 else 0.0

    def _aggregate_results(self) -> Dict:
        """聚合评估结果"""
        metrics = {}
        for metric_name, values in self.results.items():
            metrics[metric_name] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'median': np.median(values)
            }
        return metrics

    def _calculate_performance_metrics(self, response_times: List[float]) -> Dict:
        """计算性能指标"""
        return {
            'mean': np.mean(response_times),
            'p50': np.percentile(response_times, 50),
            'p95': np.percentile(response_times, 95),
            'p99': np.percentile(response_times, 99),
            'min': np.min(response_times),
            'max': np.max(response_times)
        }

    def _print_results(self, metrics: Dict):
        """打印评估结果"""
        print("\n" + "="*70)
        print("📊 评估结果总览")
        print("="*70)

        # 核心指标
        print("\n🎯 核心指标:")
        for k in [3, 5, 10]:
            if f'recall@{k}' in metrics:
                print(f"  Recall@{k}:    {metrics[f'recall@{k}']['mean']:.3f} ± {metrics[f'recall@{k}']['std']:.3f}")
                print(f"  Precision@{k}: {metrics[f'precision@{k}']['mean']:.3f} ± {metrics[f'precision@{k}']['std']:.3f}")
                if f'ndcg@{k}' in metrics:
                    print(f"  NDCG@{k}:      {metrics[f'ndcg@{k}']['mean']:.3f} ± {metrics[f'ndcg@{k}']['std']:.3f}")
                print()

        if 'mrr' in metrics:
            print(f"  MRR:           {metrics['mrr']['mean']:.3f} ± {metrics['mrr']['std']:.3f}")

        # 性能指标
        perf = metrics['performance']
        print("\n⚡ 性能指标:")
        print(f"  平均响应时间:  {perf['mean']:.2f} ms")
        print(f"  P50:           {perf['p50']:.2f} ms")
        print(f"  P95:           {perf['p95']:.2f} ms")
        print(f"  P99:           {perf['p99']:.2f} ms")

        # 生产环境判定
        print("\n✅ 生产环境标准判定:")
        self._evaluate_production_readiness(metrics)

        print("\n" + "="*70 + "\n")

    def _evaluate_production_readiness(self, metrics: Dict):
        """评估是否满足生产环境要求"""
        checks = []

        # Recall@5
        recall5 = metrics.get('recall@5', {}).get('mean', 0)
        if recall5 >= 0.8:
            checks.append(("✅ Recall@5 ≥ 80%", "优秀", recall5))
        elif recall5 >= 0.6:
            checks.append(("⚠️  Recall@5 ≥ 60%", "合格", recall5))
        else:
            checks.append(("❌ Recall@5 < 60%", "需改进", recall5))

        # Precision@3
        precision3 = metrics.get('precision@3', {}).get('mean', 0)
        if precision3 >= 0.7:
            checks.append(("✅ Precision@3 ≥ 70%", "优秀", precision3))
        elif precision3 >= 0.5:
            checks.append(("⚠️  Precision@3 ≥ 50%", "合格", precision3))
        else:
            checks.append(("❌ Precision@3 < 50%", "需改进", precision3))

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
            if isinstance(value, float) and value < 10:
                print(f"  {check}: {value:.3f} ({level})")
            else:
                print(f"  {check}: {value:.2f} ({level})")

        # 总体评估
        pass_count = sum(1 for c, _, _ in checks if "✅" in c)
        warn_count = sum(1 for c, _, _ in checks if "⚠️" in c)
        fail_count = sum(1 for c, _, _ in checks if "❌" in c)

        print(f"\n  总体评估: {pass_count} 项优秀, {warn_count} 项合格, {fail_count} 项需改进")

        if fail_count == 0 and pass_count >= 3:
            print("  🎉 推荐用于生产环境")
        elif fail_count == 0:
            print("  ✅ 可用于生产环境")
        elif fail_count <= 1:
            print("  ⚠️  需优化后再上生产")
        else:
            print("  ❌ 不建议用于生产环境")

    def _save_report(self, metrics: Dict):
        """保存详细报告"""
        report_path = "evaluation/retrieval_evaluation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"📄 详细报告已保存至: {report_path}")


# 使用示例
if __name__ == "__main__":
    from app.services.knowledge_service import search_knowledge

    # 包装检索函数
    def retrieval_function(query: str, k: int):
        """
        调用实际的检索接口
        返回: [(doc_id, similarity_score), ...]
        """
        result = search_knowledge(
            app_id="app_001",
            query=query,
            top_k=k
        )

        if result['success']:
            return [
                (item['document_id'], item['similarity'])
                for item in result['data']['results']
            ]
        return []

    # 执行评估
    evaluator = RetrievalEvaluator('evaluation/test_cases.json')
    metrics = evaluator.evaluate(retrieval_function, k_values=[3, 5, 10])
```

### 测试用例生成脚本

```python
# evaluation/generate_test_cases.py
import json
from typing import List, Dict

def generate_test_cases(documents: List[Dict]) -> Dict:
    """
    生成测试用例（需要人工标注）

    Args:
        documents: 文档列表 [{"id": 1, "title": "...", "content": "..."}, ...]

    Returns:
        测试用例模板
    """
    test_cases = {
        "test_cases": [],
        "metadata": {
            "total_documents": len(documents),
            "version": "1.0",
            "created_at": "2026-03-14"
        }
    }

    # 生成示例查询（需要人工替换为实际查询）
    sample_queries = [
        {
            "query": "TODO: 添加实际查询",
            "query_type": "定义型",  # 定义型/方法型/对比型/列举型/原因型
            "difficulty": "简单",  # 简单/中等/困难
            "relevant_doc_ids": [],  # TODO: 人工标注
            "relevance_scores": {},  # TODO: 人工标注 {"doc_id": score}
            "domain": "TODO: 领域标签"
        }
    ]

    test_cases["test_cases"] = sample_queries

    return test_cases

# 保存模板
template = generate_test_cases([])
with open('evaluation/test_cases_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)
```

---

## 🎯 生产环境标准

### 一级指标（核心指标）

| 指标 | 优秀 | 合格 | 需改进 | 权重 |
|------|------|------|--------|------|
| **Recall@5** | ≥ 80% | ≥ 60% | < 60% | 30% |
| **Precision@3** | ≥ 70% | ≥ 50% | < 50% | 25% |
| **MRR** | ≥ 0.7 | ≥ 0.5 | < 0.5 | 20% |
| **NDCG@5** | ≥ 0.8 | ≥ 0.6 | < 0.6 | 15% |
| **P95 响应时间** | < 50ms | < 100ms | ≥ 100ms | 10% |

### 二级指标（辅助指标）

| 指标 | 目标值 |
|------|--------|
| Hit Rate@5 | ≥ 90% |
| F1-Score@5 | ≥ 0.6 |
| 平均相似度分数 | ≥ 0.65 |
| P99 响应时间 | < 200ms |

### 生产环境准入标准

**必须满足（AND 关系）：**
1. ✅ Recall@5 ≥ 60%
2. ✅ Precision@3 ≥ 50%
3. ✅ MRR ≥ 0.5
4. ✅ P95 响应时间 < 100ms
5. ✅ 无数据泄露/安全问题

**推荐满足（优化方向）：**
- ⭐ 至少 3 项核心指标达到"优秀"级别
- ⭐ 所有一级指标至少达到"合格"级别
- ⭐ 在真实业务场景下验证通过

---

## 🔍 当前项目评估

### 评估配置

```yaml
项目: Knowledge-RAG
向量模型: bge-m3 (1024维)
向量数据库: PostgreSQL + pgvector (HNSW索引)
分块策略: 512字符/块
相似度度量: 余弦相似度
```

### 预估性能分析

基于 bge-m3 模型和 pgvector 的行业数据：

| 指标 | 预估值 | 评级 | 说明 |
|------|--------|------|------|
| **Recall@5** | 65-75% | 🟡 合格 | bge-m3 在中文语料上表现良好 |
| **Precision@3** | 55-65% | 🟡 合格 | 受分块质量影响 |
| **MRR** | 0.55-0.65 | 🟡 合格 | 首位相关文档排名较好 |
| **NDCG@5** | 0.60-0.70 | 🟡 合格 | 排序质量中等 |
| **P95 响应时间** | 20-40ms | 🟢 优秀 | HNSW索引高效 |

### 当前优势 ✅

1. **向量模型选择**
   - bge-m3 是当前中文领域 SOTA 模型之一
   - 支持多语言、跨领域检索
   - 1024 维向量平衡了精度和性能

2. **索引策略**
   - HNSW 索引提供 O(log N) 查询复杂度
   - 支持百万级向量高效检索
   - 响应时间 < 50ms

3. **数据库架构**
   - 多租户物理隔离保证安全性
   - pgvector 生态成熟，性能可靠
   - 易于运维和扩展

### 当前不足 ⚠️

1. **分块策略**
   - ❌ 固定 512 字符可能不适合所有文档
   - ❌ 缺少重叠分块（overlap）
   - ❌ 未考虑语义边界

2. **检索策略**
   - ❌ 仅使用密集向量（dense vector）
   - ❌ 未融合关键词检索（BM25）
   - ❌ 缺少重排序（rerank）机制

3. **评估体系**
   - ❌ 缺少自动化评估流程
   - ❌ 无线上质量监控
   - ❌ 缺少 A/B 测试能力

4. **元数据利用**
   - ❌ 检索时未充分利用 tags、source 等元数据
   - ❌ 缺少过滤和加权机制

### 生产环境就绪度评估

| 评估项 | 状态 | 说明 |
|--------|------|------|
| **基础功能** | ✅ 就绪 | 核心检索功能完整 |
| **性能** | ✅ 就绪 | 响应时间满足要求 |
| **准确性** | 🟡 基本就绪 | 预估指标达到合格线 |
| **监控** | ❌ 未就绪 | 缺少质量监控 |
| **可扩展性** | ✅ 就绪 | 架构设计良好 |
| **评估体系** | ❌ 未就绪 | 需建立评估流程 |

**总体结论：**
- ✅ 可用于**小规模生产环境**或**MVP 验证**
- ⚠️  需完善评估和监控后才能**大规模生产部署**
- 🎯 预估核心指标可达到**合格线**，但距离**优秀**还有优化空间

---

## 🚀 改进建议

### 短期优化（1-2周）

#### 1. 建立评估体系（最高优先级）
```python
# 立即行动
1. 创建 20-30 个测试用例
2. 部署自动化评估脚本
3. 运行首次基准评估
4. 记录当前性能基线
```

#### 2. 优化分块策略
```python
# 推荐方案
- 添加重叠分块（overlap=50-100字符）
- 根据语义边界切分（句子/段落）
- 保留上下文信息（前后句）

# 代码示例
def chunk_with_overlap(text: str, chunk_size: int = 512, overlap: int = 50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks
```

#### 3. 添加元数据过滤
```python
# 在检索时利用 tags、source 等信息
def search_with_filters(query, top_k, tags=None, source=None):
    # 先向量检索 top_k * 2
    # 然后根据元数据过滤
    # 最后返回 top_k
    pass
```

### 中期优化（1-2月）

#### 4. 混合检索（Hybrid Search）
```python
# 结合密集向量 + 关键词（BM25）
def hybrid_search(query, top_k, alpha=0.7):
    # alpha * 向量相似度 + (1-alpha) * BM25分数
    vector_results = dense_vector_search(query, top_k * 2)
    bm25_results = bm25_search(query, top_k * 2)

    # 融合结果（RRF: Reciprocal Rank Fusion）
    merged = merge_results(vector_results, bm25_results, alpha)
    return merged[:top_k]
```

**预期提升：**
- Recall@5: +5-10%
- Precision@3: +8-12%

#### 5. 重排序（Reranking）
```python
# 使用 Cross-Encoder 重排序 Top-K 结果
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')

def rerank_results(query, candidates, top_k):
    pairs = [[query, doc['text']] for doc in candidates]
    scores = reranker.predict(pairs)

    # 按新分数重排序
    reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in reranked[:top_k]]
```

**预期提升：**
- Precision@3: +10-15%
- NDCG@5: +8-12%

#### 6. 建立监控系统
```python
# 线上质量监控
- 实时跟踪平均相似度分数
- 监控 "无结果" 查询比例
- 记录用户点击率（CTR）
- A/B 测试不同策略
```

### 长期优化（3-6月）

#### 7. 模型微调
- 在自己的领域数据上微调 bge-m3
- 预期 Recall 提升 5-15%

#### 8. 查询理解
- 查询改写（Query Rewriting）
- 同义词扩展
- 意图识别

#### 9. 个性化检索
- 基于用户历史的个性化排序
- 领域自适应

---

## 📈 优化效果预估

| 优化项 | Recall@5 提升 | Precision@3 提升 | 实施难度 | 优先级 |
|--------|--------------|-----------------|---------|--------|
| 重叠分块 | +3-5% | +2-4% | 低 | ⭐⭐⭐ |
| 元数据过滤 | +2-4% | +3-5% | 低 | ⭐⭐⭐ |
| 混合检索 | +5-10% | +8-12% | 中 | ⭐⭐⭐⭐ |
| 重排序 | +3-5% | +10-15% | 中 | ⭐⭐⭐⭐⭐ |
| 模型微调 | +5-15% | +3-8% | 高 | ⭐⭐ |

**综合预期（实施前4项）：**
- Recall@5: 65-75% → **80-90%**（优秀）
- Precision@3: 55-65% → **75-85%**（优秀）
- NDCG@5: 0.60-0.70 → **0.75-0.85%**（优秀）

---

## 📝 实施路线图

### Week 1-2: 建立基线
- [ ] 创建测试数据集（20-30个用例）
- [ ] 部署评估脚本
- [ ] 运行首次评估，记录基线指标
- [ ] 识别最大问题点

### Week 3-4: 快速优化
- [ ] 实施重叠分块
- [ ] 添加元数据过滤
- [ ] 重新评估，对比提升

### Month 2: 混合检索
- [ ] 实现 BM25 检索
- [ ] 融合密集向量 + BM25
- [ ] 调优融合权重
- [ ] 评估效果

### Month 3: 重排序
- [ ] 集成 reranker 模型
- [ ] 优化 reranking 策略
- [ ] 性能优化（缓存、批处理）
- [ ] 生产环境部署

### Month 4+: 持续优化
- [ ] 建立线上监控
- [ ] A/B 测试
- [ ] 考虑模型微调
- [ ] 个性化检索

---

## 🎓 参考资源

### 学术论文
- [BGE-M3: Versatile Text Retrieval](https://arxiv.org/abs/2402.03216)
- [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906)
- [Measuring Search Effectiveness](https://dl.acm.org/doi/10.1145/3404835.3462951)

### 工具和框架
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - 向量模型排行榜
- [BEIR Benchmark](https://github.com/beir-cellar/beir) - 检索评估基准
- [LlamaIndex](https://www.llamaindex.ai/) - RAG 框架参考

### 最佳实践
- [Pinecone: RAG Evaluation Guide](https://www.pinecone.io/learn/)
- [Weaviate: Hybrid Search](https://weaviate.io/developers/weaviate/search/hybrid)
- [OpenAI: RAG Best Practices](https://platform.openai.com/docs/guides/embeddings)

---

*文档版本: v1.0*
*最后更新: 2026-03-14*
*项目: Knowledge-RAG Quality Evaluation Framework*
