"""Abstract Informational Resource."""


from abc import ABC, abstractmethod
from functools import cached_property
from typing import TypeVar

from ._prompts import RESOURCE_OVERVIEW_PROMPT_TEMPLATE


class AbstractResource(ABC):
    """Abstract Informational Resource."""

    @cached_property
    @abstractmethod
    def unique_name(self) -> str:
        """Return globally-unique name of Informational Resource."""

    @cached_property
    @abstractmethod
    def name(self) -> str:
        """Return potentially non-unique, but informationally helpful name of Informational Resource."""

    @abstractmethod
    def answer(self, question: str, n_words: int = 1000) -> str:
        """Answer question from Informational Resource."""

    @cached_property
    def overview(self) -> str:
        """Return overview of Informational Resource."""
        return self.answer(question=RESOURCE_OVERVIEW_PROMPT_TEMPLATE.format(name=self.name))


AResource: TypeVar = TypeVar('AResource', bound=AbstractResource, covariant=False, contravariant=False)
