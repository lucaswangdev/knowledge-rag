import { create } from 'zustand';

interface AppConfig {
  appId: string;
  appSecret: string;
  apiBaseUrl: string;
}

interface Document {
  id: number;
  title: string;
  content?: string;
  tags: string[];
  source: string;
  created_at: string;
}

interface SearchResult {
  chunk_text: string;
  document_id: number;
  document_title: string;
  similarity_score: number;
  chunk_index: number;
}

interface AppState {
  // Config
  config: AppConfig;
  setConfig: (config: AppConfig) => void;
  
  // Documents
  documents: Document[];
  setDocuments: (docs: Document[]) => void;
  addDocument: (doc: Document) => void;
  
  // Search
  searchResults: SearchResult[];
  setSearchResults: (results: SearchResult[]) => void;
  isSearching: boolean;
  setIsSearching: (loading: boolean) => void;
  
  // Upload
  isUploading: boolean;
  setIsUploading: (loading: boolean) => void;
  
  // Chat
  chatAnswer: string;
  setChatAnswer: (answer: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Default config
  config: {
    appId: 'app_001',
    appSecret: 'test_secret_001',
    apiBaseUrl: 'http://localhost:8000',
  },
  setConfig: (config) => set({ config }),
  
  // Documents
  documents: [],
  setDocuments: (documents) => set({ documents }),
  addDocument: (doc) => set((state) => ({ 
    documents: [doc, ...state.documents] 
  })),
  
  // Search
  searchResults: [],
  setSearchResults: (searchResults) => set({ searchResults }),
  isSearching: false,
  setIsSearching: (isSearching) => set({ isSearching }),
  
  // Upload
  isUploading: false,
  setIsUploading: (isUploading) => set({ isUploading }),
  
  // Chat
  chatAnswer: '',
  setChatAnswer: (chatAnswer) => set({ chatAnswer }),
}));