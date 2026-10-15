# Public configuration repository

This repository and its Git history are public. These rules apply to every file,
commit, generated artifact, and contribution, including work by delegated agents.

## What belongs here

Track reusable development configuration, agent definitions, skills, scripts, and
instructions. Development preferences, public developer identities, and public
technical references are allowed when relevant. Include only information necessary
to explain or use the configuration.

Development relevance alone does not make information safe to publish. Company,
customer, and third-party confidential information must remain outside this repo.

## Never include

- Credentials or authentication material: passwords, API keys, tokens, cookies,
  private keys, recovery codes, credential-bearing URLs, or secret environment values.
- Personal information unrelated to development: private correspondence, personal
  contact details, family information, financial records, health information,
  travel details, or calendar contents.
- Private source material: chat/session transcripts, memories, writing samples,
  meeting notes, customer data, internal tickets, private document contents, or
  proprietary code and operational details without explicit authorization to publish.
- Local runtime state: authentication stores, session databases, logs, caches,
  benchmark evidence bundles, backups, or generated exports containing private data.

Do not copy entire configuration directories or follow symlinks into private files.
Select and inspect individual files. A referenced private file is not permission to
copy its contents into this repository.

## Make configuration portable

Use environment variables, home-relative paths, and clearly labeled placeholders
instead of personal absolute paths, real account identifiers, or private service
addresses. Reference secrets by environment-variable name; never supply real values.
Keep local overrides and sensitive source material outside the repository, with
appropriate ignore rules for any local-only files. Ignoring a file does not protect
it if it is already tracked.

## Before staging, committing, or pushing

1. Inspect the exact files and complete diff, including new, hidden, generated,
   and binary files. Review staged content again before committing. Do not use
   blanket staging to import unreviewed files.
2. Check for credentials, personal information, private references, and sensitive
   information in comments, examples, filenames, and metadata. Use a secret scanner
   when available; a clean scan does not replace content review.
3. Verify that only the intended, reviewed files are included. When pushing existing
   local commits, inspect all outgoing commits, not only the final tree: deleting a
   secret in a later commit does not remove it from public history.
4. If information may be sensitive, omit or sanitize it. Ask the owner only when
   its inclusion is necessary and publication authority is unclear. Never print
   suspected secret values in reports or tool output; identify the file and location.

If a secret or private information is discovered in tracked content or history,
stop the affected commit/push and notify the owner with its location, without
repeating the value. If already published, flag the exposure immediately and
recommend credential revocation/rotation where applicable. Coordinate history
cleanup with the owner; do not rewrite shared history unilaterally.
