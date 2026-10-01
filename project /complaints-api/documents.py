"""Synthetic documents for the Banking Complaints Intelligence project.

All policies, terms, guidance and case decisions are fictional.
They are training data, not real regulatory guidance or legal advice.
"""

DOCUMENTS = [
    {
        "id": "doc-001",
        "title": "Complaint Handling Policy",
        "type": "policy",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "SYNTHETIC INTERNAL POLICY. Applies to mortgage and credit card "
            "complaints at the fictional bank.\n\n"
            "Staff must record the customer's concern, the product involved, "
            "the relevant dates and the outcome the customer is seeking. "
            "Distinguish the customer's account from facts verified through "
            "bank records. Identify missing evidence before recommending "
            "an outcome.\n\n"
            "For disputed payments or charges, review account entries, "
            "payment records, applicable terms and relevant correspondence. "
            "Check recorded communication and support needs.\n\n"
            "The final response must explain the findings, the evidence "
            "used and any corrective action. An authorised staff member "
            "must approve the outcome before the complaint is marked resolved. "
            "An AI recommendation does not constitute approval."
        ),
    },
    {
        "id": "doc-002",
        "title": "Vulnerable Customer Support Policy",
        "type": "policy",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "SYNTHETIC INTERNAL POLICY. Staff must review recorded support "
            "needs when handling a complaint and confirm with the customer "
            "whether those arrangements remain suitable.\n\n"
            "Examples include large-print letters, written follow-up after "
            "telephone conversations and referral to a specialist support "
            "team when a customer reports financial difficulty. Record agreed "
            "arrangements and use them in subsequent communication.\n\n"
            "If an agreed accessible format was not provided, arrange a "
            "suitable replacement and investigate the communication failure.\n\n"
            "Do not infer vulnerability from a customer's name or segment. "
            "A vulnerability flag alone does not establish complaint severity, "
            "bank error or entitlement to compensation. Assess the issue "
            "and its impact using the available evidence."
        ),
    },
    {
        "id": "doc-003",
        "title": "Synthetic Regulatory Guidance: Fair Complaint Handling",
        "type": "regulatory_guidance",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "FICTIONAL REGULATORY-STYLE GUIDANCE FOR TRAINING. This document "
            "is not issued by a regulator and does not state actual legal "
            "requirements or statutory deadlines.\n\n"
            "For this prototype, fair complaint handling means investigating "
            "the available evidence, considering individual circumstances "
            "and explaining the reasons for the decision clearly. Similar "
            "cases should be assessed using consistent principles, while "
            "material differences must be considered.\n\n"
            "Complaint records should distinguish allegations, verified "
            "findings and approved actions. Repeated themes should prompt "
            "further investigation; frequency alone does not prove a root "
            "cause. Unsupported conclusions must be referred for review "
            "rather than presented as established facts."
        ),
    },
    {
        "id": "doc-004",
        "title": "Mortgage Product Terms: Payments and Charges",
        "type": "product_terms",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "SYNTHETIC PRODUCT TERMS. These complaint-relevant terms apply "
            "to PRD-001 Two-Year Fixed Mortgage, PRD-002 Five-Year Fixed "
            "Mortgage and PRD-003 Tracker Mortgage.\n\n"
            "The payment amount and due date are recorded in the individual "
            "customer's payment schedule. A late-payment fee may apply when "
            "payment is received after that date, subject to the applicable "
            "account conditions. This document does not specify fee amounts.\n\n"
            "When a fee is disputed, establish the due date, bank receipt "
            "date and account posting date. Evidence that money left another "
            "account does not by itself establish when the bank received it.\n\n"
            "Where an internal processing error delayed an on-time payment, "
            "staff should recommend correction of the payment record and "
            "reversal of charges caused by that error, subject to approval. "
            "Refer reported financial difficulty for appropriate support."
        ),
    },
    {
        "id": "doc-005",
        "title": "Credit Card Product Terms: Fees and Corrections",
        "type": "product_terms",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "SYNTHETIC PRODUCT TERMS. These complaint-relevant terms apply "
            "to PRD-004 Everyday Credit Card and PRD-005 Rewards Credit Card.\n\n"
            "Product-specific fees are set out in the customer's applicable "
            "fee schedule. This document does not provide those amounts. "
            "Staff must check the schedule and statement entries before "
            "deciding whether a disputed fee was charged correctly.\n\n"
            "Where the bank has charged the same annual fee twice in error, "
            "staff should recommend reversal of the duplicate charge, "
            "subject to approval. Two entries must be investigated before "
            "being treated as a confirmed duplicate.\n\n"
            "A correctly applied fee is not automatically refundable because "
            "the customer disputes it. A separate communication failure may "
            "still require an apology and a clearer explanation."
        ),
    },
    {
        "id": "doc-006",
        "title": "Redress Methodology and Approval Rules",
        "type": "redress_guidance",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "SYNTHETIC INTERNAL METHODOLOGY. Redress recommendations must "
            "identify the established error, the resulting impact and "
            "the evidence supporting the proposed remedy.\n\n"
            "Possible corrective actions include reversing an erroneous "
            "charge, correcting a payment date, recalculating affected "
            "interest or replacing an inaccessible letter. Any monetary "
            "correction must use verified account amounts and avoid "
            "duplicating an adjustment already made.\n\n"
            "This document contains no fixed compensation tariff for "
            "distress or inconvenience. An exact award cannot be derived "
            "from a complaint theme, vulnerability flag or previous case "
            "alone. Missing evidence must be identified and referred "
            "to an authorised reviewer.\n\n"
            "Only authorised staff may approve redress or payments. "
            "The assistant may recommend further checks but cannot "
            "promise compensation or authorise an outcome."
        ),
    },
    {
        "id": "doc-007",
        "title": "Fictional Ombudsman-Style Decision: Mortgage Payment Error",
        "type": "case_decision",
        "date": "2026-08-18",
        "version": "1.0",
        "body": (
            "FICTIONAL OMBUDSMAN-STYLE CASE FOR TRAINING. This is not an "
            "authentic decision or a record from the bank's complaint list.\n\n"
            "The customer disputed a mortgage late-payment fee. The reviewer "
            "examined the payment schedule, bank receipt timestamp and "
            "mortgage account ledger. These showed that the bank received "
            "payment before the due date but posted it two days later.\n\n"
            "The complaint was upheld because the fee resulted from the "
            "bank's processing error. The remedy was to correct the payment "
            "date and reverse the resulting fee.\n\n"
            "The decisive evidence was the bank receipt timestamp. A new "
            "case requires its own evidence; a customer stating that payment "
            "was sent on time is not sufficient to assume the same finding."
        ),
    },
    {
        "id": "doc-008",
        "title": "Fictional Ombudsman-Style Decision: Incorrect Card Charge",
        "type": "case_decision",
        "date": "2026-08-24",
        "version": "1.0",
        "body": (
            "FICTIONAL OMBUDSMAN-STYLE CASE FOR TRAINING. This is not an "
            "authentic decision or a record from the bank's complaint list.\n\n"
            "A customer challenged two annual card fees on one statement. "
            "The reviewer compared the statement, fee schedule and internal "
            "posting records. The evidence confirmed that one annual fee "
            "had been posted twice for the same charging period.\n\n"
            "The complaint was upheld and the duplicate fee was reversed. "
            "The valid annual fee remained payable. The bank provided a "
            "written explanation of the correction.\n\n"
            "This example supports checking whether apparently similar "
            "entries are genuinely duplicates. It does not establish that "
            "every disputed fee is incorrect or that additional compensation "
            "is automatically due."
        ),
    },
    {
        "id": "doc-009",
        "title": (
            "Fictional Ombudsman-Style Decision: Communication "
            "and Support Failure"
        ),
        "type": "case_decision",
        "date": "2026-09-01",
        "version": "1.0",
        "body": (
            "FICTIONAL OMBUDSMAN-STYLE CASE FOR TRAINING. This is not an "
            "authentic decision or a record from the bank's complaint list.\n\n"
            "The customer had requested large-print correspondence. "
            "The request was recorded, but the bank sent a complaint "
            "response in standard print. Review confirmed that staff "
            "had not applied the agreed communication arrangement.\n\n"
            "The communication complaint was upheld. The bank supplied "
            "a large-print response, apologised and checked that the "
            "customer's preference was available to the handling team.\n\n"
            "This finding concerned access to information. It did not "
            "establish that a separately disputed product charge was "
            "incorrect. The reviewer required that issue to be assessed "
            "using the applicable terms and account evidence."
        ),
    },
    {
        "id": "doc-010",
        "title": "Complaint Classification and Escalation Procedure",
        "type": "procedure",
        "date": "2026-07-01",
        "version": "1.0",
        "body": (
            "SYNTHETIC INTERNAL PROCEDURE. Classify the main complaint issue "
            "as late_payment_fee, incorrect_charge, payment_processing_delay, "
            "communication_failure, accessibility_issue or other. "
            "Use unclassified when the issue is not yet clear.\n\n"
            "Assess severity from recorded impact and urgency. Low severity "
            "covers limited impact with no identified ongoing harm. Medium "
            "covers disputed charges or service failures requiring review. "
            "High covers substantial impact or an urgent unresolved problem, "
            "such as a missing mortgage payment with potential further "
            "financial consequences. Use unassessed when facts are insufficient.\n\n"
            "Model classifications are proposals for staff review. For an "
            "unclear statement complaint, ask which entry is disputed and "
            "why before assigning a specific theme. Escalate urgent harm "
            "and unresolved evidence gaps to an appropriate specialist. "
            "A support flag alone must not determine severity."
        ),
    },
]