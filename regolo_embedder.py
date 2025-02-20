import os
from enum import Enum
from typing import List, Type, Optional
import httpx

from pydantic import ConfigDict
from langchain_core.embeddings import Embeddings

from cat.log import log
from cat.mad_hatter.decorators import hook
from cat.factory.embedder import EmbedderSettings
from dotenv import load_dotenv, dotenv_values
from cat.looking_glass.cheshire_cat import CheshireCat

load_dotenv()
ccat = CheshireCat()

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



def get_embedders_enum() -> Optional[Type[Enum]|str]:
    try:
        # Execute http no cache request
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        settings = ccat.mad_hatter.get_plugin().load_settings()
        key = settings["regolo_key"]
        if key is not None:
            headers["Authorization"] = f"Bearer {key}"
        response = httpx.get(
            os.getenv("COMPLETION_JSON_URL"),
            headers=headers
        )
        if response.status_code == 401:
            return Enum("Enum", {"Authentication Error": "Auth error, please try updating the Api key in the plugin options",
                                      "Please try restarting the plugin": "If key is correct try restarting the plugin"})
        elif response.status_code == 503:
            return Enum("Enum", {"Service unavailable": "Service unavailable",
                                      "Please try restarting the plugin": "Please try restarting the plugin"})
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP
        # Parsing JSON response
        data = response.json()
        if "data" not in data:
            raise ValueError('Models not found')

        models_info = data["data"]
        models = {model["model_name"]: model["model_name"] for model
                  in models_info if model["model_info"]["mode"] == "embedding"}
        if len(models) == 0:
            return Enum("Enum", {"No embedders available": "No embedders available",
                                 "More embedders coming soon": "More embedders coming soon"})
        elif len(models) == 1:
            models["More embedders coming soon"] = "More embedders coming soon"
        return Enum("Enum", models)
    except httpx.RequestError as e:
        raise RuntimeError(f"HTTP request failed: {e}")
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Invalid response format: {e}")

class RegoloEmbeddingsConfig(EmbedderSettings):
    model: get_embedders_enum()
    Regolo_Key: str = ccat.mad_hatter.get_plugin().load_settings()["regolo_key"]
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
