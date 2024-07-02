# my_project/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, HttpUrl
from pathlib import Path
import dotenv

# Define the path to the .env file in the parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
dotenv.load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    KRAKEN_API_URL: HttpUrl
    KRAKEN_API_KEY: str
    KRAKEN_API_SECRET: str
    LOGGING_LEVEL: str

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_prefix="",
        case_sensitive=True,
    )

# Debugging step to verify environment variables
if __name__ == "__main__":
    import os
    print("Env file path:", env_path)
    print("DATABASE_URL:", os.getenv("DATABASE_URL"))
    print("KRAKEN_API_URL:", os.getenv("KRAKEN_API_URL"))
    print("KRAKEN_API_KEY:", os.getenv("KRAKEN_API_KEY"))
    print("KRAKEN_API_SECRET:", os.getenv("KRAKEN_API_SECRET"))
    print("LOGGING_LEVEL:", os.getenv("LOGGING_LEVEL"))
