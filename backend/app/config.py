import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    VNSTOCK_SOURCE: str = os.getenv("VNSTOCK_SOURCE", "VCI")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")
    # Model string hiện tại (kiểm tra docs.claude.com nếu có bản mới hơn)
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")


settings = Settings()
