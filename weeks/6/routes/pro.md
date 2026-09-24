# Week 6 on the pro route

**No helpers, one real constraint.** Your finished piece is *harder and made public*: the
constraint is a **zero-downtime rollback**. Run the old image and the new one side by side on two
ports, move traffic between them, and prove with a smoke test every 30 seconds that no run failed.
Plus an incident report for the break as if it had reached users.
