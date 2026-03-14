"""Knowledge-RAG - 认证中间件"""
import logging
import hmac
from typing import Optional
from fastapi import HTTPException, Request, Depends

from app.services.db_service import AppConfig, db_router

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务"""
    
    def __init__(self):
        pass
    
    def verify_app(self, app_id: str, app_secret: str) -> AppConfig:
        """验证应用凭证"""
        # 获取应用配置
        app_config = db_router.get_app_config(app_id)
        if not app_config:
            logger.warning(f"无效的appId: {app_id}")
            raise HTTPException(status_code=401, detail="无效的appId")
        
        # 校验secret
        if not self._verify_secret(app_secret, app_config.app_secret):
            logger.warning(f"appSecret错误: {app_id}")
            raise HTTPException(status_code=401, detail="appSecret错误")
        
        # 检查状态
        if app_config.status != "active":
            logger.warning(f"应用已禁用: {app_id}")
            raise HTTPException(status_code=403, detail="应用已禁用")
        
        return app_config
    
    def _verify_secret(self, provided: str, stored: str) -> bool:
        """校验secret（支持HMAC格式）"""
        if stored.startswith('hmac:'):
            _, key = stored.split(':', 1)
            return hmac.compare_digest(provided, key)
        return hmac.compare_digest(provided, stored)


async def get_app_config(request: Request) -> AppConfig:
    """从请求中获取并验证应用配置 - 支持JSON和Form"""
    content_type = request.headers.get('content-type', '')
    
    # 尝试从JSON获取
    if 'application/json' in content_type:
        body = await request.json()
        app_id = body.get('app_id')
        app_secret = body.get('app_secret')
    else:
        # 从Form数据获取
        form = await request.form()
        app_id = form.get('app_id')
        app_secret = form.get('app_secret')
    
    if not app_id or not app_secret:
        raise HTTPException(status_code=400, detail="缺少appId或appSecret")
    
    auth = AuthService()
    return auth.verify_app(app_id, app_secret)


auth_service = AuthService()