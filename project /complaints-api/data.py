"""Synthetic records for the Banking Complaints Intelligence project."""

# Each dictionary represents one fictional customer.
CUSTOMERS = [
    {
        "id": "CUST-001",
        "name": "Amira Bennett",
        "segment": "standard_retail",
        "vulnerability_flag": True,
        "support_needs": "Requests large-print letters.",
    },
    {
        "id": "CUST-002",
        "name": "Daniel Mercer",
        "segment": "standard_retail",
        "vulnerability_flag": False,
        "support_needs": None,
    },
    {
        "id": "CUST-003",
        "name": "Priya Lawson",
        "segment": "premium_retail",
        "vulnerability_flag": True,
        "support_needs": (
            "Has reported financial difficulty and requests "
            "help from the specialist support team."
        ),
    },
    {
        "id": "CUST-004",
        "name": "Oliver Shah",
        "segment": "standard_retail",
        "vulnerability_flag": False,
        "support_needs": None,
    },
    {
        "id": "CUST-005",
        "name": "Leah Foster",
        "segment": "premium_retail",
        "vulnerability_flag": True,
        "support_needs": (
            "Requests written follow-up after telephone conversations "
            "to help review the information."
        ),
    },
]

# Each dictionary represents a fictional banking product.
PRODUCTS = [
    {
        "id": "PRD-001",
        "name": "Two-Year Fixed Mortgage",
        "product_type": "mortgage",
        "terms_document_id": "doc-004",
    },
    {
        "id": "PRD-002",
        "name": "Five-Year Fixed Mortgage",
        "product_type": "mortgage",
        "terms_document_id": "doc-004",
    },
    {
        "id": "PRD-003",
        "name": "Tracker Mortgage",
        "product_type": "mortgage",
        "terms_document_id": "doc-004",
    },
    {
        "id": "PRD-004",
        "name": "Everyday Credit Card",
        "product_type": "credit_card",
        "terms_document_id": "doc-005",
    },
    {
        "id": "PRD-005",
        "name": "Rewards Credit Card",
        "product_type": "credit_card",
        "terms_document_id": "doc-005",
    },
]

# Each dictionary represents a fictional complaint.
# Unresolved complaints have no resolution date, summary or outcome.
COMPLAINTS = [
    {
        "id": "CMP-001",
        "customer_id": "CUS-001",
        "product_id": "PRD-001",
        "description": (
            "The customer disputes a mortgage late-payment fee. "
            "They say the payment left their account before the due date. "
            "The payment receipt and processing dates have not been checked."
        ),
        "channel": "phone",
        "received_date": "2026-09-28",
        "theme": "late_payment_fee",
        "severity": "medium",
        "status": "open",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    },
    {
        "id": "CMP-002",
        "customer_id": "CUS-002",
        "product_id": "PRD-001",
        "description": (
            "The customer disputed a mortgage late-payment fee. "
            "Investigation confirmed that the bank received the payment "
            "on time but posted it to the mortgage account late."
        ),
        "channel": "email",
        "received_date": "2026-08-03",
        "theme": "late_payment_fee",
        "severity": "medium",
        "status": "resolved",
        "resolved_date": "2026-08-12",
        "resolution_summary": (
            "The bank reversed the fee, corrected the payment record "
            "and sent an apology explaining the processing error."
        ),
        "outcome": "upheld",
    },
    {
        "id": "CMP-003",
        "customer_id": "CUS-003",
        "product_id": "PRD-002",
        "description": (
            "The customer disputed a mortgage late-payment fee. "
            "Account records confirmed that the payment arrived after "
            "the due date. The customer had reported financial difficulty."
        ),
        "channel": "phone",
        "received_date": "2026-08-10",
        "theme": "late_payment_fee",
        "severity": "medium",
        "status": "resolved",
        "resolved_date": "2026-08-21",
        "resolution_summary": (
            "Review found that the fee was applied in line with the "
            "applicable terms, so it was retained. With the customer's "
            "agreement, staff arranged specialist support."
        ),
        "outcome": "not_upheld",
    },
    {
        "id": "CMP-004",
        "customer_id": "CUS-004",
        "product_id": "PRD-004",
        "description": (
            "The customer reports two annual card fees on the same "
            "statement and believes one was charged in error. "
            "The statement entries have not yet been verified."
        ),
        "channel": "online",
        "received_date": "2026-09-25",
        "theme": "incorrect_charge",
        "severity": "medium",
        "status": "under_review",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    },
    {
        "id": "CMP-005",
        "customer_id": "CUS-005",
        "product_id": "PRD-004",
        "description": (
            "The customer reported a duplicate annual card fee. "
            "Investigation confirmed that the bank had charged "
            "the same fee twice."
        ),
        "channel": "email",
        "received_date": "2026-08-05",
        "theme": "incorrect_charge",
        "severity": "medium",
        "status": "resolved",
        "resolved_date": "2026-08-14",
        "resolution_summary": (
            "The bank refunded the duplicate fee and provided "
            "written confirmation of the correction."
        ),
        "outcome": "upheld",
    },
    {
        "id": "CMP-006",
        "customer_id": "CUS-002",
        "product_id": "PRD-005",
        "description": (
            "The customer disputed a card fee and said that staff had "
            "not explained it clearly. Review found that the fee matched "
            "the terms, but the bank's initial explanation was incomplete."
        ),
        "channel": "phone",
        "received_date": "2026-09-02",
        "theme": "incorrect_charge",
        "severity": "low",
        "status": "resolved",
        "resolved_date": "2026-09-11",
        "resolution_summary": (
            "The fee was retained. The bank apologised for the incomplete "
            "explanation and sent a clear breakdown with the relevant terms."
        ),
        "outcome": "partially_upheld",
    },
    {
        "id": "CMP-007",
        "customer_id": "CUS-003",
        "product_id": "PRD-003",
        "description": (
            "The customer says a mortgage payment has not appeared "
            "on their account five days after they sent it. "
            "They are concerned that further charges may be applied."
        ),
        "channel": "phone",
        "received_date": "2026-09-29",
        "theme": "payment_processing_delay",
        "severity": "high",
        "status": "open",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    },
    {
        "id": "CMP-008",
        "customer_id": "CUS-004",
        "product_id": "PRD-003",
        "description": (
            "The customer reported a missing mortgage payment. "
            "Investigation located the payment in the bank's "
            "unallocated payments account."
        ),
        "channel": "branch",
        "received_date": "2026-08-17",
        "theme": "payment_processing_delay",
        "severity": "high",
        "status": "resolved",
        "resolved_date": "2026-08-25",
        "resolution_summary": (
            "The bank allocated the payment to the mortgage, corrected "
            "its effective date and reversed the resulting interest error."
        ),
        "outcome": "upheld",
    },
    {
        "id": "CMP-009",
        "customer_id": "CUS-005",
        "product_id": "PRD-005",
        "description": (
            "The customer says they were promised a written explanation "
            "of a card payment issue after a telephone call, "
            "but no follow-up has arrived."
        ),
        "channel": "email",
        "received_date": "2026-09-24",
        "theme": "communication_failure",
        "severity": "medium",
        "status": "open",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    },
    {
        "id": "CMP-010",
        "customer_id": "CUS-002",
        "product_id": "PRD-005",
        "description": (
            "The customer complained that the bank had not sent "
            "a promised written explanation of a card account adjustment. "
            "Review confirmed that the follow-up had been missed."
        ),
        "channel": "online",
        "received_date": "2026-09-04",
        "theme": "communication_failure",
        "severity": "medium",
        "status": "resolved",
        "resolved_date": "2026-09-15",
        "resolution_summary": (
            "The bank sent the explanation, apologised for the delay "
            "and confirmed that the customer had received it."
        ),
        "outcome": "upheld",
    },
    {
        "id": "CMP-011",
        "customer_id": "CUS-001",
        "product_id": "PRD-001",
        "description": (
            "The customer reports receiving a standard-print mortgage "
            "letter despite a recorded request for large-print letters. "
            "They say they cannot comfortably read the information."
        ),
        "channel": "phone",
        "received_date": "2026-09-30",
        "theme": "accessibility_issue",
        "severity": "medium",
        "status": "open",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    },
    {
        "id": "CMP-012",
        "customer_id": "CUS-004",
        "product_id": "PRD-004",
        "description": (
            "The customer says something on their latest card statement "
            "does not look right. They have not identified the entry "
            "or explained what they believe is incorrect."
        ),
        "channel": "online",
        "received_date": "2026-09-30",
        "theme": "unclassified",
        "severity": "unassessed",
        "status": "open",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    },
]
