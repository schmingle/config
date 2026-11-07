---
name: worktree-cleanup
description: Review stale local Git worktrees and chats, then perform only a user-confirmed cleanup. Use only when explicitly invoked.
disable-model-invocation: true
---

# Worktree cleanup

Inventory and propose a bounded cleanup on the current host. Never archive a chat or remove a
worktree without showing the exact action and target and receiving confirmation for that batch.
Read-only invocations stay read-only. The user's explicit scope or thresholds override defaults.

## Discover and classify

Use native Codex chat and worktree controls where available, plus read-only Git and filesystem
inspection. Default to the current project and its local repository; honor a broader or narrower
scope explicitly requested by the user. State which repositories and chat sources were actually
inspected, including pagination or access gaps. Do not assume one repository's Git worktree list
contains all repositories, or that a missing attachment means no chat exists.

Use the current time and the user's timezone for cutoffs. The defaults are:

- **Chats:** consider non-pinned chats with no message activity for over 28 days for archiving.
  Exclude this chat, work in progress, and chats needed by active automations. Verify the latest
  message activity and the chat's current state; a filesystem timestamp is not message activity.
- **Worktrees:** consider checkouts over 14 days old for cleanup only when no non-archived chat
  or running process uses them and available evidence indicates no activity in the last 14 days.
  Inspect chat and checkout activity; a directory, index, or HEAD timestamp alone is not proof
  of last use. If age, use, ownership, or chat-association coverage cannot be established,
  report the checkout as uncertain rather than selecting it for removal.
- **Large-worktree review:** separately list checkouts over 14 days old and larger than 500 MB
  that have a non-archived chat attached, regardless of that chat's age. Show the chat, its latest
  message time and status when available, and useful size and activity evidence. These are review
  items, not removal candidates unless the user explicitly selects them and their use is resolved.

For each proposed worktree, inspect the registered path, lock state, tracked and untracked changes,
ignored files, commit/branch reachability, chat associations, and current process use. Preserve
branches and commits, including otherwise-unreferenced detached commits; do not infer that a
commit is safely preserved merely because the checkout is clean. Respect managed-worktree
ownership and native protections. Never remove the current checkout, an active or pinned chat's
checkout, or another checkout whose safety is unclear. Existing explicit user decisions about
archived chats and disposable local files apply within their stated scope, but still disclose the
contents and exact removal in the preview.

Rank cleanup and review candidates largest first. Report apparent or allocated size accurately;
shared files and snapshots can make actual recoverable space differ. Do not count unrelated
`/tmp` files, caches, or test evidence as worktrees or delete them under this skill.

## Preview and confirm

Present separate lists for (1) chats to archive, (2) exact worktree paths to remove, (3) large
worktrees with non-archived chats for review, and (4) skipped or uncertain items and why. Include
chat names and latest activity, worktree age evidence, size, changes and ignored files to be
discarded, commit preservation, and any impact on restoring archived chats. Do not expose secrets.

If archiving a listed chat would make its worktree eligible, explicitly include that resulting
worktree action and its consequences in the same preview or leave it for a later invocation. Do
not expand an approved batch after confirmation. Obtain explicit confirmation of the exact actions
and targets before mutation; a skill invocation or an automatic tool approval alone is not that
confirmation. If the user changes the selection or the state materially changes, show the revised
batch and confirm again.

## Execute and verify

Recheck each approved target's current chat status, process use, Git state, commit preservation,
and ownership immediately before acting. Skip changed or uncertain targets and report why; do
not use force to discard newly discovered work without a revised preview and confirmation.

Archive approved chats with the native chat control. For an eligible managed worktree, use the
native worktree archive control where supported; its snapshot does not preserve ignored files.
Respect primary, shared, protected, and other native refusal conditions without bypassing them
through Git. For a reviewed unmanaged Git worktree, use `git worktree remove` on the exact path;
only use force when the preview explicitly identified the changes to be discarded and the user
confirmed that exact removal. Never delete a worktree with a blanket `rm -rf`.

Verify each outcome, remaining Git registrations and preserved references. Measure free space
before and after and report the observed change, noting concurrent disk activity when applicable.
List completed, skipped, and failed actions once each; do not retry an uncertain mutation blindly.
