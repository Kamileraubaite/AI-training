#### Spec:

### WHY

Customer raises the same problem twice, which raises duplicate tickets - so we need a feature that merges these duplicate tickets so the same issue is resolved at once. 

### WHAT 

Create a merge function

The function initially takes two tickets, the first being the primary ticket and the second being the duplicate ticket which is then merged into the primary one. 

A merge is successful if the duplicate ticket status is "merged"
- If duplicate ticker is already "merged", leave both tickets
- if primary ticket is already "merged", leave both tickets

### CONTEXT

Files: tickets.py
Pattern: Follow the existing function structure in tickets.py and use a one-line docstring.
Settled: Ticket state stays in the existing ticket record.

### CONSTRAINTS

Do not delete either ticket.
Do not email or notify the customer.
Do not add new dependencies.
Do not create a new ticket during the merge.
Do not merge a ticket into itself.
Do not allow an already "Merged" ticket to be merged again.
Do not change the priority of the primary ticket.
A ticket with status "Merged" must not later be escalated by escalate_ticket.

### TASKS

1. Check whether two tickets can be merged

Touches: tickets.py
Before merging, check:
the primary and duplicate tickets are different;
the duplicate ticket is not already "Merged";
the primary ticket is not already "Merged".

Verify:
Ticket 2 can be merged into ticket 1 when both are active.
Ticket 1 cannot be merged into itself.
A ticket already marked "Merged" cannot be merged again.
A ticket cannot be merged into a primary ticket whose status is "Merged".
Failed merge attempts leave both tickets unchanged.

2. Apply the merge

Touches: tickets.py
When the merge is valid:
set the duplicate ticket status to "Merged";
store the primary ticket ID on the duplicate ticket;
leave the primary ticket active.

Verify:
Merging ticket 2 into ticket 1 sets ticket 2 status to "Merged".
Ticket 2 records that it was merged into ticket 1.
Ticket 1 remains active.
Ticket 1's priority and other existing fields remain unchanged.

3. Prevent merged tickets from being escalated

Touches: tickets.py
Update the existing escalation behaviour so a ticket with status "Merged" is ignored.

Verify:
A "Merged" ticket whose last_customer_reply_at was 5 days ago remains unchanged.
Its priority does not become "Urgent".
Existing non-merged tickets still follow the Round 2 escalation rules.

### DONE

Given two active tickets, ticket 1 and ticket 2, calling merge_ticket with ticket 1 as the primary and ticket 2 as the duplicate results in:

ticket 1 remaining active;
ticket 2 having status "Merged";
ticket 2 storing ticket 1 as its primary ticket;
ticket 2 no longer being eligible for escalation.

Invalid merge attempts make no changes to either ticket.