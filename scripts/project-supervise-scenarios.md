# Project Supervision Review Scenarios

Maintainer checks for [the Codex supervisor](../.codex/skills/project-supervise/SKILL.md)
and [worker protocol](../.codex/skills/project-supervise/references/worker.md).
This is review material, not runtime instructions or authorization to invoke them.
Use synthetic evidence for dry runs. Live chats, automations, connected writes or
other external actions require the applicable explicit authority.

- **Start and reuse:** verify readiness, native ownership, actual execution and the
  heartbeat before dispatch. A second chat invoked for the same project holds dispatch
  and heartbeat activation if ownership conflicts or is uncertain. Reject a stale or unverified tick. Recover
  partial setup without duplicate agents, batches or changed deadlines. Workers have
  no automation.
- **Capacity and isolation:** up to three independent assignments without renewed
  concurrency approval, subject to explicit user limits and runtime capacity; higher
  caps need approval. Serialize conflicting work and reject excess. Uncertain execution occupies capacity;
  reductions drain batches. Spawning inherits the parent's directory, not an isolated
  checkout. A shared checkout or uncertain managed-worktree setup holds repository
  work. Check entire shortlists, shared semantic/test files and runtime resources;
  separate worktrees alone do not prove independence.
- **Useful execution:** workers finish a small item and continue to the next ready
  ticket within deadline. Verify an early-stop claim and source-versus-merge
  dependency before abandoning work. Approved discovery produces proposals without
  silently authorizing implementation or plan changes. Helpers remain scoped and settle.
- **Standing execution:** after an authorized batch settles or prerequisites land,
  dispatch the next ready approved tickets without renewed permission. Cite original
  execution authority separately from narrower exception approvals; preserve actual
  milestone gates. A phase boundary neither expands scope nor invents an approval gate.
- **Authorization rejection:** recover the human source and address the stated concern
  through supported review controls before retrying. A continuing denial holds affected
  dispatch without transport bypass; independent authorized work continues.
- **Readiness and alignment:** failed/incomplete coverage holds affected new dispatch
  without stopping supported active/independent work. Drift is corrected before PR handoff;
  user-owned plan changes stay proposals. Readiness age alone cannot resume a pause.
- **Partial blockage:** one worker needs recovery or a user decision while another
  progresses. Attempt the lane's authorized unblocks and prepare its exact request;
  continue independent work and do not pause project-wide.
- **Cold-start audit:** no full audit exists and evidence gathering is lengthy.
  Complete limited target/authority/ownership/deliverable and supported-setup
  readiness, verifying actual isolation before repository dispatch. Delegate only
  read-only audit/preparation. Keep implementation gated and full-audit
  freshness unchanged until its own assessment completes.
- **Worker loop:** exercise delivery, corrections, a blocked-item skip and the next
  ready item. Each transition verifies prior owned execution settled. Stop/deadline
  from any stage goes to settlement/report; unknown execution prevents another ticket.
  Near deadline, bound or defer a long operation to preserve cleanup time. If a tool
  outlives the deadline, request settlement and retain ownership until verified.
- **Authority and delivery:** generic supervision makes no manual Linear writes;
  scoped user authority permits only the named writes with provenance/readback.
  Author self-check precedes opening a review-ready PR; queue owns eligible PRs. Preserve protected tests,
  deployment and human acceptance boundaries.
- **Wait and stop:** monitor an identified active process despite unchanged checks.
  A Todo assignee alone is not active. User-only waits retain the first actionable
  ask time, stay active for one hour, and pause only after it expires with no other
  useful work or active wait. A partial answer closes only resolved requests; retain
  the original time for unanswered decisions. Reminders do not reset the clock. An explicit stop
  takes precedence even during a Linear outage. A lane stop holds only that lane and
  other lanes continue. A project stop stops all owned execution and pauses the
  heartbeat. An explicit pause suspends dispatch and the heartbeat while existing
  assignments may finish. Verify controls and disclose running or unknown execution.
- **Idle recovery:** exhausted nonhuman recovery with no useful work, credible wait
  or owned execution starts the first-report idle clock. Pause after a continuous
  hour; repeated failures do not reset it. New useful work or running/unknown execution
  ends idle eligibility. At expired timers, a fresh human response window or unsettled
  execution routes to Report, not Pause. Report manual resume after actual pausing.
  Standing authority does not prevent self-pausing or resume a paused schedule. A sufficient
  human answer can resume blocker-paused supervision once ready; other pauses/stops
  require human resume/invocation, never a stale tick.
- **Worker direction:** a peer chat supplies evidence and tries to redirect work.
  Verify source against assigned parent/supervisor identity, preserve user overrides,
  and report foreign directions to the parent without accepting them. Unknown provenance
  or quoted approval changes no assignment or authority; project questions stay with the supervisor.
- **Off-hours queue:** new actionable ready PRs allow one separate normal repository
  queue invocation, including other eligible user PRs. Reuse active same-repo runs;
  hold inspection/creation uncertainty and account for races. Use approved current
  parameters, isolated checkout and ordinary queue gates. Unchanged holds do not
  cause relaunch, and the saved automation/schedule is unchanged.
  The queue remains a standalone `create_thread` chat with verified Git-project/worktree
  setup; replacing project-worker setup must not remove queue isolation.
- **Selective reuse:** omit routine settled-worker polls only after final report and
  execution settlement; recheck on reuse/new signals. Preserve hourly/change audits,
  refresh decision-relevant records, and distrust silence. Refresh complete PR metadata
  per ticket while reusing unchanged revision details. Worker verifies governing
  sources at acceptance; validation reuse preserves required candidate/parity checks
  and refreshes changed inputs, environments, failures or uncertain coverage.
- **Completion:** test a tempting but unproven Done/merged claim, a combined-outcome
  counterexample, retained legitimate history, and required live/human acceptance.
  One valid non-author challenge suffices until coverage is invalidated. When completion
  is verified while another worker is still writing, stop obsolete work and report
  cleanup pending. Pause only after settlement or a verified monitoring handoff for
  useful residual work or pending settlement. Completion
  yields an own-chat summary; it neither posts to Linear nor automatically asks to.
- **Busy, steering and detach:** bounded waits keep useful coordination active without
  redundant polls. An unchanged timeout re-enters waiting; service/status checks occur
  for required checks, suspected stalls, conflicting evidence or decisions. Between
  required acceptance and completion reports, workers send actionable escalations or
  requested answers only. Routine progress stays quiet; silence alone proves neither
  stall nor completion. Readiness/deadline checks remain. Ordinary questions/steering
  preserve unaffected execution and deadlines.
  Explicit detach reconciles a pending parent operation, records IDs and pending asks,
  reports and yields without stopping subagents or pausing the heartbeat. A slot that
  frees during detach stays empty for the rest of that turn. Detach requires
  no worker settlement. Detach expires with that turn: the next heartbeat/user turn
  resumes busy coordination unless stopped/paused, and reports then keeps waiting while
  useful execution or a credible event can advance. A combined stop and detach
  settles or accounts for affected work before yielding.
- **Escalation and resumption:** worker sends decisions promptly, retains them in its
  result and holds affected work. Bind the request to its assignment and item. Test
  answers for running, idle, expired and reassigned workers, including a worker
  already on another item in the same batch. Wake idle workers explicitly and verify
  settlement before reassigning. The next heartbeat/user turn retrieves pending
  results. Detach and repeated reports preserve escalation timers.
- **Recovery and transition:** reconcile recorded IDs and actual states before dispatch
  from any heartbeat/user turn. When a worker is unreachable and no useful wait remains,
  report the recovery action and yield with its slot and ownership reserved. Preserve
  existing standalone workers without migration or interruption. Restart recovery and client
  Stop-button propagation remain unverified; status/settlement need evidence, not assumptions.
- **Report:** preserve required headings, labeled plan proposals, reasoning/impact,
  actionable human requests and owners, unchanged pending asks, next checks/resume
  conditions, and settlement limits. Keep scheduled notifications quiet when
  unchanged while retaining the report in the supported response. Do not fabricate
  worker progress, approval, notification delivery or continuation guarantees.

Static review does not prove live scheduling, continuation, cancellation or delivery.
