"""
Configuration settings using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    db_host: str = Field(default="localhost", description="Database host")
    db_user: str = Field(default="root", description="Database user")
    db_password: str = Field(default="rootpassword", description="Database password")

    # Legacy Database
    legacy_db: str = Field(default="legacy_db", description="Legacy database name")
    legacy_db_port: int = Field(default=3307, description="Legacy database port")

    # New Database
    new_db: str = Field(default="new_db", description="New database name")
    new_db_port: int = Field(default=3308, description="New database port")

    # Migration Settings
    batch_size: int = Field(default=100, ge=1, le=10000, description="Batch size for migrations")
    dry_run: bool = Field(default=False, description="Dry run mode (no actual changes)")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/migration.log", description="Log file path")

    # Faker/Seeder Settings
    seed_count: int = Field(default=3000, ge=1, le=100000, description="Number of records to seed")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @property
    def legacy_db_url(self) -> str:
        """Get legacy database URL."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.legacy_db_port}/{self.legacy_db}"
        )

    @property
    def new_db_url(self) -> str:
        """Get new database URL."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.new_db_port}/{self.new_db}"
        )

    def create_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
