# 1. Kickoff

**A worked example.** The meeting, quotes and figures below are invented. See `README.md`.

Monday 7 September 2026, 90 minutes, at UnderCover's office.

## Why this step

Before any problem is explored, three things must be clear: who pays for the work and signs it off (the sponsor), who owns the result once it is live (the owner), and how decisions get made along the way. Without a sponsor, the work has no budget and no one to say yes at each gate. Without an owner, nobody runs it after we leave.

The kickoff is also the first test of the "agent for X" trap. If the client arrives asking for an agent, the first job is to find the business problem underneath, and whether it can be measured.

## Who was there

- Chief Operating Officer: the sponsor
- Head of Claims Operations: the owner
- Head of IT
- Data Governance Lead
- XPLORATECH: the forward deployed engineer

## What we asked

1. What prompted this work, and why now?
2. What does the problem cost you today, and how do you know?
3. If this works, what is different in a year? How would you measure it?
4. Who owns claims, and who would own an automated system?
5. Who needs to approve the scope, the budget, and anything that goes live?
6. Who else must be involved: security, legal, data, the people doing the work?
7. What has been tried before?
8. What must never happen?

## What we heard

The sponsor opened by asking for "an AI agent for claims". Asked what it should change, the answer was about the queue:

> "Every summer the queue gets away from us. Customers wait weeks for a simple baggage claim, and we either hire temps who don't know the wording or we ask the team to work late. I want claims decided faster without decisions getting worse."

The owner added that the three handlers spend most of their time on routine claims that are clearly covered or clearly excluded, and too little on the ones that need judgement.

Nothing had been tried before beyond a spreadsheet of standard payouts. The head of IT confirmed that claims, policies and customers each live in a separate system, and that all three can export records.

On what must never happen, three answers:

- A payment over the handler sign-off limit goes out without a handler.
- A customer is declined who should have been paid.
- Customer data leaves UnderCover's systems or is used for anything but the customer's own claim.

## Governance agreed

| Level | Who | How often | Decides |
|---|---|---|---|
| Project committee | Sponsor, owner, head of IT, data governance lead, XPLORATECH | Monthly, and at each gate | Scope, risk, budget and releases |
| Working group | Owner, a senior claims handler, an IT engineer, XPLORATECH | Weekly | What to build next, how it is evaluated, and what it found |

The firm's leadership group sets the policy and risk appetite above both. It was not involved in discovery.

The sponsor signs off at the end of each phase. For discovery, that sign-off is the scope and the budget for R&D.

## What it produced

- The sponsor and the owner, named in `docs/DISCOVERY.md`.
- The governance above.
- A first statement of the problem: claims decisions are slow at peak, and handlers' time goes on routine claims.
- Three "never" rules, carried into `08_autonomy_and_risk.md`.
- The plan for the next three weeks: interviews, a process map, data requests, a baseline, and the evals.

## Actions

| Action | Owner | By |
|---|---|---|
| Book interviews with each handler and with finance | Head of Claims Operations | 9 September |
| Arrange two days sitting with the handlers | Head of Claims Operations | 14 September |
| Send the first data request | XPLORATECH | 14 September |
| Confirm how records can be exported, and where data may be stored | Head of IT | 18 September |
| Share the data catalog and any data owners' list | Data Governance Lead | 18 September |
