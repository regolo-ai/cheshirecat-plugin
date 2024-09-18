from enum import Enum
from typing import List, Optional, Type, Any, Mapping
import httpx

from pydantic import ConfigDict
from langchain_openai.chat_models import ChatOpenAI

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings
from cat.log import log

class LLMRegolo(ChatOpenAI):

    def __init__(self, model, Regolo_Key, streaming, **kwargs):
        super().__init__(
            model_kwargs={},
            base_url="https://api.regolo.ai/v1/",
            model_name=model,
            api_key=Regolo_Key,
            streaming=streaming,
            **kwargs
        )


def get_models_enum() -> Type[Enum]:
    response = httpx.post("https://regolo.ai/models.json").json()
    models = {content["id"]: content["id"] for content in response["models"]}
    return Enum('Enum', models)

LLMEnum = get_models_enum()

class RegoloLLMSettings(LLMSettings):
    model: LLMEnum
    Regolo_Key: str
    streaming: bool = True
    _pyclass: Type = LLMRegolo

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Regolo LLM",
            "description": "LLM on regolo.ai",
            "link": "https://regolo.ai/",
        }
    )

@hook
def factory_allowed_llms(allowed, cat) -> List:
    allowed.append(RegoloLLMSettings)
    return allowed
