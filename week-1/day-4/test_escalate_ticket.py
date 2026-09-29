from datetime import datetime, timedelta

from tickets import Ticket, escalate_ticket

NOW = datetime(2026, 9, 10, 12, 0, 0)


def make_ticket(status="open", priority="Normal", days_since_reply=0) -> Ticket:
    return Ticket(
        id="HD-TEST",
        customer="Test Customer",
        subject="Test subject",
        priority=priority,
        status=status,
        created_at=NOW - timedelta(days=10),
        last_customer_reply_at=NOW - timedelta(days=days_since_reply),
        reply_deadline=NOW + timedelta(days=1),
    )


def test_escalates_ticket_silent_for_5_or_more_days():
    ticket = make_ticket(days_since_reply=5)

    escalated = escalate_ticket(ticket, now=NOW)

    assert escalated is True
    assert ticket.priority == "Urgent"
    assert ticket.escalated_by == "system"


def test_leaves_ticket_normal_under_5_days():
    ticket = make_ticket(days_since_reply=4)

    escalated = escalate_ticket(ticket, now=NOW)

    assert escalated is False
    assert ticket.priority == "Normal"
    assert ticket.escalated_by is None


def test_ignores_already_urgent_ticket():
    ticket = make_ticket(priority="Urgent", days_since_reply=10)

    escalated = escalate_ticket(ticket, now=NOW)

    assert escalated is False
    assert ticket.priority == "Urgent"
    assert ticket.escalated_by is None


def test_ignores_closed_ticket():
    ticket = make_ticket(status="closed", days_since_reply=10)

    escalated = escalate_ticket(ticket, now=NOW)

    assert escalated is False
    assert ticket.priority == "Normal"
    assert ticket.escalated_by is None


def test_ignores_merged_ticket():
    ticket = make_ticket(status="Merged", days_since_reply=5)

    escalated = escalate_ticket(ticket, now=NOW)

    assert escalated is False
    assert ticket.priority == "Normal"
    assert ticket.escalated_by is None
