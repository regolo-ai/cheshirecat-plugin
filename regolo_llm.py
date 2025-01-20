import os
from enum import Enum
from typing import List, Type
import httpx

from pydantic import ConfigDict
from langchain_openai.chat_models import ChatOpenAI

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings
from dotenv import load_dotenv, dotenv_values

load_dotenv()

class LLMRegolo(ChatOpenAI):

    def __init__(self, model, Regolo_Key, streaming, **kwargs):
        super().__init__(
            model_kwargs={},
            base_url=os.getenv("REGOLO_BASE"),
            model_name=model,
            api_key=Regolo_Key,
            streaming=streaming,
            **kwargs
        )

def get_models_enum() -> Type[Enum]:
    try:
        # Execute http no cache request
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        response = httpx.post(
            os.getenv("COMPLETION_JSON_URL"),
            headers=headers
        )
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP

        # Parsing JSON response
        data = response.json()
        if "models" not in data:
            raise ValueError("Key 'models' not found in response")

        models = {content["id"]: content["id"] for content in data["models"]}
        return Enum("ModelEnum", models)

    except httpx.RequestError as e:
        raise RuntimeError(f"HTTP request failed: {e}")
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Invalid response format: {e}")

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
            "link": f"{os.getenv('REGOLO_URL')}",
        }
    )

@hook
def factory_allowed_llms(allowed, cat) -> List:
    allowed.append(RegoloLLMSettings)
    return allowed
