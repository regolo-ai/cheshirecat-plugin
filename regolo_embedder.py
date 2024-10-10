import os
from enum import Enum
from typing import List, Type
import httpx

from pydantic import ConfigDict
from langchain_core.embeddings import Embeddings

from cat.mad_hatter.decorators import hook
from cat.factory.embedder import EmbedderSettings
from dotenv import load_dotenv, dotenv_values

load_dotenv()

class RegoloEmbeddings(Embeddings):
    """Regolo embeddings"""

    def __init__(self, model, Regolo_Key):
        self.model_name = model
        self.Regolo_Key = Regolo_Key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {"input": texts, "model": self.model_name}
        headers = {"Authorization": self.Regolo_Key if self.Regolo_Key.__contains__("Bearer") else
        f"Bearer {self.Regolo_Key}"}
        ret = httpx.post(os.getenv("EMBEDDINGS_URL"), headers=headers, json=payload,
                         timeout=httpx.Timeout(timeout=int(os.getenv("TIMEOUT"))))
        ret.raise_for_status()
        to_return = [e["embedding"] for e in ret.json()["data"]]
        return to_return

    def embed_query(self, text: str) -> List[float]:
        payload = {"input": text, "model": self.model_name}
        headers = {"Authorization": self.Regolo_Key if self.Regolo_Key.__contains__("Bearer") else
        f"Bearer {self.Regolo_Key}"}
        ret = httpx.post(os.getenv("EMBEDDINGS_URL"), headers=headers, json=payload,
                         timeout=httpx.Timeout(timeout=int(os.getenv("TIMEOUT"))))
        ret.raise_for_status()
        to_return = ret.json()["data"][0]["embedding"]
        return to_return



def get_embedders_enum() -> Type[Enum]:
    response = httpx.post(os.getenv("EMBEDDINGS_JSON_URL")).json()
    models = {content["id"]: content["id"] for content in response["models"]}
    # TODO: take away the following line as soon as new models are available
    models["unavailable"] = "More models coming soon" # enum needs at least two values
    return Enum('Enum', models)

EmbedderEnum = get_embedders_enum()

class RegoloEmbeddingsConfig(EmbedderSettings):
    model: EmbedderEnum
    Regolo_Key: str
    _pyclass: Type = RegoloEmbeddings

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Regolo embedder models",
            "description": "Configuration for regolo.ai embeddings",
            "link": f"{os.getenv('REGOLO_URL')}",
        }
    )

@hook
def factory_allowed_embedders(allowed, cat) -> List:
    allowed.append(RegoloEmbeddingsConfig)
    return allowed
