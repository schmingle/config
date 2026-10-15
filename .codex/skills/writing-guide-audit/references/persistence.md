# Local guide persistence

## Paths and Git boundary

The default directory is the absolute resolved `<codex-home>/writing`; the canonical file is `style-guide.md`. Keep one private local Git repository there. For an explicit alternate guide path, inspect its directory and agree on versioning before using an existing shared repository; never include personal samples in a public or unrelated project automatically.

Use absolute verified paths or tool `workdir` parameters. Quote shell paths correctly. Do not use `~` inside quoted paths, hardcode a username, or repurpose `HOME` or `CODEX_HOME`.

Before writes, inspect directory contents, Git root, status, and existing configuration. If the exact directory is not a Git root and has no `.git`, `git init --initial-branch=main <absolute-guide-directory>` creates the dedicated repository. If `.git` already exists but resolves elsewhere, inspect rather than replacing it. Creating this repository is part of the requested local commit workflow, not permission to push or to alter an enclosing repository.

Use the user's existing Git identity. If no usable identity exists, prepare the approved files and ask for the missing author name/email; do not invent an identity or change global Git configuration.

## Working files

- `style-guide.md`: the canonical, committed guide.
- `style-guide.review.md`: proposed next version, pending final approval.

Do not create or consume persistent audit progress. Keep the baseline hash and current feedback in the conversation. Each invocation starts fresh; an existing review draft does not imply unfinished work.

Keep the review draft local and ignored with an exact `style-guide.review.md` entry in this repository's `.git/info/exclude`, preserving existing entries. Do not stage it in the guide commit. It is proposed content, not a workflow checkpoint.

## Safe finalization

1. Before presenting final review, put an actual ISO 8601 audit timestamp and the coverage/decision into the review draft. Retain last complete audit for a partial run. If no style changed, explicitly say so in the audit record. Approval covers this exact draft.
2. After approval, confirm canonical SHA-256 equals the recorded baseline (or remains absent for first creation), and verify no unrelated staged or unstaged work appeared. If the baseline differs, preserve current and proposed content and resolve the conflict before replacing anything.
3. Apply the approved content to the canonical file using the provided editing tool; ensure the metadata timestamp makes an otherwise unchanged audit a real content change. Run `touch` on that exact canonical path as requested. `touch` may need filesystem permission; do not bypass the sandbox.
4. Inspect `git diff --check` and the scoped diff (or inspect the whole file on first creation). Confirm source labels and reviewed-group coverage. Use `git add -- <guide-filename>` followed by `git diff --cached --name-only` to verify the index contains only the intended guide. If unexpected staged files exist, stop and preserve them rather than committing them.
5. Commit locally with a concise message such as `Audit writing guide: refine Slack proposals` or `Audit writing guide: no style changes`. Do not use `--amend`, force operations, blanket `git add .`, or automatically push. Verify `git show --stat HEAD`, the committed file's contents, and clean scoped status.
6. If commit fails after the approved file was written, preserve the working file and retry only the failed finalization step after resolving the cause. Report approval and saved-file status separately from commit status. Do not restart the entire audit.

When the user ends the audit, stop without writing pause, closure, or resumption state. Do not touch or claim finalization of the canonical guide without approval. Future invocations start fresh from the guide and current request.
