"""Base reasoner."""


from dataclasses import dataclass

from openssa.l2.reasoning.abstract import AbstractReasoner
from openssa.l2.task.abstract import ATask

from ._prompts import RESOURCE_QA_CONSO_PROMPT_TEMPLATE


@dataclass
class BaseReasoner(AbstractReasoner):
    """Base reasoner."""

    def reason(self, task: ATask, n_words: int = 300) -> str:
        """Reason through task and return conclusion."""
        if task.resources:
            if len(task.resources) > 1:
                return self.lm.get_response(
                    prompt=RESOURCE_QA_CONSO_PROMPT_TEMPLATE.format(
                        question=task.ask, n_words=n_words,
                        resources_and_answers='\n\n'.join(
                            (f'INFORMATIONAL RESOURCE #{i + 1} (name: "{r.name}"):\n'
                             '\n'
                             f'INFORMATIONAL RESOURCE #{i + 1} OVERVIEW:\n{r.overview}\n'
                             '\n'
                             f'ANSWER #{i + 1}:\n{r.answer(question=task.ask, n_words=n_words)}\n')
                            for i, r in enumerate(task.resources))))

            return next(iter(task.resources)).answer(question=task.ask, n_words=n_words)

        return self.lm.get_response(prompt=f'`[WITHIN {n_words:,} WORDS:]`\n{task.ask}')
