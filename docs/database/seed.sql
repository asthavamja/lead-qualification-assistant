BEGIN;

INSERT INTO service_catalog (
    slug, name, description, price_min, price_max, billing_period,
    timeline_min, timeline_max, timeline_unit, price_note, details
)
VALUES
(
    'website',
    'Website Development',
    'Business websites, landing pages, e-commerce stores, and portfolio sites.',
    30000, 150000, NULL, 2, 6, 'weeks',
    'Approximate range. Final price and schedule depend on pages, design complexity, and features such as payments or admin panels.',
    '{"includes":["Mobile-friendly websites","SEO-ready websites"],"use_cases":["Business websites","Landing pages","E-commerce stores","Portfolio sites"],"cost_factors":["Number of pages","Design complexity","Online payments","Admin panels"]}'
),
(
    'mobile-app',
    'Mobile App Development',
    'Android and iOS mobile applications, typically built with a shared Flutter or React Native codebase.',
    200000, 800000, NULL, 2, 4, 'months',
    'Approximate range. Final price and schedule depend on features, platforms, and third-party integrations.',
    '{"includes":["UI/UX design","Backend and API development","App-store publishing"],"use_cases":["Delivery apps","Booking apps","E-learning apps","Customer-service apps"],"cost_factors":["Number of features","Platforms","Third-party integrations"],"technologies":["Flutter","React Native"]}'
),
(
    'custom-software',
    'Custom Software / ERP / CRM Setup',
    'Custom business software, ERP and CRM setup, Odoo customization, dashboards, and reporting tools.',
    300000, 1200000, NULL, 3, 6, 'months',
    'Approximate range. Final price and schedule depend on modules, users, and integrations with existing systems.',
    '{"use_cases":["Inventory management","Sales management","HR management","Accounting","Customer management"],"cost_factors":["Number of modules","Number of users","Integrations"],"technologies":["Odoo","HubSpot integrations"]}'
),
(
    'ai-automation',
    'AI and Automation Solutions',
    'AI chatbots, workflow automation, document processing, lead qualification bots, and business-tool integrations.',
    100000, 600000, NULL, 1, 3, 'months',
    'Approximate range. Final price and schedule depend on workflows, integrations, and AI features.',
    '{"includes":["Workflow automation"],"use_cases":["Support chatbots","Daily report automation","Document processing","Lead qualification"],"cost_factors":["Number of workflows","Integrations","AI features"],"technologies":["LangChain","LangGraph","n8n","OpenAI","Open-source models"]}'
),
(
    'maintenance',
    'Maintenance and Support',
    'Ongoing bug fixes, security updates, performance monitoring, small feature changes, and support.',
    10000, NULL, 'month', NULL, NULL, NULL,
    'Monthly plans start at INR 10,000. Existing systems are reviewed before maintenance is agreed.',
    '{"plans":[{"name":"Basic","monthly_price":10000,"includes":["Bug fixes","Updates","Email support"]},{"name":"Standard","monthly_price":20000,"includes":["Everything in Basic","Small feature changes","Faster response"]},{"name":"Premium","monthly_price":35000,"includes":["Everything in Standard","Priority support","Monthly performance reports"]}],"availability":"Can be added to TechNova projects or existing systems after a review."}'
)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    currency = EXCLUDED.currency,
    price_min = EXCLUDED.price_min,
    price_max = EXCLUDED.price_max,
    billing_period = EXCLUDED.billing_period,
    timeline_min = EXCLUDED.timeline_min,
    timeline_max = EXCLUDED.timeline_max,
    timeline_unit = EXCLUDED.timeline_unit,
    price_note = EXCLUDED.price_note,
    details = EXCLUDED.details,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO project_process_steps (step_number, name, description, timing_note)
VALUES
    (1, 'Enquiry', 'The client contacts TechNova through the website or chat.', NULL),
    (2, 'Discovery call', 'The team discusses the project requirements in detail.', 'Usually 30 to 45 minutes.'),
    (3, 'Proposal and quote', 'The team prepares a document with scope, timeline, and final price.', 'Within 3 to 5 working days after discovery.'),
    (4, 'Agreement and advance payment', 'The contract is signed and the project starts after an advance payment.', NULL),
    (5, 'Development', 'The project is developed in stages with regular progress updates.', NULL),
    (6, 'Testing and delivery', 'The team tests the completed work and hands it over to the client.', NULL),
    (7, 'Support', 'The project includes a free support period, with optional maintenance plans afterward.', '30 days of free bug-fix support after delivery.')
ON CONFLICT (step_number) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    timing_note = EXCLUDED.timing_note;

INSERT INTO company_policies (
    policy_key, category, title, policy_text, requires_human_review
)
VALUES
    ('price-estimates', 'pricing', 'Price estimates',
     'Published prices are approximate ranges. Final price is decided after a discovery call and a written proposal.', 0),
    ('exact-quotes', 'handoff', 'Exact quotes and final pricing',
     'Do not provide or promise an exact quote or final price. Hand the request to the TechNova team.', 1),
    ('payment-terms', 'payments', 'Payment terms',
     'Typical structure: 30% advance, 40% on milestones, and 30% on delivery. Exact terms are confirmed in the proposal. Bank transfer and UPI are accepted; GST invoices are provided.', 0),
    ('legal-and-nda', 'handoff', 'Contracts and NDA details',
     'Hand questions about contract terms or NDA details to the TechNova team. The company is willing to sign an NDA before discussing project details.', 1),
    ('technical-architecture', 'handoff', 'Detailed technical architecture',
     'Hand detailed technical architecture discussions to the TechNova team.', 1),
    ('discounts-and-negotiation', 'handoff', 'Discounts and negotiation',
     'Hand requests for discounts or price negotiation to the TechNova team.', 1),
    ('existing-project-complaints', 'handoff', 'Existing project complaints',
     'Hand complaints or issues about an existing TechNova project to the TechNova team.', 1),
    ('unknown-information', 'handoff', 'Information not in approved sources',
     'Do not guess or invent company facts. Hand questions not covered by approved company information to the TechNova team.', 1),
    ('sales-response-time', 'sales', 'Sales response time',
     'The sales team aims to contact new leads within one working day.', 0),
    ('office-hours', 'support', 'Office hours',
     'Monday to Saturday, 10 AM to 7 PM IST.', 0),
    ('support-period', 'support', 'Post-delivery support',
     'Every project includes 30 days of free bug-fix support after delivery. Optional maintenance plans are available afterward.', 0),
    ('free-discovery-call', 'sales', 'Discovery call',
     'The first discovery call is free.', 0)
ON CONFLICT (policy_key) DO UPDATE SET
    category = EXCLUDED.category,
    title = EXCLUDED.title,
    policy_text = EXCLUDED.policy_text,
    requires_human_review = EXCLUDED.requires_human_review;

COMMIT;
