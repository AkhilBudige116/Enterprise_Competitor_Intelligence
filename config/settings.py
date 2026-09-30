"""Settings and LLM factory for Enterprise Multi-Agent Competitor Intelligence."""
import os
from functools import lru_cache
from typing import Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage

class Settings(BaseSettings):
    """Application settings with environment variable auto-discovery."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Keys
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    
    # Model preferences
    DEFAULT_LLM_PROVIDER: str = "gemini"  # gemini, openai, groq, mock
    DEFAULT_LLM_MODEL: Optional[str] = None
    DEFAULT_TEMPERATURE: float = 0.2
    
    # Execution
    MAX_SELF_CORRECTION_RETRIES: int = 2
    LOG_LEVEL: str = "INFO"
    CACHE_ENABLED: bool = True
    OUTPUT_DIR: str = "output"

@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached application settings instance."""
    return Settings()

class MockChatModel(BaseChatModel):
    """Fallback LLM for testing/demo when no external API key is supplied."""
    model_name: str = "mock-agent-llm"
    
    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None, **kwargs: Any):
        from langchain_core.outputs import ChatResult, ChatGeneration
        last_msg = messages[-1].content if messages else ""
        content = f"Synthesized analysis based on structured evidence: {last_msg[:300]}"
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    @property
    def _llm_type(self) -> str:
        return "mock"

def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.2,
    api_key: Optional[str] = None
) -> BaseChatModel:
    """Factory creating LangChain Chat Model instances based on config or explicit parameters."""
    settings = get_settings()
    selected_provider = (provider or settings.DEFAULT_LLM_PROVIDER).lower()
    
    # Check for Gemini / Google GenAI
    gemini_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
    openai_key = api_key or os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    groq_key = api_key or os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY

    # Auto-detect if provider not matched with keys
    if selected_provider == "gemini" and gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            target_model = model_name or settings.DEFAULT_LLM_MODEL or "gemini-1.5-pro"
            # In case gemini-2.0-flash or gemini-1.5-pro
            return ChatGoogleGenerativeAI(
                model=target_model,
                temperature=temperature,
                google_api_key=gemini_key,
                convert_system_message_to_human=True
            )
        except Exception as e:
            print(f"[Warning] Failed to initialize ChatGoogleGenerativeAI: {e}")

    if (selected_provider == "openai" or openai_key) and openai_key:
        try:
            from langchain_openai import ChatOpenAI
            target_model = model_name or settings.DEFAULT_LLM_MODEL or "gpt-4o"
            return ChatOpenAI(
                model=target_model,
                temperature=temperature,
                api_key=openai_key
            )
        except Exception as e:
            print(f"[Warning] Failed to initialize ChatOpenAI: {e}")

    if (selected_provider == "groq" or groq_key) and groq_key:
        try:
            from langchain_groq import ChatGroq
            target_model = model_name or settings.DEFAULT_LLM_MODEL or "llama-3.3-70b-versatile"
            return ChatGroq(
                model=target_model,
                temperature=temperature,
                groq_api_key=groq_key
            )
        except Exception as e:
            print(f"[Warning] Failed to initialize ChatGroq: {e}")

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=temperature,
                google_api_key=gemini_key
            )
        except Exception:
            pass

    # Fallback to Mock Chat Model for resilience
    return MockChatModel()
