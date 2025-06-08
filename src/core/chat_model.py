from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import init_chat_model


def get_chat_model(model: str = "claude-sonnet-4-20250514", **kwargs) -> BaseChatModel:
    return init_chat_model(model=model, **kwargs)
