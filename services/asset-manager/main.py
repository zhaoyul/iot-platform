from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import hashlib
import os
import json
from datetime import datetime
from enum import Enum
import asyncpg
import redis.asyncio as redis

app = FastAPI(title="IoT Platform Asset Manager", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssetType(str, Enum):
    CODE = "code"
    BINARY = "binary"
    PLC = "plc"
    EDA = "eda"
    FIRMWARE = "firmware"
    CONFIG = "config"

class Asset(BaseModel):
    id: str
    name: str
    type: AssetType
    size: int
    hash: str
    repository: str
    branch: str
    path: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class PLCProgram(BaseModel):
    id: str
    name: str
    language: str  # ST, LD, FBD, IL, SFC
    variables: List[Dict[str, Any]]
    function_blocks: List[Dict[str, Any]]
    programs: List[Dict[str, Any]]

class EDADesign(BaseModel):
    id: str
    name: str
    tool: str  # KiCad, Altium, Eagle
    components: List[Dict[str, Any]]
    nets: List[Dict[str, Any]]
    layers: int
    board_size: Dict[str, float]

# 数据库和缓存连接
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://gitea:gitea_password@postgres:5432/gitea")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
STORAGE_PATH = os.getenv("STORAGE_PATH", "/assets")

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def get_redis_client():
    return await redis.from_url(REDIS_URL)

class AssetManager:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def calculate_hash(self, file_path: str) -> str:
        """计算文件SHA256哈希"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def store_asset(self, file: UploadFile, asset_type: AssetType, metadata: Dict[str, Any]) -> Asset:
        """存储资产文件"""
        # 创建存储路径
        type_path = os.path.join(self.storage_path, asset_type.value)
        os.makedirs(type_path, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(type_path, filename)
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 计算哈希
        file_hash = self.calculate_hash(file_path)
        
        # 创建资产对象
        asset = Asset(
            id=file_hash[:16],
            name=file.filename,
            type=asset_type,
            size=len(content),
            hash=file_hash,
            repository=metadata.get("repository", ""),
            branch=metadata.get("branch", ""),
            path=file_path,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return asset
    
    async def parse_plc_program(self, file_path: str) -> PLCProgram:
        """解析PLC程序"""
        # 这是一个简化的示例
        # 实际实现需要根据具体的PLC编程语言进行解析
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        plc_program = PLCProgram(
            id=hashlib.md5(file_path.encode()).hexdigest(),
            name=os.path.basename(file_path),
            language="ST",  # Structured Text
            variables=[],
            function_blocks=[],
            programs=[]
        )
        
        # 简单的变量提取（实际需要更复杂的解析器）
        for line in content.split('\n'):
            if 'VAR' in line:
                # 提取变量定义
                pass
        
        return plc_program
    
    async def parse_eda_design(self, file_path: str) -> EDADesign:
        """解析EDA设计文件"""
        # KiCad示例解析
        eda_design = EDADesign(
            id=hashlib.md5(file_path.encode()).hexdigest(),
            name=os.path.basename(file_path),
            tool="KiCad",
            components=[],
            nets=[],
            layers=2,
            board_size={"width": 100.0, "height": 80.0}
        )
        
        return eda_design

# 创建全局实例
asset_manager = AssetManager(STORAGE_PATH)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "asset-manager"}

@app.post("/api/v1/assets/upload")
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: AssetType = AssetType.CODE,
    repository: str = "",
    branch: str = "main",
):
    """上传资产文件"""
    metadata = {
        "repository": repository,
        "branch": branch,
        "original_name": file.filename,
        "content_type": file.content_type
    }
    
    asset = await asset_manager.store_asset(file, asset_type, metadata)
    
    return {
        "status": "success",
        "asset": asset.dict()
    }

@app.get("/api/v1/assets/{asset_id}")
async def get_asset(asset_id: str):
    """获取资产信息"""
    # 从数据库查询资产信息
    # 这里是简化实现
    return {
        "id": asset_id,
        "status": "found"
    }

@app.post("/api/v1/plc/parse")
async def parse_plc(file: UploadFile = File(...)):
    """解析PLC程序"""
    # 临时保存文件
    temp_path = os.path.join("/tmp", file.filename)
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)
    
    plc_program = await asset_manager.parse_plc_program(temp_path)
    
    # 清理临时文件
    os.remove(temp_path)
    
    return plc_program.dict()

@app.post("/api/v1/eda/parse")
async def parse_eda(file: UploadFile = File(...)):
    """解析EDA设计文件"""
    temp_path = os.path.join("/tmp", file.filename)
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)
    
    eda_design = await asset_manager.parse_eda_design(temp_path)
    
    os.remove(temp_path)
    
    return eda_design.dict()

@app.get("/api/v1/assets")
async def list_assets(
    asset_type: Optional[AssetType] = None,
    repository: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """列出资产"""
    # 从数据库查询
    # 这里是简化实现
    return {
        "total": 0,
        "items": [],
        "limit": limit,
        "offset": offset
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
