# Atomic Stack Merges

Use only inside an authorized queue run after candidate admission. This optimization
does not invoke the queue, create native stacks, change merge policy, or skip CI.
Reconcile outstanding asynchronous operations identified in current chat/PR
evidence or supplied automation memory before affecting those members; a prior
run ending does not establish that its GitHub operation ended.

## Identify the exact group

Use scoped `gh api` reads on the verified host/repository to inspect PR `stack`
metadata and fully enumerate its native stack through GitHub's documented Stacks
API. Confirm support on the actual host; missing/ambiguous metadata or unsupported
APIs mean no atomic optimization, not permission to infer a stack from branch names.
Read the current [stack API documentation][stack-api] for endpoint/schema details;
do not guess endpoint names or undocumented payload fields.

Selecting a native stack member includes **every open downstack PR through that
member**. Select only a contiguous prefix starting at the lowest unmerged member,
rooted in verified `DEFAULT_BRANCH`, with linear same-repository ancestry. Record
the ordered PRs, author/admission, stack identity/order, each head and actual base,
trunk SHA, and the selected top head. Prove lower heads are ancestors of that top.
Resolve external prerequisites normally; branching dependency graphs are not one
atomic linear stack.

## Qualify every included PR and the combined result

- Every included PR must be admitted under this run's authenticated-author,
  open/non-draft/non-`noautomerge` filters. Never include an excluded, unreviewed,
  stopped, or otherwise unauthorized ancestor merely because GitHub includes it.
- Apply the queue's risk ceiling, scoped exceptions, review/disposition, discussion,
  ownership, and GitHub protection gates independently to every member. Accepted
  source reviews must also cover the combined integration against the current
  trunk; a top PR's green checks or LGTM alone do not cover lower PRs. Reuse valid
  coverage and obtain only missing integration review through the existing roles.
- Do not invent a combined risk rating or weaken individual assessments. Hold a
  combination whose interaction introduces material exposure not covered by the
  accepted assessments/reviews; follow the queue's existing reassessment authority.
- GitHub must permit the group under trunk protections. Native stack support does
  not waive required checks or approvals. Do not alter checks, branch rules, or
  local/CI execution policy to make it eligible.
- Reserve one remaining merge-count unit per included PR, and enough time for
  bounded polling/readback before settlement. `count=0` prohibits submissions.
  Shrink to an eligible bottom prefix when count or gates exclude upper members;
  do not wait unnecessarily for a larger group.
- Preserve a separate squash commit and required deduplicated co-author trailers
  for each PR. Confirm the supported API/repository-generated message behavior
  preserves each member's trailers before using a multi-PR operation. A single
  `commit_message` field is not proof of per-member message control. If preservation
  cannot be established, use bottom-only serial merging with an explicit supported
  squash message instead; never change merge method or rewrite history as a shortcut.

## Submit and reconcile

Immediately before submitting, refresh the complete group and all normal write
gates, including head/base/trunk, membership/order, exclusions, holds, and writer
ownership. Include upper stack branches that GitHub may automatically rebase or
retarget, even when those PRs are outside the selected group or excluded from
admission; active or ambiguous writers there hold the operation. Invalidate changed
evidence before proceeding. The API exposes a selected-head SHA guard, not a
documented compare-and-swap for every member or the
trunk; do not claim a stronger guarantee. Any unresolved source/membership race
holds the group.

Use scoped `gh api` with the [documented asynchronous merge API][merge-api]:
`PUT /repos/{owner}/{repo}/pulls/{selected_top}/merge-async`, supplying the pinned
top `sha`, `merge_method: squash`, `merge_action: direct_merge`, and
`bypass_rules: false`. Use a temporary JSON request file with `--input` when
supplying commit text. This policy does not authorize enqueueing; if repository
rules require GitHub's merge queue, report the block rather than bypassing it or
switching to `default`/`merge_queue`.

Record the response UUID and options. `202` means accepted, not merged; protections
are evaluated during background execution. Poll
`GET /repos/{owner}/{repo}/pulls/{selected_top}/merge-async/{uuid}` within the
original run limits. Reconcile an existing-request `409` against its options and
actual PR state instead of resubmitting. `enqueued` is not merged and must be
reported as an unexpected outstanding action under this direct-only policy.

On `merged`, verify **every** included PR's merged state, landing commits and
ancestry on `DEFAULT_BRANCH`, and per-PR trailers. Count each confirmed distinct
landing; missing trailers are an attribution failure that still consumes the PR's
merge-count unit, not permission to replace it with another merge. Distinguish
this run's operation from concurrent merges. Unexpected or partial readback is
uncertainty, not permission to fill in missing merges.
Afterward refresh the remaining stack: GitHub may rebase/retarget its members.

On a definite failed/rejected request, refresh the reason and affected state;
retry only after a relevant change. Use the ordinary serial reconciliation path
where safe; native bottom-only merges still require this asynchronous API. Never
silently dissolve a native stack or fall back to the legacy endpoint for it.

A timeout, network error, expired/unknown UUID, or inconsistent readback leaves an
unresolved operation until verified otherwise. Do not submit overlapping merges,
retry, rebase, retarget, or dispatch writers on affected members while it may still
execute. Poll only within the remaining budget, then report the UUID, members and
known state in settlement and supplied automation memory for the next run. Do not
claim that ending this chat cancelled GitHub's operation. Other independent work
may continue only within the remaining count capacity and original limits.

[stack-api]: https://docs.github.com/en/pull-requests/reference/stacked-pull-requests-apis-and-webhooks
[merge-api]: https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously
