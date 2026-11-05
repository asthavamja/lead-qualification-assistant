import csv
import os
from datetime import datetime

FIELDS = ["time", "name", "contact", "service_name", "summary_of_product",
          "budget", "timeline_months", "decision_maker", "score", "handoff_reason"]

def save_lead(state, path="leads.csv"):
    new_file = not os.path.exists(path)
    row = {f: state.get(f) for f in FIELDS if f != "time"}
    row["time"] = datetime.now().isoformat(timespec="seconds")
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)

if __name__ == "__main__":
    save_lead({"name": "Rahul", "contact": "rahul@example.com", "service_name": "website",
               "summary_of_product": "jewellery shop site", "budget": 50000,
               "timeline_months": 2, "decision_maker": True, "score": "hot",
               "handoff_reason": None})
    print(open("leads.csv", encoding="utf-8").read())