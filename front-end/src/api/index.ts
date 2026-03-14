import { useAppStore } from '../store/useAppStore';

const API_BASE_URL = 'http://localhost:8000';

interface ApiResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T;
}

// 文件上传
export async function uploadDocument(file: File, title: string, tags: string[]): Promise<any> {
  const { config } = useAppStore.getState();
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('app_id', config.appId);
  formData.append('app_secret', config.appSecret);
  formData.append('title', title);
  formData.append('tags', tags.join(','));
  formData.append('source', 'file');
  
  const response = await fetch(`${API_BASE_URL}/api/v1/document/upload`, {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
}

// 获取文档列表
export async function getDocumentList(page = 1, pageSize = 10): Promise<any> {
  const { config } = useAppStore.getState();
  
  const response = await fetch(`${API_BASE_URL}/api/v1/document/list`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      app_id: config.appId,
      app_secret: config.appSecret,
      data: { page, page_size: pageSize },
    }),
  });
  
  return response.json();
}

// 语义搜索
export async function searchKnowledge(query: string, topK = 5): Promise<any> {
  const { config } = useAppStore.getState();
  
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      app_id: config.appId,
      app_secret: config.appSecret,
      data: { query, top_k: topK },
    }),
  });
  
  return response.json();
}

// RAG问答
export async function chatWithKnowledge(query: string, topK = 3): Promise<any> {
  const { config } = useAppStore.getState();
  
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      app_id: config.appId,
      app_secret: config.appSecret,
      data: { query, top_k: topK },
    }),
  });
  
  return response.json();
}

// 删除文档
export async function deleteDocument(documentId: number): Promise<any> {
  const { config } = useAppStore.getState();
  
  const response = await fetch(`${API_BASE_URL}/api/v1/document/delete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      app_id: config.appId,
      app_secret: config.appSecret,
      data: { document_id: documentId },
    }),
  });
  
  return response.json();
}