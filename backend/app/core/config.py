import secrets
import os
from typing import Any, Dict, List, Optional, Union, Literal

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")
    
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]], info: ValidationInfo) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "RAG Query API"
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "doc_query"
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        
        postgres_user = info.data.get("POSTGRES_USER")
        postgres_password = info.data.get("POSTGRES_PASSWORD")
        postgres_server = info.data.get("POSTGRES_SERVER")
        postgres_port = info.data.get("POSTGRES_PORT")
        postgres_db = info.data.get("POSTGRES_DB")
        
        # Build connection string manually
        if postgres_user and postgres_password and postgres_server and postgres_db:
            return f"postgresql+psycopg2://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"
        return v
    
    @field_validator("POSTGRES_PORT", mode="before")
    def validate_port(cls, v: Any) -> int:
        if isinstance(v, str):
            return int(v)
        return v
    
    # Model Provider Settings
    MODEL_PROVIDER: Literal["openai", "local", "huggingface"] = "openai"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Local Model Settings
    LOCAL_EMBEDDING_MODEL_PATH: str = os.getenv("LOCAL_EMBEDDING_MODEL_PATH", "")
    LOCAL_COMPLETION_MODEL_PATH: str = os.getenv("LOCAL_COMPLETION_MODEL_PATH", "")
    LOCAL_MODEL_SERVER_URL: str = os.getenv("LOCAL_MODEL_SERVER_URL", "http://localhost:8080")
    
    # HuggingFace Settings
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Vector Settings
    VECTOR_COLLECTION_NAME: str = os.getenv("VECTOR_COLLECTION_NAME", "document_embeddings")
    
    # Default Model Names
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # OpenAI default
    COMPLETION_MODEL: str = os.getenv("COMPLETION_MODEL", "gpt-4o")                 # OpenAI default
    
    # Alternative Model Names
    LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")  # HF model ID for local use
    LOCAL_COMPLETION_MODEL: str = os.getenv("LOCAL_COMPLETION_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    
    HUGGINGFACE_EMBEDDING_MODEL: str = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    HUGGINGFACE_COMPLETION_MODEL: str = os.getenv("HUGGINGFACE_COMPLETION_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    
    # Model Parameters
    EMBEDDING_DIMENSION: int = os.getenv("EMBEDDING_DIMENSION", 1536)  # OpenAI default, may change with other models
    
settings = Settings() 