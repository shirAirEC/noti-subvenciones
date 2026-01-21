"""
Configuración de la aplicación
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/subvenciones"
    
    # BDNS API
    bdns_api_url: str = "https://www.infosubvenciones.es/bdnstrans/api"
    
    # Google Calendar
    google_service_account_file: str = "./credentials/service-account.json"
    calendar_id: str = ""
    
    # Email
    email_from: str = "noreply@example.com"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:8080"
    
    # Scheduler
    scheduler_enabled: bool = True
    scheduler_hour: int = 8
    scheduler_minute: int = 0
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Obtener configuración (cached)"""
    return Settings()
