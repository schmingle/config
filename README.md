# Development configuration

Reusable development settings, agent definitions, and skills. This repository is
public; follow [AGENTS.md](AGENTS.md) before adding or publishing content.

- [Agents](.codex/agents/): role definitions, shared instructions, and review helpers.
- [Skills](.codex/skills/): custom skills and supporting files.

The `.codex/` directory mirrors the corresponding directories in `~/.codex/`.
Instruction references use that default installation path; adapt them if your Codex
home differs. Symlink the installed `agents` and `skills` folders to these directories
to edit the same files from either location. Back up existing folders before linking.
Other local Codex settings are not included.

Codex-managed `.system` skills are excluded by `skills/.gitignore`; runtime state is
also excluded. The writer references
a private `~/.codex/writing/style-guide.md`; supply your own guide outside this repo.
This repository does not include writing samples, credentials, or session history.

## Validate changes

Use Python 3.12 or newer:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_config.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .codex/agents/scripts -p 'test_*.py'
```

GitHub Actions runs the same checks on pushes and pull requests. Tests use local
fixtures and a fake CLI; they do not invoke a paid model or connected service.
The checks flag common configuration mistakes and credential formats; review the
full diff for privacy and correctness before committing or pushing.
