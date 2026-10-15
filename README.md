# Development configuration

Reusable development settings, agent definitions, and skills. This repository is
public; follow [AGENTS.md](AGENTS.md) before adding or publishing content.

- [Agents](.codex/agents/): role definitions, shared instructions, and review helpers.
- [Skills](.codex/skills/): custom skills and supporting files.

The `.codex/` directory mirrors the corresponding directories in `~/.codex/`.
Instruction references use that default installation path; adapt them if your Codex
home differs. Symlink the installed `agents` and `skills` folders to these directories
to edit the same files from either location. Back up existing folders before linking.
Agent registration and other local settings are not included.

Codex-managed `.system` skills are excluded by `skills/.gitignore`; runtime state is
also excluded. The writer references
a private `~/.codex/writing/style-guide.md`; supply your own guide outside this repo.
This repository does not include writing samples, credentials, or session history.
