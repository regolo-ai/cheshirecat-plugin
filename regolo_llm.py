import os
import json
from enum import Enum
from typing import List, Type, Optional
import httpx
from pydantic import ConfigDict
from langchain_openai.chat_models import ChatOpenAI

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings
from dotenv import load_dotenv, dotenv_values
from cat.log import log
from pathlib import Path
load_dotenv()
# Read the settings.json from the same folder of the plugin
REGOLO_API_KEY_ENV_NAME = "REGOLO_API_KEY"

current_dir = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(current_dir, 'settings.json')
if Path(json_path).exists():
    with open(json_path, 'r') as f:
        json_settings = json.load(f)
else:
    json_settings = {"regolo_key": os.getenv("REGOLO_API_KEY")}


class LLMRegolo(ChatOpenAI):

    def __init__(self, model, streaming, **kwargs):
        super().__init__(
            model_kwargs={},
            base_url=os.getenv("REGOLO_BASE"),
            model_name=model,
            api_key=json_settings["regolo_key"],
            streaming=streaming,
            **kwargs
        )


def get_models_enum() -> Optional[Type[Enum] | str]:
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
            return Enum("ModelEnum", {"Service unavailable": "Service unavailable",
                                      "Please try restarting the plugin": "Please try restarting the plugin"})
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP
        # Parsing JSON response
        data = response.json()
        if "data" not in data:
            raise ValueError('Models not found')

        models_info = data["data"]
        models = {model["model_name"]: model["model_name"] for model
                  in models_info if model["model_info"]["mode"] == "chat" or model["model_info"]["mode"] is None}
        if len(models) == 0:
            return Enum("Enum", {"No models available": "No models available",
                                 "More models coming soon": "More models coming soon"})
        elif len(models) == 1:
            models["More models coming soon"] = "More models coming soon"
        return Enum("ModelEnum", models)

    except httpx.RequestError as e:
        raise RuntimeError(f"HTTP request failed: {e}")
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Invalid response format: {e}")


class RegoloLLMSettings(LLMSettings):
    model: get_models_enum()
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
def factory_allowed_llms(allowed, cat) -> List:  # noqa
    allowed.append(RegoloLLMSettings)
    return allowed
