from enum import Enum
from typing import List, Optional, Type, Any, Mapping

import httpx
from cat.factory.llm import LLMSettings
from cat.mad_hatter.decorators import hook
from langchain_core.language_models.llms import LLM
from langchain_core.embeddings import Embeddings
from cat.factory.embedder import EmbedderSettings
from pydantic import ConfigDict


# Regolo models settings

class LLMRegolo(LLM):
    """Setup for the Regolo plugin"""

    Regolo_Key: str
    model: str = "mistralai/Mistral-7B-Instruct-v0.2"

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self,
              prompt: str,
              stop: Optional[List[str]] = None,
              run_manager: Optional[Any] = None,
              **kwargs: Any) -> str:
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json",
                   "Authorization": self.Regolo_Key if self.Regolo_Key.__contains__("Bearer") else
                   f"Bearer {self.Regolo_Key}"}
        try:
            response = httpx.post("https://api.regolo.ai/v1/chat/completions", headers=headers, json=data).json()
        except (Exception,):
            return "Error"
        generated_text = response["choices"][0]["message"]
        return generated_text["content"]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Identifying parameters."""
        return {"model": self.model, "auth_key": self.Regolo_Key}


def get_models_enum() -> tuple[Type[Enum], str] | tuple[Type[str], str]:
    response = httpx.post("https://regolo.ai/models.json").json()
    models = [content["id"] for content in response["models"]]
    x = 0
    var = {}
    for model in models:
        var[f"x{x}"] = model
        x += 1
    if len(var) == 1:
        return str, models[0]
    return Enum('Enumerate', var), ""


models_names = get_models_enum()


class RegoloLLMSettings(LLMSettings):
    model: models_names[0] = models_names[1]
    Regolo_Key: str

    _pyclass: Type = LLMRegolo

    @classmethod
    def get_llm_from_config(cls, config):
        return cls._pyclass.default(**config)

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Regolo LLM",
            "description": "LLM on regolo.ai",
            "link": "https://regolo.ai/"
        }
    )


@hook
def factory_allowed_llms(allowed, cat) -> List:
    allowed.append(RegoloLLMSettings)
    return allowed


# Regolo Embeddings settings


class RegoloEmbeddings(Embeddings):
    """Regolo embeddings"""

    def __init__(self, model, Regolo_Key):
        self.model_name = model
        self.Regolo_Key = Regolo_Key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {"input": texts, "model": self.model_name}
        headers = {"Authorization": self.Regolo_Key if self.Regolo_Key.__contains__("Bearer") else
        f"Bearer {self.Regolo_Key}"}
        ret = httpx.post("https://api.regolo.ai/v1/embeddings", headers=headers, json=payload)
        ret.raise_for_status()
        return [e["embedding"] for e in ret.json()["data"]]

    def embed_query(self, text: str) -> List[float]:
        payload = {"input": text, "model": self.model_name}
        headers = {"Authorization": self.Regolo_Key if self.Regolo_Key.__contains__("Bearer") else
        f"Bearer {self.Regolo_Key}"}
        ret = httpx.post("https://api.regolo.ai/v1/embeddings", headers=headers, json=payload)
        ret.raise_for_status()
        return ret.json()["data"][0]["embedding"]


def get_embeddings_enum() -> tuple[Type[Enum], str] | tuple[Type[str], str]:
    response = httpx.post("https://regolo.ai/models_embeddings.json").json()
    models = [content["id"] for content in response["models"]]
    x = 0
    var = {}
    for model in models:
        var[f"x{x}"] = model
        x += 1
    if len(var) == 1:
        return str, models[0]
    return Enum('Enumerate', var), ""


embedding_models_names = get_embeddings_enum()


class RegoloEmbeddingsConfig(EmbedderSettings):
    model: embedding_models_names[0] = embedding_models_names[1]
    Regolo_Key: str
    _pyclass: Type = RegoloEmbeddings

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Regolo embedder models",
            "description": "Configuration for regolo.ai embeddings",
            "link": "",
        }
    )


@hook
def factory_allowed_embedders(allowed, cat) -> List:
    allowed.append(RegoloEmbeddingsConfig)
    return allowed
