# Challenge: rank it yourself, then check the machine

**40 minutes. Laptops closed for the first half.**

You have built something that turns text into numbers and ranks
documents by how close those numbers sit together. Before you trust it, find out how well it
actually matches your own judgement.

---

## Part One: predict (laptops closed, 15 minutes)

Below are the eight documents already sitting in your index. Read them again, properly this
time, not skimming for code.

For each of the three questions, write down which document you think is the **best** match,
and one sentence on **why**. Do this before looking at anyone else's answers.

**The documents:**

| id | title |
|---|---|
| doc-001 | Harding & Voss - Market Position Note |
| doc-002 | Marchetti Ruiz - Compensation Review |
| doc-003 | Okonkwo Bell - Strategy Briefing |
| doc-004 | Sandoval Kerr - Risk and Compliance Summary |
| doc-005 | Lindqvist Partners - APAC Expansion Review |
| doc-006 | UK Market Commentary - Lateral Hiring |
| doc-007 | Jurisdiction Note - EU Practice Rights |
| doc-008 | Benchmarking Methodology |

*(Full text is in `documents.py` - go and actually read it again rather than working from
the titles alone.)*

**Question 1**
> Which firm works in energy and infrastructure?

My prediction: Doc 003 - "Okonkwo Bell — Strategy Briefing"
Why: The firm has built a reputation in energy and infrastructure work.

**Question 2**
> Which firms operate in the United States?

My prediction: Doc 002 - "Marchetti Ruiz — Compensation Review"
Why: The firm's US practice drives the majority of profitability.

**Question 3**
> Has any firm had a regulatory or compliance problem recently?

My prediction: Doc 004 - "Sandoval Kerr — Risk and Compliance Summary" 
Why: The firm's matter intake process now requires sign-off from a dedicated risk partner for any engagement above a defined threshold. - this suggests the company had some compliance problems because theyve now implimented a regulation. 

---

## Part Two: discuss (10 minutes)

Compare your three answers with the person next to you before opening a laptop. Where did
you agree? Where did you disagree, and why?

---

# PAUSE
### We will come back to this after we implement our endpoint




## Part Three: verify (10 minutes)

Laptops open. Run each of your three questions through the real endpoint:

```bash
curl -X POST http://127.0.0.1:8000/knowledge/search -H "Content-Type: application/json" \
  -d '{"question":"YOUR QUESTION HERE"}'
```

For each one, write down what the machine actually returned as its top result, and its
score.

**Question 1 - machine's top result:** Doc 003
**Did it match your prediction?** Yes

**Question 2 - machine's top result:** Doc 001 
**Did it match your prediction?** No

**Question 3 - machine's top result:** Doc 004
**Did it match your prediction?** Yes

---

## If you finish early

Try these two, same process, no need to write it up formally, just notice what happens:

> What is matter LP-2291?

> What is the position on fixed-share partners?

---

## Keep this sheet

You will want it again this afternoon.
