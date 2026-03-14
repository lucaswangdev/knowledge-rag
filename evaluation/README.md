# 向量检索质量评估

本目录包含向量检索质量评估相关的脚本和测试用例。

## 📁 文件说明

- `evaluate_retrieval.py` - 评估脚本
- `test_cases_template.json` - 测试用例模板
- `test_cases.json` - 实际测试用例（需要自己创建）
- `reports/` - 评估报告输出目录

## 🚀 快速开始

### 1. 创建测试用例

```bash
# 复制模板
cp evaluation/test_cases_template.json evaluation/test_cases.json

# 编辑测试用例
# 根据实际文档修改 relevant_doc_ids 和 relevance_scores
```

### 2. 运行评估

```bash
# 安装依赖
pip install numpy

# 运行评估脚本
python evaluation/evaluate_retrieval.py
```

### 3. 查看结果

评估完成后，查看：
- 终端输出：核心指标和生产环境判定
- `reports/` 目录：详细的JSON报告

## 📊 测试用例格式

```json
{
  "id": "test_001",
  "query": "查询问题",
  "query_type": "定义型",
  "difficulty": "简单",
  "relevant_doc_ids": [1, 5, 12],
  "relevance_scores": {
    "1": 3,  // 高度相关
    "5": 2,  // 相关
    "12": 1  // 弱相关
  },
  "expected_top_3": [1, 5, 12],
  "domain": "领域标签"
}
```

## 🎯 评估指标

- **Recall@K**: 召回率
- **Precision@K**: 精确率
- **MRR**: 平均倒数排名
- **NDCG@K**: 归一化折损累积增益
- **响应时间**: P50, P95, P99

## 📈 生产环境标准

| 指标 | 优秀 | 合格 | 需改进 |
|------|------|------|--------|
| Recall@5 | ≥ 80% | ≥ 60% | < 60% |
| Precision@3 | ≥ 70% | ≥ 50% | < 50% |
| MRR | ≥ 0.7 | ≥ 0.5 | < 0.5 |
| P95 响应时间 | < 50ms | < 100ms | ≥ 100ms |

## 💡 使用建议

1. **最小测试集**：20-30 个用例（快速验证）
2. **基础评估**：50-100 个用例（建立基准）
3. **完整评估**：200-500 个用例（生产验证）

## 🔧 集成到实际项目

在 `evaluate_retrieval.py` 中替换模拟检索函数：

```python
from app.services.knowledge_service import search_knowledge

def retrieval_function(query: str, k: int):
    """调用实际的检索接口"""
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
metrics = evaluator.evaluate(retrieval_function)
```

## 📚 参考文档

详细评估方法和优化建议，请参考：
- `docs/retrieval-quality-evaluation.md` - 完整评估框架文档
