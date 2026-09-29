from datetime import datetime, timedelta
from typing import List, Optional

from tickets import Ticket

DEFAULT_INACTIVITY = timedelta(hours=24)
AUTO_CLOSE_LABEL = "system (auto-closed: 24h inactivity)"


def close_inactive_tickets(
    tickets: List[Ticket],
    now: Optional[datetime] = None,
    inactivity_threshold: timedelta = DEFAULT_INACTIVITY,
) -> List[Ticket]:
    """Close open tickets whose customer has gone silent past the threshold.

    A ticket is closed when it is still "open" and the time since its last
    customer reply meets or exceeds `inactivity_threshold`. Tickets are
    mutated in place; the ones closed by this call are returned.
    """
    now = now or datetime.now()
    closed = []
    for ticket in tickets:
        if ticket.status != "open":
            continue
        if now - ticket.last_customer_reply_at >= inactivity_threshold:
            ticket.status = "closed"
            ticket.closed_by = AUTO_CLOSE_LABEL
            closed.append(ticket)
    return closed


if __name__ == "__main__":
    from tickets import load_sample_tickets

    tickets = load_sample_tickets()
    closed = close_inactive_tickets(tickets)

    print(f"Closed {len(closed)} of {len(tickets)} tickets due to 24h inactivity:\n")
    for ticket in closed:
        silence = datetime.now() - ticket.last_customer_reply_at
        print(f"  {ticket.id} ({ticket.customer}) - silent for {silence.days} days")
