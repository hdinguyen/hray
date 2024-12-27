from typing import Union

from dspy import InputField, OutputField, Signature
from foundation import ExaQuery, SummarizedContent


class AssistanceQueryPurpose(Signature):
    purpose: str = InputField(desc="Why do you want to know the answer to this question?")
    question: str = InputField(desc="What do you want to know, more specifically?")
    queries: list[ExaQuery] = InputField(desc="Optimise the queries to get the most relevant information follow the best practices (omitted)")

class ExtractContent(Signature):
    original_content: str = InputField(desc="The original content to extract information from")
    query:str = InputField(desc="The query context for determining relevance")
    cleaned_response: Union[SummarizedContent, None] = OutputField(
        desc='the cleaned and summarized result, `None` if no relevant content'
    )
