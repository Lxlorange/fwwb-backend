from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    应用全局配置类，使用 Pydantic V2 的 BaseSettings。
    可以从环境变量或 .env 文件中读取配置。
    """
    PROJECT_NAME: str = "海洋环境智能分析与预警系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS 域名配置
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
