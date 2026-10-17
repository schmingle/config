# Explicit isolated pilot

Run only when the human explicitly requests a pilot. Use an isolated test project, test tasks, and a disposable checkout with permitted effects; agree on any connected-service writes first. Configuration review does not authorize creating live tasks, automations, tickets, or project updates. Shorten intervals and batches only for this test, and record their actual values.

Exercise these scenarios against observable task/automation records and resulting artifacts:

1. **New and resumed invocation:** Kickoff creates one supervisor heartbeat, starts the first cycle immediately, and creates one standalone worker. Reinvoking in the same task, including after a long gap, recovers the existing pair and schedule. A second supervisor cannot silently create a competitor.
2. **Continuation and delivery:** Give the worker multiple safe steps, an empty authorized queue, and a blocker. Observe whether it actually continues, reports early waiting, delivers an immediate question/final report that wakes the supervisor under existing authority, receives mid-run steering, and leaves the supervisor heartbeat active while blocked. A prompt promising continuation is insufficient evidence.
3. **Corrections and phase gates:** Introduce active-batch and idle-worker discrepancies; confirm nudges retain the active deadline while an idle correction gets a full fresh batch after settlement. Require observed correction evidence. A worker claim and Done ticket cannot clear it or unlock dependent work; independent preparation can proceed.
4. **Deadline and settlement:** Include an owned child agent or command crossing the test deadline. Verify cleanup/status reporting, no deadline reset on a nudge, and no new overlapping batch while owned work remains active or unknown. Report unsupported stop controls honestly.
5. **Recovery and user stop:** Simulate a lost creation response and recover through readback without duplicates. Stop supervision while work is active; verify the heartbeat pauses, settlement is checked separately, and a queued scheduled invocation cannot restart either. An explicit human resume reconciles the existing pair, reactivates the same heartbeat with readback, and persists the resume.
6. **Full acceptance:** Verify the combined artifacts against all test-project criteria and independent review. Only after worker/child/supervisor-reviewer/write settlement may completion publish its final update and pause the heartbeat with readback. Reinvoke on unchanged completed work and confirm it creates nothing.

Report observed passes, failures, untested scenarios, and host limitations separately. Pause test automations when the pilot is explicitly stopped or verified complete; never present static checks as a successful live pilot.
