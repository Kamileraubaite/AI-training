"""A labelled eval set for retrieval and answer quality.

Each answerable question records:
  doc_id    the document that holds the answer
  evidence  a short verbatim span from that document. A retrieved chunk
            counts as a hit only if it contains this exact span.
  keywords  what a correct answer must mention. Every item must appear.
            "a|b" means either is acceptable. A trailing * allows endings.
  kind      what the question tests

Unanswerable questions have doc_id None and no evidence.
The correct behaviour is refusal.
"""

EVAL_SET = [
    # Complaint Handling Policy (doc-001)
    {"id": "q01", "question": "What information must staff record when a complaint is received?",
     "doc_id": "doc-001", "evidence": "the customer's concern, the product involved, the relevant dates and the outcome the customer is seeking",
     "keywords": ["concern", "product", "dates", "outcome"], "kind": "lookup"},
    {"id": "q02", "question": "Who must approve an outcome before a complaint is marked resolved?",
     "doc_id": "doc-001", "evidence": "An authorised staff member must approve the outcome before the complaint is marked resolved.",
     "keywords": ["authorised", "staff"], "kind": "lookup"},
    {"id": "q03", "question": "Does an AI recommendation constitute approval of a complaint outcome?",
     "doc_id": "doc-001", "evidence": "An AI recommendation does not constitute approval.",
     "keywords": ["not|no"], "kind": "negation"},

    # Vulnerable Customer Support Policy (doc-002)
    {"id": "q04", "question": "What should staff do if an agreed accessible format was not provided?",
     "doc_id": "doc-002", "evidence": "arrange a suitable replacement and investigate the communication failure",
     "keywords": ["replace*", "investigat*"], "kind": "lookup"},
    {"id": "q05", "question": "Can staff infer vulnerability from a customer's name or segment?",
     "doc_id": "doc-002", "evidence": "Do not infer vulnerability from a customer's name or segment.",
     "keywords": ["not|no", "name", "segment"], "kind": "negation"},
    {"id": "q06", "question": "Does a vulnerability flag alone establish entitlement to compensation?",
     "doc_id": "doc-002", "evidence": "A vulnerability flag alone does not establish complaint severity, bank error or entitlement to compensation.",
     "keywords": ["not|no"], "kind": "negation"},

    # Synthetic Regulatory Guidance (doc-003)
    {"id": "q07", "question": "Does a repeated complaint theme prove a root cause?",
     "doc_id": "doc-003", "evidence": "frequency alone does not prove a root cause",
     "keywords": ["not|no"], "kind": "negation"},
    {"id": "q08", "question": "What distinctions should complaint records make?",
     "doc_id": "doc-003", "evidence": "Complaint records should distinguish allegations, verified findings and approved actions.",
     "keywords": ["allegations", "findings", "actions"], "kind": "lookup"},

    # Mortgage Product Terms (doc-004)
    {"id": "q09", "question": "What dates should staff establish when a mortgage late-payment fee is disputed?",
     "doc_id": "doc-004", "evidence": "establish the due date, bank receipt date and account posting date",
     "keywords": ["due date", "bank receipt date", "account posting date"], "kind": "lookup"},
    {"id": "q10", "question": "Does money leaving another account prove when the bank received a mortgage payment?",
     "doc_id": "doc-004", "evidence": "Evidence that money left another account does not by itself establish when the bank received it.",
     "keywords": ["not|no", "receiv*"], "kind": "negation"},
    {"id": "q11", "question": "Which product is PRD-003 in the mortgage terms?",
     "doc_id": "doc-004", "evidence": "PRD-003 Tracker Mortgage",
     "keywords": ["Tracker Mortgage"], "kind": "exact-id"},
    {"id": "q12", "question": "What should staff recommend if an internal processing error delayed an on-time mortgage payment?",
     "doc_id": "doc-004", "evidence": "correction of the payment record and reversal of charges caused by that error, subject to approval",
     "keywords": ["correct*", "revers*", "approval"], "kind": "lookup"},

    # Credit Card Product Terms (doc-005)
    {"id": "q13", "question": "What should staff check before deciding whether a disputed card fee was charged correctly?",
     "doc_id": "doc-005", "evidence": "Staff must check the schedule and statement entries before deciding whether a disputed fee was charged correctly.",
     "keywords": ["schedule", "statement"], "kind": "lookup"},
    {"id": "q14", "question": "Should two annual fee entries immediately be treated as a confirmed duplicate?",
     "doc_id": "doc-005", "evidence": "Two entries must be investigated before being treated as a confirmed duplicate.",
     "keywords": ["investigat*"], "kind": "negation"},
    {"id": "q15", "question": "Is a correctly applied card fee automatically refundable because the customer disputes it?",
     "doc_id": "doc-005", "evidence": "A correctly applied fee is not automatically refundable because the customer disputes it.",
     "keywords": ["not|no"], "kind": "negation"},
    {"id": "q16", "question": "Which product is PRD-005 in the credit card terms?",
     "doc_id": "doc-005", "evidence": "PRD-005 Rewards Credit Card",
     "keywords": ["Rewards Credit Card"], "kind": "exact-id"},

    # Redress Methodology (doc-006)
    {"id": "q17", "question": "What must a redress recommendation identify?",
     "doc_id": "doc-006", "evidence": "the established error, the resulting impact and the evidence supporting the proposed remedy",
     "keywords": ["error", "impact", "evidence"], "kind": "lookup"},
    {"id": "q18", "question": "Who may approve redress or payments?",
     "doc_id": "doc-006", "evidence": "Only authorised staff may approve redress or payments.",
     "keywords": ["authorised", "staff"], "kind": "lookup"},
    {"id": "q19", "question": "Does the redress methodology provide a fixed compensation tariff for distress or inconvenience?",
     "doc_id": "doc-006", "evidence": "This document contains no fixed compensation tariff for distress or inconvenience.",
     "keywords": ["no|not"], "kind": "negation"},

    # Fictional Mortgage Payment Decision (doc-007)
    {"id": "q20", "question": "How late did the bank post the payment in the fictional mortgage payment error case?",
     "doc_id": "doc-007", "evidence": "posted it two days later",
     "keywords": ["two|2", "days"], "kind": "numeric"},
    {"id": "q21", "question": "What was the decisive evidence in the fictional mortgage payment error case?",
     "doc_id": "doc-007", "evidence": "The decisive evidence was the bank receipt timestamp.",
     "keywords": ["bank receipt timestamp"], "kind": "lookup"},
    {"id": "q22", "question": "What remedy was used in the fictional mortgage payment error case?",
     "doc_id": "doc-007", "evidence": "The remedy was to correct the payment date and reverse the resulting fee.",
     "keywords": ["correct*", "payment date", "revers*"], "kind": "lookup"},

    # Fictional Incorrect Card Charge Decision (doc-008)
    {"id": "q23", "question": "Which records did the reviewer compare in the fictional duplicate card fee case?",
     "doc_id": "doc-008", "evidence": "The reviewer compared the statement, fee schedule and internal posting records.",
     "keywords": ["statement", "fee schedule", "posting records"], "kind": "lookup"},
    {"id": "q24", "question": "Did the valid annual fee remain payable after the duplicate card fee was reversed?",
     "doc_id": "doc-008", "evidence": "The valid annual fee remained payable.",
     "keywords": ["payable"], "kind": "lookup"},

    # Fictional Communication and Support Decision (doc-009)
    {"id": "q25", "question": "What format had the customer requested in the fictional communication and support failure case?",
     "doc_id": "doc-009", "evidence": "The customer had requested large-print correspondence.",
     "keywords": ["large-print|large print"], "kind": "lookup"},
    {"id": "q26", "question": "Did the communication failure establish that a separately disputed product charge was incorrect?",
     "doc_id": "doc-009", "evidence": "It did not establish that a separately disputed product charge was incorrect.",
     "keywords": ["not|no"], "kind": "negation"},

    # Complaint Classification and Escalation Procedure (doc-010)
    {"id": "q27", "question": "What classification should be used when the complaint issue is not yet clear?",
     "doc_id": "doc-010", "evidence": "Use unclassified when the issue is not yet clear.",
     "keywords": ["unclassified"], "kind": "lookup"},
    {"id": "q28", "question": "What severity label should be used when the facts are insufficient?",
     "doc_id": "doc-010", "evidence": "Use unassessed when facts are insufficient.",
     "keywords": ["unassessed"], "kind": "lookup"},
    {"id": "q29", "question": "Can a support flag alone determine complaint severity?",
     "doc_id": "doc-010", "evidence": "A support flag alone must not determine severity.",
     "keywords": ["not|no"], "kind": "negation"},

    # Unanswerable: the documents do not contain these answers
    {"id": "q30", "question": "How do I repair a bicycle puncture?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q31", "question": "Exactly how many pounds of compensation are guaranteed for CMP-001?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
    {"id": "q32", "question": "What is the exact annual fee in pounds for PRD-004?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
]


def answerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is not None]


def unanswerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is None]