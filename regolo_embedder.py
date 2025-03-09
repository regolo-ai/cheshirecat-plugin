import os
import json

from enum import Enum
from typing import List, Type, Optional
import httpx

from pydantic import ConfigDict, Field
from langchain_core.embeddings import Embeddings

from cat.log import log
from cat.mad_hatter.decorators import hook
from cat.factory.embedder import EmbedderSettings
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Read the settings.json from the same folder of the plugin

current_dir = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(current_dir, 'settings.json')
with open(json_path, 'r') as f:
    json_settings = json.load(f)


class RegoloEmbeddings(Embeddings):
    """Regolo embeddings"""

    def __init__(self, model):
        self.model_name = model
        self.Regolo_Key = json_settings["regolo_key"]

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


def get_embedders_enum() -> Optional[Type[Enum] | str]:
    try:
        # Execute http no cache request
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        key = json_settings["regolo_key"]
        if key is not None and key != "":
            headers["Authorization"] = f"Bearer {key}"
        response = httpx.get(
            os.getenv("COMPLETION_JSON_URL"),
            headers=headers
        )
        if response.status_code == 401:
            return Enum("Enum",
                        {"Authentication Error": "Auth error, please try updating the Api key in the plugin options",
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
