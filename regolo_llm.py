from enum import Enum
from typing import List, Optional, Type, Any, Mapping
import httpx

from pydantic import ConfigDict
from langchain_core.language_models.llms import LLM
from langchain_openai.chat_models import ChatOpenAI

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings
from cat.log import log


# Regolo models settings


# class LLMRegolo(LLM):
#     """Setup for the Regolo plugin"""

#     Regolo_Key: str
#     model: str = "mistralai/Mistral-7B-Instruct-v0.2"

#     @property
#     def _llm_type(self) -> str:
#         return "custom"

#     def _call(self,
#               prompt: str,
#               stop: Optional[List[str]] = None,
#               run_manager: Optional[Any] = None,
#               **kwargs: Any) -> str:
        
#         log.warning(prompt)

#         data = {
#             "model": self.model,
#             "messages": [{"role": "user", "content": prompt}]
#         }
#         headers = {"Content-Type": "application/json",
#                    "Accept": "application/json",
#                    "Authorization": self.Regolo_Key if self.Regolo_Key.__contains__("Bearer") else
#                    f"Bearer {self.Regolo_Key}"}
#         try:
#             response = httpx.post(
#                 "https://api.regolo.ai/v1/chat/completions",
#                 headers=headers,
#                 json=data,
#                 timeout=httpx.Timeout(timeout=20)
#             )
#             json = response.json()
#             log.warning(json)
#             generated_text = json["choices"][0]["message"]
#         except Exception as e:
#             return str(e)
#         return generated_text["content"]

#     @property
#     def _identifying_params(self) -> Mapping[str, Any]:
#         """Identifying parameters."""
#         return {"model": self.model, "auth_key": self.Regolo_Key}
    

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

    """
    def invoke(self, *args, **kwargs):
        log.warning(args)
        log.warning(kwargs)
        out = super().invoke(*args, **kwargs)
        log.error(out)
        return out

    """ 

    def _stream(self, *args, **kwargs) -> str:
        log.warning(args)
        log.warning(kwargs)

        out = super()._stream(*args, **kwargs)
        log.error(out)
        return out


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
