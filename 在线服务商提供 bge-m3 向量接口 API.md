# 在线服务商提供 bge-m3 向量接口 API

**更新时间：** 2026-03-15

---

## 📋 概述

本文档汇总了可以替代本地 Ollama 的在线 bge-m3 向量接口 API 服务商，包括国际和国内服务商的详细对比、价格、集成方法和迁移指南。

**BGE-M3 简介：**
- 由北京智源人工智能研究院（BAAI）开发
- 支持 100+ 语言
- 三种检索功能：密集检索、稀疏检索、多向量检索
- 输入长度：最多 8192 tokens
- 向量维度：1024 维

---

## 🌍 国际服务商

### 1. DeepInfra ⭐⭐⭐⭐⭐

**API 地址：** `https://api.deepinfra.com/v1/embeddings`

**特点：**
- ✅ 完全兼容 OpenAI API 格式
- ✅ 支持 `BAAI/bge-m3` 和 `BAAI/bge-m3-multi`
- ✅ 按需付费，无需长期合约
- ✅ 提供详细的 API 文档

**价格：** 约 **$0.01 / 百万 tokens**

**文档：** [DeepInfra BGE-M3 API](https://deepinfra.com/BAAI/bge-m3/api)

**集成示例：**
```python
import openai

client = openai.OpenAI(
    api_key="your_deepinfra_api_key",
    base_url="https://api.deepinfra.com/v1"
)

def encode_query(text: str):
    response = client.embeddings.create(
        model="BAAI/bge-m3",
        input=text
    )
    return response.data[0].embedding  # 1024维向量
```

---

### 2. OpenRouter ⭐⭐⭐⭐

**API 地址：** `https://openrouter.ai/api/v1/embeddings`

**特点：**
- ✅ OpenAI 兼容格式
- ✅ 支持多个后端提供商（包括 DeepInfra）
- ✅ 8192 token 上下文窗口
- ✅ 自动路由到最佳提供商

**价格：** **$0.01 / 百万 input tokens**（output 免费）

**文档：** [OpenRouter bge-m3](https://openrouter.ai/baai/bge-m3)

**集成示例：**
```python
import openai

client = openai.OpenAI(
    api_key="your_openrouter_api_key",
    base_url="https://openrouter.ai/api/v1"
)

response = client.embeddings.create(
    model="baai/bge-m3",
    input="你的文本"
)
```

---

### 3. NVIDIA NIM ⭐⭐⭐⭐

**特点：**
- ✅ NVIDIA 优化的推理平台
- ✅ 专为文本检索优化
- ✅ 企业级 SLA 保障
- ✅ GPU 加速

**价格：** 需联系 NVIDIA 获取企业定价

**文档：** [NVIDIA NIM BGE-M3](https://build.nvidia.com/baai/bge-m3)

**适合场景：** 大规模企业部署，需要高性能和稳定性

---

## 🇨🇳 国内服务商

### 1. 硅基流动 (SiliconFlow) ⭐⭐⭐⭐⭐ **推荐**

**API 地址：** `https://api.siliconflow.cn/v1/embeddings`

**特点：**
- ✅ 国内访问速度快，无需翻墙
- ✅ 完全兼容 OpenAI API 格式
- ✅ 支持两个版本：
  - `BAAI/bge-m3` (免费版，有速率限制)
  - `Pro/BAAI/bge-m3` (付费加速版，更高并发)

**价格：**
- **免费版：** 免费使用，但有速率和并发限制
- **Pro 版：** 预估 **¥0.04-0.08 / 百万 tokens**（参考其他模型定价）

**文档：**
- [SiliconFlow 文档](https://docs.siliconflow.cn/cn/api-reference/embeddings/create-embeddings)
- [模型列表](https://cloud.siliconflow.cn/open/models?target=Pro/BAAI/bge-m3)

**集成示例：**
```python
import requests

class BGEService:
    def __init__(self):
        self.api_key = "your_siliconflow_api_key"
        self.base_url = "https://api.siliconflow.cn/v1"
        self.model = "Pro/BAAI/bge-m3"  # 或 "BAAI/bge-m3"

    def encode_query(self, text: str):
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": text,
                "encoding_format": "float"
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        return result['data'][0]['embedding']  # 1024维向量
```

**获取 API Key：**
1. 访问 [SiliconFlow 官网](https://www.siliconflow.cn/)
2. 注册账号
3. 在控制台创建 API Key
4. 选择免费版或 Pro 版

---

### 2. 阿里云 Model Studio ⭐⭐⭐⭐

**特点：**
- ✅ 基于 bge-m3 微调的向量模型
- ✅ 2024年3月在中文向量榜单排名第一
- ✅ 支持多种数据类型（文本、图像、视频）
- ✅ 企业级稳定性和安全性

**访问方式：**
- 通过阿里云百炼平台（Model Studio）
- 可从 ModelScope 下载模型进行本地部署

**价格：** 需要联系阿里云商务获取定价

**文档：** [阿里云向量化服务](https://help.aliyun.com/zh/model-studio/embedding)

**ModelScope 下载命令：**
```bash
modelscope download --model 'BAAI/bge-m3'
```

---

### 3. 自建部署 - 阿里云函数计算

**项目地址：** [fc-bge-m3-api](https://github.com/devsapp/fc-bge-m3-api)

**特点：**
- ✅ 使用 Serverless 架构
- ✅ 自主可控
- ✅ 按量计费
- ✅ 自动扩缩容

**部署方式：**
```bash
# 1. 安装 Serverless Devs
npm install -g @serverless-devs/s

# 2. 克隆项目
git clone https://github.com/devsapp/fc-bge-m3-api.git
cd fc-bge-m3-api

# 3. 部署到阿里云函数计算
s deploy
```

**适合场景：** 需要完全自主控制、数据安全要求高的企业

---

## 💰 价格对比总结

| 服务商 | 价格（每百万 tokens） | 访问速度（国内） | OpenAI 兼容 | 备注 |
|--------|---------------------|----------------|------------|------|
| **DeepInfra** | $0.01 (~¥0.07) | 较慢（需翻墙） | ✅ | 国际用户推荐 |
| **OpenRouter** | $0.01 (~¥0.07) | 较慢（需翻墙） | ✅ | 自动路由 |
| **NVIDIA NIM** | 企业定价 | 中等 | ✅ | 企业级 |
| **硅基流动 (免费版)** | 免费 | 快 | ✅ | 有速率限制 |
| **硅基流动 (Pro版)** | ¥0.04-0.08 | 快 | ✅ | **国内推荐** |
| **阿里云** | 需咨询 | 快 | ❌ | 企业定制 |
| **函数计算自建** | 按实例计费 | 快 | ✅ | 自主可控 |
| **本地 Ollama** | 免费 | 最快 | ❌ | 需要硬件 |

---

## 🚀 推荐方案

### 方案 1：硅基流动 Pro 版（国内推荐）✨

**适合场景：**
- 国内用户
- 需要稳定快速的服务
- 中小规模应用（日均 < 1000万 tokens）

**优势：**
- ✅ 访问速度快（国内 CDN）
- ✅ 价格合理（¥0.04-0.08/百万 tokens）
- ✅ OpenAI 兼容，迁移简单
- ✅ 提供免费版试用

**成本估算：**
```
假设日均 100万 tokens 向量化：
- 每日成本：¥0.04-0.08
- 每月成本：¥1.2-2.4
- 每年成本：¥14.4-28.8
```

---

### 方案 2：DeepInfra（国际推荐）

**适合场景：**
- 海外用户或有国际访问需求
- 需要稳定的国际服务
- 接受美元计费

**优势：**
- ✅ 国际访问速度快
- ✅ 价格透明（$0.01/百万 tokens）
- ✅ OpenAI 兼容
- ✅ 详细的 API 文档

**成本估算：**
```
假设日均 100万 tokens 向量化：
- 每日成本：$0.01 (~¥0.07)
- 每月成本：$0.30 (~¥2.1)
- 每年成本：$3.6 (~¥25.2)
```

---

### 方案 3：混合部署（大规模应用）

**适合场景：**
- 大规模企业应用
- 日均 > 1000万 tokens
- 需要高可用和灾备

**架构：**
```
主要流量：本地 Ollama（降低成本）
    ↓
高峰/备用：在线 API（硅基流动 Pro）
    ↓
灾备：DeepInfra（国际备份）
```

**优势：**
- ✅ 成本优化
- ✅ 高可用
- ✅ 灵活扩展

---

## 🔧 从 Ollama 迁移到在线 API

### 步骤 1: 修改配置文件

**编辑 `.env` 文件：**

```bash
# ======================================
# 向量化服务配置
# ======================================

# 选择向量化服务类型
# 可选值: ollama, siliconflow, deepinfra
EMBEDDING_API_TYPE=siliconflow

# === Ollama 配置（本地） ===
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_EMBED_MODEL=bge-m3

# === 硅基流动配置 ===
EMBEDDING_API_KEY=your_siliconflow_api_key_here
EMBEDDING_API_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=Pro/BAAI/bge-m3  # 或 BAAI/bge-m3 (免费版)

# === DeepInfra 配置 ===
# EMBEDDING_API_KEY=your_deepinfra_api_key_here
# EMBEDDING_API_BASE_URL=https://api.deepinfra.com/v1
# EMBEDDING_MODEL=BAAI/bge-m3

# 向量维度（保持不变）
VECTOR_DIMENSION=1024
```

---

### 步骤 2: 修改 `app/config.py`

```python
# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 向量化服务配置
    embedding_api_type: str = os.getenv('EMBEDDING_API_TYPE', 'ollama')

    # Ollama 配置
    ollama_base_url: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_embed_model: str = os.getenv('OLLAMA_EMBED_MODEL', 'bge-m3')

    # 在线 API 配置
    embedding_api_key: str = os.getenv('EMBEDDING_API_KEY', '')
    embedding_api_base_url: str = os.getenv('EMBEDDING_API_BASE_URL', '')
    embedding_model: str = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')

    # 向量维度
    vector_dimension: int = int(os.getenv('VECTOR_DIMENSION', '1024'))

    class Config:
        env_file = '.env'

settings = Settings()
```

---

### 步骤 3: 修改 `app/services/bge_service.py`

```python
# app/services/bge_service.py
import os
import requests
from typing import List
from app.config import settings

class BGEService:
    """向量化服务 - 支持多种后端"""

    def __init__(self):
        self.api_type = settings.embedding_api_type

        if self.api_type == 'siliconflow':
            self.api_key = settings.embedding_api_key
            self.base_url = settings.embedding_api_base_url
            self.model = settings.embedding_model
        elif self.api_type == 'deepinfra':
            self.api_key = settings.embedding_api_key
            self.base_url = settings.embedding_api_base_url
            self.model = settings.embedding_model
        else:  # ollama (默认)
            self.base_url = settings.ollama_base_url
            self.model = settings.ollama_embed_model

    def encode_query(self, text: str) -> List[float]:
        """
        将文本编码为向量

        Args:
            text: 输入文本

        Returns:
            1024维向量列表
        """
        if self.api_type in ['siliconflow', 'deepinfra']:
            return self._encode_openai_compatible(text)
        else:
            return self._encode_ollama(text)

    def _encode_openai_compatible(self, text: str) -> List[float]:
        """OpenAI 兼容格式（硅基流动、DeepInfra）"""
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": text,
                "encoding_format": "float"
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        return result['data'][0]['embedding']

    def _encode_ollama(self, text: str) -> List[float]:
        """Ollama 格式（原有方法）"""
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={
                "model": self.model,
                "input": text
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        return result['embeddings'][0]

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量编码文本

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if self.api_type in ['siliconflow', 'deepinfra']:
            # 在线 API 支持批量请求
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": texts,
                    "encoding_format": "float"
                },
                timeout=60
            )

            response.raise_for_status()
            result = response.json()
            return [item['embedding'] for item in result['data']]
        else:
            # Ollama 逐个编码
            return [self.encode_query(text) for text in texts]

# 全局实例
bge_service = BGEService()
```

---

### 步骤 4: 测试迁移

**测试向量化功能：**

```bash
# 测试语义搜索
curl -X POST "http://localhost:8000/api/v1/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "query": "字节跳动是什么公司？",
      "top_k": 3
    }
  }' | python3 -m json.tool
```

**预期输出：**
```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "query": "字节跳动是什么公司？",
        "total": 3,
        "results": [
            {
                "chunk_text": "张一鸣在2012年创立了字节跳动...",
                "document_id": 2,
                "document_title": "字节跳动创业故事",
                "similarity_score": 0.6812,
                "chunk_index": 0
            }
        ]
    }
}
```

---

### 步骤 5: 监控和优化

**添加日志记录：**

```python
# app/services/bge_service.py
import logging
import time

logger = logging.getLogger(__name__)

class BGEService:
    def encode_query(self, text: str) -> List[float]:
        start_time = time.time()

        try:
            if self.api_type in ['siliconflow', 'deepinfra']:
                result = self._encode_openai_compatible(text)
            else:
                result = self._encode_ollama(text)

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"向量化成功 [{self.api_type}] - 耗时: {elapsed:.2f}ms")

            return result

        except Exception as e:
            logger.error(f"向量化失败 [{self.api_type}]: {e}")
            raise
```

---

## ✅ 优势对比

### 本地 Ollama vs 在线 API

| 特性 | 本地 Ollama | 在线 API (硅基流动) |
|------|------------|-------------------|
| **成本** | 免费（需硬件投入） | 按量付费（低成本） |
| **速度** | 最快（本地网络） | 快（CDN 加速） |
| **可靠性** | 依赖本地环境 | 99.9% SLA |
| **扩展性** | 受限于硬件 | 无限扩展 |
| **维护** | 需要自己维护 | 服务商维护 |
| **访问控制** | 本地完全控制 | API Key 控制 |
| **数据安全** | 最高（不出本地） | 加密传输 |
| **初始部署** | 复杂（需安装配置） | 简单（API Key） |
| **多环境支持** | 每个环境需部署 | 统一 API |
| **成本弹性** | 固定成本 | 按实际使用付费 |

**推荐策略：**
- **开发/测试环境：** 使用本地 Ollama（快速迭代）
- **生产环境（小规模）：** 使用在线 API（稳定可靠）
- **生产环境（大规模）：** 混合部署（成本优化）

---

## 🔒 数据安全考虑

### 在线 API 数据安全问题

**问题：** 使用在线 API 时，文本数据会发送到第三方服务器

**解决方案：**

1. **敏感数据脱敏**
   ```python
   def sanitize_text(text: str) -> str:
       """移除敏感信息"""
       # 移除手机号、邮箱、身份证等
       text = re.sub(r'\d{11}', '[PHONE]', text)
       text = re.sub(r'\w+@\w+\.\w+', '[EMAIL]', text)
       return text
   ```

2. **本地缓存**
   ```python
   # 相同文本不重复请求
   from functools import lru_cache

   @lru_cache(maxsize=10000)
   def encode_query_cached(text: str):
       return bge_service.encode_query(text)
   ```

3. **混合模式**
   ```python
   def encode_query_smart(text: str):
       """敏感数据本地，一般数据在线"""
       if is_sensitive(text):
           return ollama_encode(text)  # 本地
       else:
           return online_api_encode(text)  # 在线
   ```

4. **私有部署**
   - 使用阿里云函数计算自建
   - 数据不离开自己的云账户

---

## 💡 成本优化建议

### 1. 批量请求

```python
# 不推荐：逐个请求
for text in texts:
    vector = bge_service.encode_query(text)

# 推荐：批量请求（节省网络开销）
vectors = bge_service.encode_batch(texts)
```

### 2. 缓存策略

```python
import redis

class CachedBGEService:
    def __init__(self):
        self.bge = BGEService()
        self.redis = redis.Redis(host='localhost', port=6379)

    def encode_query(self, text: str):
        # 检查缓存
        cache_key = f"vector:{hash(text)}"
        cached = self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        # 请求 API
        vector = self.bge.encode_query(text)

        # 保存缓存（24小时过期）
        self.redis.setex(cache_key, 86400, json.dumps(vector))

        return vector
```

### 3. 异步处理

```python
import asyncio
import httpx

class AsyncBGEService:
    async def encode_query(self, text: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": text}
            )
            return response.json()['data'][0]['embedding']

    async def encode_batch(self, texts: List[str]):
        tasks = [self.encode_query(text) for text in texts]
        return await asyncio.gather(*tasks)
```

---

## 📚 参考资源

### 官方文档

- [BGE-M3 官方文档](https://bge-model.com/bge/bge_m3.html)
- [BAAI/bge-m3 · Hugging Face](https://huggingface.co/BAAI/bge-m3)
- [BGE-M3 技术指南 | Zilliz](https://zilliz.com/ai-models/bge-m3)

### 服务商文档

**国际：**
- [DeepInfra BGE-M3 API 文档](https://deepinfra.com/BAAI/bge-m3/api)
- [OpenRouter BGE-M3 定价](https://openrouter.ai/baai/bge-m3)
- [NVIDIA NIM BGE-M3](https://build.nvidia.com/baai/bge-m3)

**国内：**
- [硅基流动 Embedding API](https://docs.siliconflow.cn/cn/api-reference/embeddings/create-embeddings)
- [硅基流动模型列表](https://cloud.siliconflow.cn/open/models?target=Pro/BAAI/bge-m3)
- [阿里云向量化服务](https://help.aliyun.com/zh/model-studio/embedding)
- [阿里云函数计算部署方案](https://github.com/devsapp/fc-bge-m3-api)

### 性能对比

- [OpenAI vs BGE-M3 对比](https://agentset.ai/embeddings/compare/openai-text-embedding-3-small-vs-baaibge-m3)
- [Voyage 3 vs BGE-M3 对比](https://agentset.ai/embeddings/compare/voyage-3-large-vs-baaibge-m3)

---

## ❓ 常见问题

### Q1: 在线 API 和本地 Ollama 生成的向量一样吗？

**A:** 是的，只要使用相同的 bge-m3 模型，生成的向量是完全一致的（相同文本 → 相同向量）。

### Q2: 如何选择免费版还是 Pro 版（硅基流动）？

**A:**
- **免费版：** 适合开发测试、小规模应用（QPS < 10）
- **Pro 版：** 适合生产环境、中大规模应用（QPS > 10，需要稳定性）

### Q3: 在线 API 会限速吗？

**A:** 会，各服务商有不同的速率限制：
- 硅基流动免费版：较低 QPS 限制
- 硅基流动 Pro 版：更高 QPS 限制
- DeepInfra：根据付费等级不同

### Q4: 如何处理 API 请求失败？

**A:** 实现重试机制：

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def encode_query_with_retry(text: str):
    return bge_service.encode_query(text)
```

### Q5: 可以同时使用多个服务商吗？

**A:** 可以，建议实现负载均衡或故障切换：

```python
class MultiBackendBGEService:
    def __init__(self):
        self.primary = SiliconFlowBGE()
        self.fallback = DeepInfraBGE()

    def encode_query(self, text: str):
        try:
            return self.primary.encode_query(text)
        except Exception as e:
            logger.warning(f"Primary failed, using fallback: {e}")
            return self.fallback.encode_query(text)
```

---

## 📊 总结与建议

### 推荐配置

| 应用规模 | 推荐方案 | 预估月成本 |
|---------|---------|-----------|
| **个人项目/学习** | 硅基流动免费版 | ¥0 |
| **小型应用** (日均 < 100万 tokens) | 硅基流动 Pro | ¥1-3 |
| **中型应用** (日均 100万-1000万 tokens) | 硅基流动 Pro + 缓存 | ¥5-20 |
| **大型应用** (日均 > 1000万 tokens) | 本地 Ollama + 在线 API 混合 | ¥20-100 |
| **企业级应用** | 自建 + 在线备份 | 定制化 |

### 最佳实践

1. ✅ **开发环境用本地，生产环境用在线**
2. ✅ **实现缓存机制，减少重复请求**
3. ✅ **使用批量请求接口**
4. ✅ **添加重试和降级策略**
5. ✅ **监控 API 调用量和成本**
6. ✅ **定期评估服务商价格和性能**

---

**文档维护：** Knowledge-RAG Team
**最后更新：** 2026-03-15
**版本：** v1.0
