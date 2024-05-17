"""Base Reasoner."""


from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from openssa.l2.reasoning.abstract import AbstractReasoner
from openssa.l2.knowledge._prompts import knowledge_injection_lm_chat_msgs
from openssa.l2.task.status import TaskStatus

from ._prompts import (RESOURCE_QA_CONSO_PROMPT_TEMPLATE, RESOURCE_QA_AND_OTHER_RESULTS_CONSO_PROMPT_TEMPLATE,
                       OTHER_RESULTS_CONSO_PROMPT_TEMPLATE, format_other_result)

if TYPE_CHECKING:
    from openssa.l2.planning.abstract.plan import AskAnsPair
    from openssa.l2.knowledge.abstract import Knowledge
    from openssa.l2.task.abstract import ATask


@dataclass
class BaseReasoner(AbstractReasoner):
    """Base Reasoner."""

    def reason(self, task: ATask, *,
               knowledge: set[Knowledge], other_results: list[AskAnsPair] | None = None, n_words: int = 1000) -> str:
        """Work through Task and return conclusion.

        Simply forward the question/problem to Task's available Information Resources,
        and then consolidate results from them.
        """
        if task.resources:
            if len(task.resources) > 1:
                resources_and_answers_str: str = '\n\n'.join(r.present_full_answer(question=task.ask, n_words=n_words)
                                                             for r in task.resources)

                task.result: str = self.lm.get_response(
                    prompt=(RESOURCE_QA_AND_OTHER_RESULTS_CONSO_PROMPT_TEMPLATE.format(
                                question=task.ask, n_words=n_words,
                                resources_and_answers=resources_and_answers_str,
                                other_results='\n\n'.join(format_other_result(other_result)
                                                          for other_result in other_results))

                            if other_results

                            else RESOURCE_QA_CONSO_PROMPT_TEMPLATE.format(
                                question=task.ask, n_words=n_words,
                                resources_and_answers=resources_and_answers_str)),

                    history=knowledge_injection_lm_chat_msgs(knowledge=knowledge) if knowledge else None)

            elif other_results:
                task.result: str = self.lm.get_response(
                    prompt=RESOURCE_QA_AND_OTHER_RESULTS_CONSO_PROMPT_TEMPLATE.format(
                        question=task.ask, n_words=n_words,
                        resources_and_answers=next(iter(task.resources)).present_full_answer(question=task.ask,
                                                                                             n_words=n_words),
                        other_results='\n\n'.join(format_other_result(other_result) for other_result in other_results)),
                    history=knowledge_injection_lm_chat_msgs(knowledge=knowledge) if knowledge else None)

            else:
                task.result: str = next(iter(task.resources)).answer(question=task.ask, n_words=n_words)

        elif other_results:
            task.result: str = self.lm.get_response(
                prompt=OTHER_RESULTS_CONSO_PROMPT_TEMPLATE.format(
                    question=task.ask, n_words=n_words,
                    other_results='\n\n'.join(format_other_result(other_result) for other_result in other_results)),
                history=knowledge_injection_lm_chat_msgs(knowledge=knowledge) if knowledge else None)

        else:
            task.result: str = self.lm.get_response(prompt=f'`[WITHIN {n_words:,} WORDS:]`\n{task.ask}',
                                                    history=(knowledge_injection_lm_chat_msgs(knowledge=knowledge)
                                                             if knowledge
                                                             else None))

        task.status: TaskStatus = TaskStatus.DONE

        return task.result
