"""
================================
OLLAMA LANGUAGE MODELS (LMs)
=================================
"""


from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import TYPE_CHECKING

from loguru import logger

from llama_index.llms.ollama import Ollama

from llama_index.embeddings.ollama import OllamaEmbedding

from typing import List

from .base import BaseLM
from .config import LMConfig


if TYPE_CHECKING:
    from llama_index.core.base.llms.types import ChatResponse
    from .base import LMChatHist



@dataclass
class OllamaLM(BaseLM):
    """Wrapper for OLLAMA using llama-index API."""

    llm: Ollama = field(init=False)
        
    def __post_init__(self):
        """
        Initialize the OLLAMA wrapper.

        Args:
            model (str): The model name (e.g., "llama2").
            request_timeout (float): Request timeout for API calls, in seconds.
            **kwargs: Additional arguments passed to the OLLAMA client.
        """
        self.llm = Ollama(model=self.model, request_timeout=60)

    @classmethod
    def from_defaults(cls) -> OllamaLM:
        """Get HuggingFace LM instance with default parameters."""
        # pylint: disable=unexpected-keyword-arg
        return cls(model=LMConfig.OLLAMA_DEFAULT_MODEL, api_key="", api_base="")


    def call(self, messages: LMChatHist, **kwargs) -> ChatResponse:
        """
        Generate a completion for a given prompt.

        Args:
            prompt (str): The input prompt.
            **kwargs: Additional arguments for the LLM completion.

        Returns:
            str: The generated text completion.
        """
        response = self.llm.complete(messages, **kwargs)
        return response


    def get_response(self, prompt: str, history: List[dict] = None, json_format: bool = False, **kwargs) -> str:
        """
        Generate a response to a user prompt using the LLM.

        Args:
            prompt (str): The user input prompt.
            history (List[dict], optional): Chat history to maintain context. Defaults to None.
            json_format (bool): Whether to attempt parsing the response as JSON. Defaults to False.
            **kwargs: Additional arguments for the LLM completion.

        Returns:
            str: The LLM's response or the parsed JSON content.
        """
        messages = history or []
        messages.append({"role": "user", "content": prompt})

        if json_format:
            while True:
                try:
                    response = self.llm.call(messages, **kwargs)
                    return json.loads(response)  # Ensure response is valid JSON
                except json.JSONDecodeError:
                    logger.debug(f"INVALID JSON, TO BE RETRIED:\n{response}")
        else:
            response = self.llm.call(messages, **kwargs)
            return response

def default_llama_index_ollama_embed_model() -> OllamaEmbedding:
    # https://docs.llamaindex.ai/en/stable/examples/embeddings/ollama_embedding/
    print("Returning OllamaEmbedding with mxbai-embed-large")
    return OllamaEmbedding(model_name="mxbai-embed-large",
                           base_url="http://localhost:11434",
                           ollama_additional_kwargs={"mirostat": 0})



def default_llama_index_ollama_lm(name: str = LMConfig.OLLAMA_DEFAULT_MODEL, /) -> Ollama:
    return OllamaLM.from_defaults().llm
