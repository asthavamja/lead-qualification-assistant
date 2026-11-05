import json
import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent
    / "docs"
    / "database"
    / "technova_company.sqlite3"
)

def get_structured_company_context():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        services = connection.execute(
            """
            SELECT slug, name, description, currency, price_min, price_max,
                   billing_period, timeline_min, timeline_max, timeline_unit,
                   price_note, details
            FROM service_catalog
            WHERE is_active = 1
            ORDER BY name
            """
        ).fetchall()
        process_steps = connection.execute(
            """
            SELECT step_number, name, description, timing_note
            FROM project_process_steps
            ORDER BY step_number
            """
        ).fetchall()
        policies = connection.execute(
            """
            SELECT category, title, policy_text, requires_human_review
            FROM company_policies
            ORDER BY category, policy_key
            """
        ).fetchall()

    sections = ["Structured company records (authoritative for these facts):"]
    for service in services:
        price = f"{service['currency']} {service['price_min']:,.0f}"
        if service["price_max"] is not None:
            price += f" to {service['currency']} {service['price_max']:,.0f}"
        if service["billing_period"]:
            price += f" per {service['billing_period']}"

        timeline = "Not specified"
        if service["timeline_min"] is not None:
            timeline = (
                f"{service['timeline_min']} to {service['timeline_max']} "
                f"{service['timeline_unit']}"
            )

        details = json.loads(service["details"])
        sections.extend(
            [
                f"\nService: {service['name']} ({service['slug']})",
                f"Description: {service['description']}",
                f"Price: {price}. {service['price_note']}",
                f"Typical timeline: {timeline}.",
                f"Additional details: {json.dumps(details, ensure_ascii=False)}",
            ]
        )

    if process_steps:
        sections.append("\nProject process:")
        for step in process_steps:
            timing = f" Timing: {step['timing_note']}" if step["timing_note"] else ""
            sections.append(
                f"{step['step_number']}. {step['name']}: "
                f"{step['description']}{timing}"
            )

    if policies:
        sections.append("\nCompany policies:")
        for policy in policies:
            review = (
                " Human review required."
                if policy["requires_human_review"]
                else ""
            )
            sections.append(
                f"[{policy['category']}] {policy['title']}: "
                f"{policy['policy_text']}{review}"
            )

    return "\n".join(sections)


def get_handoff_policy_context():
    with sqlite3.connect(DATABASE_PATH) as connection:
        policies = connection.execute(
            """
            SELECT title, policy_text
            FROM company_policies
            WHERE requires_human_review = 1
            ORDER BY policy_key
            """
        ).fetchall()

    return "\n".join(f"- {title}: {policy_text}" for title, policy_text in policies)
