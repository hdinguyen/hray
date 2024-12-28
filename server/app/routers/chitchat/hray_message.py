from llm.agent.tool_rag import SearchReact

from . import router


@router.get("/quick_reply")
def quick_reply(msg: str):
    search_react = SearchReact()
    return search_react(msg)
