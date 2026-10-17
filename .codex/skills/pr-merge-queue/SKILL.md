---
name: pr-merge-queue
description: Coordinate bounded repairs, independent reviews, and safe merges of the authenticated user's open PRs after explicit invocation. Configuration work does not run the queue.
disable-model-invocation: true
---

# PR merge queue

Run only after explicit invocation, including an approved scheduled prompt that invokes this skill. Editing its configuration does not invoke it. Use direct `gh`/git commands and native task/agent tools; no custom queue scripts, registries, persistent queue state, or locks.

## Lightweight discovery

Perform initial discovery directly in this coordinator; do not delegate or load agent definitions before candidates remain.

1. Validate parameters first: `count=0` by default (nonnegative integer verified merge limit), `timeout=50` minutes, and `timeout_idle=10` minutes (both finite positive numbers). Reject unknown or invalid parameters before discovery or writes. Record invocation start with the clock tool or `date`; discovery counts toward the deadline.
2. In the same tool-run shell, locate `gh`, check its version/authentication, verify the intended authenticated account, and resolve the explicitly intended `OWNER/REPO` from the invocation or its approved project context. Verify that repository with `gh repo view OWNER/REPO --json nameWithOwner`; use `--repo OWNER/REPO` on all PR commands. Missing/ambiguous account or repository, CLI/auth/network failure, malformed output, or incomplete discovery is an error: stop and report the exact blocker, never classify it as an empty queue. Follow applicable sandbox escalation guidance for a denied harmless check.
3. Discover only that account's open PRs with `gh pr list --repo OWNER/REPO --author @me --state open --limit 100 --json number,url,isDraft,labels`. Ensure completeness: if the result count reaches the requested limit, increase it and repeat until fewer results are returned, or use complete pagination through `gh api`. A failed page, unverified truncation, or deadline before completeness is a discovery error, even if the partial result has no candidates. Filter drafts and PRs labeled `noautomerge` locally. Retain only candidate metadata and aggregate discovery/exclusion counts; do not fetch checks, reviews, discussions, diffs, or history yet.
4. If successful complete discovery leaves zero candidates, exit immediately. For scheduled runs, stay quiet: no routine progress updates, full report, or notification. A manual run may return one line saying there are no candidates. Do not read workflow references, agent definitions, memory, task history, or other queue context, and do not spawn agents or perform writes on this path.
5. Only when candidates remain, read [the full queue workflow](references/queue.md) and the six `~/.codex/agents/pr-{green,resolve,update,risk,review,review-high}.toml` definitions once, then follow them. Candidate discovery is not merge eligibility: all review, risk, finding, ownership, dependency, current-head, and GitHub merge gates still apply. Recheck open/non-draft/`noautomerge` status before every write.

An invocation authorizes the workflow's scoped repairs, finding dispositions, risk assessments, and independent COMMENT reviews. `count=0` never authorizes a merge; a positive count also authorizes eligible squash merges up to that verified limit. Never enable auto-merge, bypass protections, deploy, or force-push.
