import os
import requests
from dotenv import load_dotenv
from qualifying import extractor
load_dotenv()

def format_lead(state):
    score = state["score"] or "unscored"
    lines = [
        f"{score.upper()} lead: {state['name'] or 'Unknown'}",
        f"Service: {state['service_name']} ({state['summary_of_product']})",
        f"Budget: {state['budget']} | Timeline: {state['timeline_months']} months",
        f"Decision-maker: {state['decision_maker']}",
        f"Contact: {state['contact']}",
    ]
    if state["handoff_reason"]:
        lines.append(f"Note for the team: {state['handoff_reason']}")
    return "\n".join(lines)

def send_slack(text):
    r = requests.post(os.getenv("SLACK_LEADS_WEBHOOK"), json={"text": text}, timeout=10)
    return r.status_code

if __name__ == "__main__":
    fake = {
        "name": "Rahul", "contact": "rahul@example.com",
        "service_name": "website", "summary_of_product": "website for jewellery shop",
        "budget": 50000, "timeline_months": 2, "decision_maker": True,
        "score": "hot",
        "handoff_reason": "Unanswered question: which server do you host on?",
    }
    print(format_lead(fake))
    print(send_slack(format_lead(fake)))