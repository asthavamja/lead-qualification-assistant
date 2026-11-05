# Sales Agent Documents

## Knowledge sources

- `technova_knowledge_base.md` is the source currently used by the retrieval
  script for customer-facing answers.
- `database/` contains the SQLite schema and initial structured company data
  for services, prices, process steps, and policies. `company_data.py` reads
  these records for customer-facing answers.
- `examples/` contains format examples only. The current retrieval script does
  not index that folder.

## SQLite setup

From the project folder, run:

```powershell
python docs/database/setup_db.py
```

This uses Python's built-in SQLite support to create
`docs/database/technova_company.sqlite3`, apply `database/schema.sql`, and load
the initial records from `database/seed.sql`. Running it again safely refreshes
the seeded records. No extra Python package or database server is required.

The chatbot uses SQLite as the authoritative source for structured facts and
the Markdown knowledge base for explanatory content and FAQs. Leads remain in
CSV.

## Adding or updating information

Use clear headings and short, factual sections. Keep prices and timelines
explicitly marked as estimates when they are not guaranteed. Update structured
facts in the SQLite database by editing `database/seed.sql` and rerunning the
setup script. Update explanatory content and FAQs in the knowledge base.
Structured database records take precedence if sources conflict.

Before sharing information with customers, confirm that contact details,
pricing, timelines, policies, and service descriptions are current and approved.

## Example files

- `examples/service-profile.example.md` shows a reusable service-document format.
- `examples/faq.example.md` shows a reusable FAQ format.
- `database/schema.sql` defines the structured SQLite tables.
- `database/seed.sql` loads the initial structured company information.
