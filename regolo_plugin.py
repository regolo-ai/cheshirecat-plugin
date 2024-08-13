from enum import Enum
from typing import List, Optional, Type, Any, Mapping

import requests
from cat.factory.llm import LLMSettings
from cat.mad_hatter.decorators import hook
from langchain_core.language_models.llms import LLM
from pydantic import ConfigDict


@hook  # default priority = 1
def agent_prompt_prefix(prefix, cat):
    # change the Cat's personality
    prefix = ""
    return prefix


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
            response = requests.post("https://api.regolo.ai/v1/chat/completions", headers=headers, json=data).json()
        except (Exception,):
            return "Error"
        generated_text = response["choices"][0]["message"]
        return generated_text["content"]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Identifying parameters."""
        return {"model": self.model, "auth_key": self.Regolo_Key}


def get_models_enum() -> Type[Enum]:
    response = requests.post("https://regolo.ai/models.json").json()
    models = [content["id"] for content in response["models"]]
    x = 0
    var = {}
    for model in models:
        var[f"x{x}"] = model
        x += 1
    return Enum('Enumerate', var)


class RegoloLLMSettings(LLMSettings):
    Regolo_Key: str
    model: get_models_enum()

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
