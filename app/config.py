from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str 
    database_port: str
    database_name: str
    database_password: str
    database_username: str
    secret_key: str
    algorithms: str
    access_token_expires_minutes: int 
    google_client_id: str
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

setting = Settings()