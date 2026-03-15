import { FileUploader, DocumentList, KnowledgeSearch } from './components';
import { useAppStore } from './store/useAppStore';

function App() {
  const { config, setConfig } = useAppStore();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white py-4 shadow">
        <div className="container mx-auto px-4">
          <h1 className="text-2xl font-bold">📚 Knowledge-RAG 管理后台</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {/* Config */}
        <div className="bg-white p-4 rounded-lg shadow mb-4">
          <h3 className="text-lg font-bold mb-3">⚙️ 配置</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">App ID</label>
              <input
                type="text"
                value={config.appId}
                onChange={(e) => setConfig({ ...config, appId: e.target.value })}
                className="w-full border rounded p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">App Secret</label>
              <input
                type="password"
                value={config.appSecret}
                onChange={(e) => setConfig({ ...config, appSecret: e.target.value })}
                className="w-full border rounded p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">API地址</label>
              <input
                type="text"
                value={config.apiBaseUrl}
                onChange={(e) => setConfig({ ...config, apiBaseUrl: e.target.value })}
                className="w-full border rounded p-2"
              />
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <FileUploader />
            <DocumentList />
          </div>
          <div>
            <KnowledgeSearch />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;