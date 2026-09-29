from datetime import datetime, timedelta

from autoclose import AUTO_CLOSE_LABEL, close_inactive_tickets
from tickets import Ticket

NOW = datetime(2026, 9, 10, 12, 0, 0)


def make_ticket(status="open", hours_since_reply=0, closed_by=None) -> Ticket:
    return Ticket(
        id="HD-TEST",
        customer="Test Customer",
        subject="Test subject",
        priority="Normal",
        status=status,
        created_at=NOW - timedelta(days=5),
        last_customer_reply_at=NOW - timedelta(hours=hours_since_reply),
        reply_deadline=NOW + timedelta(days=1),
        closed_by=closed_by,
    )


def test_closes_ticket_silent_for_more_than_24_hours():
    ticket = make_ticket(hours_since_reply=25)

    closed = close_inactive_tickets([ticket], now=NOW)

    assert closed == [ticket]
    assert ticket.status == "closed"
    assert ticket.closed_by == AUTO_CLOSE_LABEL


def test_closes_ticket_at_exactly_24_hours():
    ticket = make_ticket(hours_since_reply=24)

    closed = close_inactive_tickets([ticket], now=NOW)

    assert ticket.status == "closed"
    assert closed == [ticket]


def test_leaves_ticket_open_under_24_hours():
    ticket = make_ticket(hours_since_reply=23)

    closed = close_inactive_tickets([ticket], now=NOW)

    assert closed == []
    assert ticket.status == "open"


def test_ignores_already_closed_tickets():
    ticket = make_ticket(status="closed", hours_since_reply=100, closed_by="Jamie")

    closed = close_inactive_tickets([ticket], now=NOW)

    assert closed == []
    assert ticket.closed_by == "Jamie"


def test_only_closes_the_stale_tickets_in_a_mixed_batch():
    stale = make_ticket(hours_since_reply=48)
    fresh = make_ticket(hours_since_reply=1)
    already_closed = make_ticket(status="closed", hours_since_reply=200, closed_by="Jamie")

    closed = close_inactive_tickets([stale, fresh, already_closed], now=NOW)

    assert closed == [stale]
    assert fresh.status == "open"
    assert already_closed.closed_by == "Jamie"


def test_custom_inactivity_threshold():
    ticket = make_ticket(hours_since_reply=2)

    closed = close_inactive_tickets([ticket], now=NOW, inactivity_threshold=timedelta(hours=1))

    assert closed == [ticket]
    assert ticket.status == "closed"
