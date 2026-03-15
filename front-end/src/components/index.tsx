import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { uploadDocument, getDocumentList, searchKnowledge, deleteDocument } from '../api';

export function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState('');
  const { isUploading, setIsUploading } = useAppStore();

  const handleUpload = async () => {
    if (!file || !title) return;
    
    setIsUploading(true);
    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(t => t);
      const result = await uploadDocument(file, title, tagList);
      
      if (result.success) {
        alert('上传成功！');
        setFile(null);
        setTitle('');
        setTags('');
      } else {
        alert('上传失败: ' + result.message);
      }
    } catch (error) {
      alert('上传失败: ' + error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <h3 className="text-lg font-bold mb-3">📤 上传文档</h3>
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1">选择文件</label>
          <input
            type="file"
            accept=".md,.txt,.pdf,.docx"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full border rounded p-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">标题</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="输入文档标题"
            className="w-full border rounded p-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">标签（逗号分隔）</label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="如: 创业,科技"
            className="w-full border rounded p-2"
          />
        </div>
        <button
          onClick={handleUpload}
          disabled={!file || !title || isUploading}
          className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:bg-gray-300"
        >
          {isUploading ? '上传中...' : '上传'}
        </button>
      </div>
    </div>
  );
}

export function DocumentList() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const result = await getDocumentList();
      if (result.success) {
        setDocuments(result.data.list);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定删除？')) return;
    try {
      await deleteDocument(id);
      loadDocuments();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold">📄 文档列表</h3>
        <button
          onClick={loadDocuments}
          className="text-blue-500 hover:underline"
        >
          刷新
        </button>
      </div>
      {loading ? (
        <p>加载中...</p>
      ) : documents.length === 0 ? (
        <p className="text-gray-500">暂无文档</p>
      ) : (
        <ul className="space-y-2">
          {documents.map((doc) => (
            <li key={doc.id} className="border-b pb-2 flex justify-between items-center">
              <div>
                <p className="font-medium">{doc.title}</p>
                <p className="text-sm text-gray-500">
                  {doc.tags?.join(', ')} | {new Date(doc.created_at).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-red-500 hover:text-red-700"
              >
                删除
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function KnowledgeSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const result = await searchKnowledge(query);
      if (result.success) {
        setResults(result.data.results);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-bold mb-3">🔍 语义搜索</h3>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入搜索内容..."
          className="flex-1 border rounded p-2"
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-green-500 text-white px-4 rounded hover:bg-green-600"
        >
          {loading ? '搜索中...' : '搜索'}
        </button>
      </div>
      <div className="space-y-3">
        {results.map((result, i) => (
          <div key={i} className="border rounded p-3">
            <div className="flex justify-between items-start mb-2">
              <span className="font-medium">{result.document_title}</span>
              <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                {result.similarity_score.toFixed(4)}
              </span>
            </div>
            <p className="text-gray-600 text-sm">{result.chunk_text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}