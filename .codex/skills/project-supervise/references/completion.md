# Project completion

Use this gate when proposing or assessing project closure, not on every heartbeat.
Completed tickets, ready PRs, passing suites and worker reports are inputs, not
proof that the project's outcome is complete.

1. **Reconcile the contract.** Map each approved goal and phase exit to concrete
   evidence. Preserve exclusions and required human acceptance; do not narrow the
   contract to fit delivery or add unrelated improvements as closure requirements.
2. **Inspect the combined result.** Identify the actual merged revision and any
   other state required by the contract. Trace the affected consumers, public
   interfaces, runtime/configuration paths and maintained instructions as relevant.
   An unmerged combined tree may expose gaps, but cannot prove merged completion.
3. **Try to disprove completion.** A non-author assessor must independently inspect
   source and outcome evidence for counterexamples to the criteria, rather than
   endorse the delivery summary. Use an authorized supervisor, oversight agent or
   reviewer; respect existing delegation and capacity limits. Bound the challenge
   to the approved outcome. For removals, check reachability and obsolete callable
   surfaces or operating instructions, not only names; legitimate history need not
   disappear. This assesses the whole outcome, not another review of every PR.
4. **Resolve relevant findings.** Classify each as removed and verified, retained
   with a concrete purpose and supporting authority, outside scope with rationale,
   or unresolved/unverified. Required in-scope gaps block closure. Workers fix
   authorized gaps under normal PR ownership; missing scope or protected changes
   need the exact human decision. Preserve findings until correction is verified.
5. **Verify and conclude.** Inspect merged corrections together and run or obtain
   focused checks for affected behavior/invariants. Reuse still-valid evidence;
   materially changed coverage needs revalidation, unrelated main movement does
   not restart the entire assessment. Record the assessed revision and limits.
   Close only when the criteria, independent challenge and required acceptance
   are satisfied. Otherwise name the gap, owner and next action. A concrete new
   contradiction reopens the assessment; speculative repeat audits do not.

Keep one concise closure record in the existing Linear evaluation ticket or
project record: outcome and criteria evidence; assessed revision; independent
assessor, challenge coverage and findings/disposition; remaining obligations and
why they do not block this contract. Link existing evidence rather than copying it.
Runtime/deployment/operational acceptance are required only where the approved
contract requires them; source evidence cannot substitute for required live proof.
No separate tracker, blanket human closure approval or new permanent reviewer is
required. The supervisor owns the closure decision and existing reporting cadence.

## Independent oversight

When a supervisor proposes or reports closure, independently apply the same gate
using the approved contract and primary evidence. Treat the supervisor's record
as a claim to test, not the answer. Form your own counterexample search and
inspect whether claimed fixes and consequential retention/exclusion decisions hold.
Do not merely request another audit or accept a second summary as verification.

Keep the claim unverified while required evidence is missing. Send concrete gaps
to the owning supervisor, preserving worker/queue ownership; verify consequential
corrections before accepting closure. If already closed, require reconciliation
and reopening where the approved criteria remain unmet. Preserve authority over
scope, production and human acceptance. One completed scoped challenge suffices
until a finding, consequential change or new evidence invalidates its coverage.
