"""Knowledge-RAG - 文件服务"""
import os
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# 支持的文件格式
ALLOWED_EXTENSIONS = {
    'md': 'text/markdown',
    'markdown': 'text/markdown',
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class FileService:
    """文件处理服务"""
    
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = storage_path
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "uploads"), exist_ok=True)
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    def _validate_file(self, filename: str, size: int) -> None:
        """验证文件"""
        ext = self._get_file_extension(filename)
        
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {ext}. 支持的格式: {', '.join(ALLOWED_EXTENSIONS.keys())}"
            )
        
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大: {size / 1024 / 1024:.1f}MB. 最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
    
    def _calculate_hash(self, content: bytes) -> str:
        """计算文件hash用于去重"""
        return hashlib.sha256(content).hexdigest()
    
    def _get_storage_path(self, app_id: str, filename: str) -> str:
        """获取存储路径"""
        now = datetime.now()
        date_path = now.strftime("%Y/%m/%d")
        
        # 生成唯一文件名
        ext = self._get_file_extension(filename)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        
        full_path = os.path.join(
            self.storage_path, 
            "uploads", 
            app_id,
            date_path,
            unique_name
        )
        
        # 创建目录
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return full_path, unique_name, date_path
    
    async def save_file(self, file: UploadFile, app_id: str) -> dict:
        """保存上传的文件"""
        # 读取文件内容
        content = await file.read()
        
        # 验证文件
        self._validate_file(file.filename, len(content))
        
        # 计算hash
        file_hash = self._calculate_hash(content)
        
        # 获取存储路径
        stored_path, unique_name, date_path = self._get_storage_path(app_id, file.filename)
        
        # 保存文件
        with open(stored_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"文件已保存: {stored_path}")
        
        return {
            "stored_path": stored_path,
            "unique_name": unique_name,
            "date_path": date_path,
            "original_filename": file.filename,
            "file_size": len(content),
            "file_hash": file_hash,
            "mime_type": ALLOWED_EXTENSIONS.get(self._get_file_extension(file.filename), 'application/octet-stream')
        }
    
    def extract_text(self, file_path: str) -> str:
        """根据文件类型提取文本"""
        ext = self._get_file_extension(file_path)
        
        extractors = {
            'md': self._extract_markdown,
            'markdown': self._extract_markdown,
            'txt': self._extract_txt,
            'pdf': self._extract_pdf,
            'docx': self._extract_docx,
        }
        
        extractor = extractors.get(ext)
        if not extractor:
            raise HTTPException(status_code=400, detail=f"暂不支持的文件格式: {ext}")
        
        return extractor(file_path)
    
    def _extract_markdown(self, file_path: str) -> str:
        """提取Markdown文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_txt(self, file_path: str) -> str:
        """提取纯文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_pdf(self, file_path: str) -> str:
        """提取PDF文本"""
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("pypdf未安装，无法解析PDF")
            raise HTTPException(status_code=400, detail="PDF解析需要安装pypdf库")
        except Exception as e:
            logger.error(f"PDF解析失败: {e}")
            raise HTTPException(status_code=400, detail=f"PDF解析失败: {str(e)}")
    
    def _extract_docx(self, file_path: str) -> str:
        """提取Word文档文本"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except ImportError:
            logger.warning("python-docx未安装，无法解析Word文档")
            raise HTTPException(status_code=400, detail="Word文档解析需要安装python-docx库")
        except Exception as e:
            logger.error(f"Word文档解析失败: {e}")
            raise HTTPException(status_code=400, detail=f"Word文档解析失败: {str(e)}")


# 全局实例
file_service = FileService()