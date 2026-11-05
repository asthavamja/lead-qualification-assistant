from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from qualifying import (
    State, initial_state, VISITOR_FIELDS,
    router_node, qualify_node, qa_node, reply_node,score_node,get_missing_fields
)
from slack_alert import send_slack,format_lead
from leads import save_lead
HANDOFF_REASONS = {
    "human_request": "Visitor asked to talk to a person",
    "angry": "Visitor seems frustrated",
    "quote_request": "Visitor asked for an exact quote",
}
def handoff_node(state):
    reason = state.get("handoff_reason") or HANDOFF_REASONS[state["route"]["handoff"]]
    return {
        "handoff_flag": True,
        "handoff_reason": reason,
        "messages": [
            (
                "assistant",
                "I'll pass your request to the TechNova team."
                if state["route"]["handoff"] != "none"
                else "I can't confirm that from the information available; it's something the TechNova team handles.",
            )
        ],
    }

def after_qualify(state):
    return "handoff" if state["route"]["handoff"] != "none" else "qa"

def after_qa(state):
    return "handoff" if state["handoff_flag"] else "compose"

def notify_node(state):
    if state["notified"]:
        return {"notified": True}
    complete = not get_missing_fields(state)
    urgent = state["route"]["handoff"] != "none" #or state["handoff_flag"]
    if urgent or complete:
        save_lead(state)
        if urgent or state["score"] in ("hot", "warm"):
            send_slack(format_lead(state))
        return {"notified": True}
    return {"notified": False}

builder = StateGraph(State)
builder.add_node("router", router_node)
builder.add_node("qualify", qualify_node)
builder.add_node("qa", qa_node)
builder.add_node("compose", reply_node)
builder.add_node("handoff", handoff_node)
builder.add_node("scoring",score_node)
builder.add_node("notify",notify_node)

builder.add_edge(START, "router")
builder.add_edge("router", "qualify")
builder.add_conditional_edges(
    "qualify",
    after_qualify,
    {"handoff": "handoff", "qa": "qa"},
)
# builder.add_conditional_edges(
#     "qa",
#     after_qa,
#     {"handoff": "handoff", "compose": "compose"},
# )
builder.add_edge("qa", "compose")
builder.add_edge("compose", "scoring")
builder.add_edge("scoring", "notify")
builder.add_edge("handoff", "notify")
builder.add_edge("notify",END)

graph = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "visitor-1"}}
    first = True
    
    while True:
        msg = input("You: ")
        if msg.lower() in ("exit", "quit"):
            break
        if first:
            inp = {**initial_state, "messages": [("human", msg)]}
            first = False
        else:
            inp = {"messages": [("human", msg)]}
        result = graph.invoke(inp, config)
        print("Bot:", result["messages"][-1].content)
        print({f: result[f] for f in VISITOR_FIELDS})
        print("handoff:", result["handoff_flag"], "|", result["handoff_reason"])
        print("route:", result["route"])