#!/usr/bin/env python3
"""Validate public agent/skill configuration without local Codex state or services."""
import ast
from pathlib import Path
import re
import subprocess
import tomllib

import yaml

ROOT = Path(__file__).resolve().parents[1]
EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'}
SECRET = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|'
                    r'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}|AKIA[A-Z0-9]{16}|'
                    r'xox[baprs]-[A-Za-z0-9-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
PRIVATE_ROOTS = {'auth.json', 'config.toml', 'writing', 'sessions', 'memories', 'automations',
                 'worktrees', 'history.jsonl', 'cache', 'backups', 'logs'}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def yaml_mapping(text, label):
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError:
        raise ValueError(label + ': invalid YAML; source content omitted') from None
    check(isinstance(value, dict), label + ': expected a YAML mapping')
    return value


def validate():
    # Git supplies the actual public payload, including new files but excluding .system.
    paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others',
                                     '--exclude-standard', '-z']).decode().split('\0')
    agents = {}
    skill_count = 0
    for name in sorted(set(paths) - {''}):
        path = ROOT / name
        if not path.exists():
            continue  # A tracked file scheduled for deletion.
        check(not path.is_symlink(), name + ': inspect symlinks before publishing')
        parts = Path(name).parts
        if parts[0] == '.codex' and len(parts) > 1:
            check(parts[1] not in PRIVATE_ROOTS, name + ': private/local-only Codex content')
            check('.system' not in parts, name + ': bundled skills must remain untracked')
        try:
            text = path.read_text()
        except UnicodeError:
            raise ValueError(name + ': binary content needs explicit review') from None
        check(not SECRET.search(text), name + ': possible credential; value omitted')
        check(not re.search(r'/' r'Users' r'/[^/\s]+/', text), name + ': replace personal absolute paths')
        check(all(line.rstrip() == line for line in text.splitlines()), name + ': trailing whitespace')
        if path.suffix == '.py':
            ast.parse(text, filename=name)
        if path.suffix == '.toml':
            value = tomllib.loads(text)
            if path.parent == ROOT / '.codex/agents':
                check({'name', 'description', 'developer_instructions'} <= value.keys(),
                      name + ': missing required agent fields')
                check(value['name'] == path.stem and value['name'] not in agents,
                      name + ': duplicate or mismatched agent name')
                check(value.get('model_reasoning_effort') in EFFORTS, name + ': invalid effort')
                check(bool(value.get('model')), name + ': missing model')
                agents[value['name']] = value
        if path.suffix in ('.yaml', '.yml'):
            yaml_mapping(text, name)
        if path.name == 'SKILL.md':
            check(text.startswith('---\n'), name + ': missing frontmatter')
            front = yaml_mapping(text.split('---', 2)[1], name)
            check(front.get('name') == path.parent.name and bool(front.get('description')),
                  name + ': missing or mismatched skill identity')
            if front.get('disable-model-invocation') is True:
                metadata = yaml_mapping((path.parent / 'agents/openai.yaml').read_text(), name)
                check(metadata.get('policy', {}).get('allow_implicit_invocation') is False,
                      name + ': explicit-only skill needs matching native invocation policy')
            skill_count += 1
        if path.suffix in ('.md', '.toml'):
            for reference in re.findall(r"~/.codex/(?:agents|skills)/[^\s`\x27\x22]+", text):
                reference = reference.rstrip('.,;)')
                group = re.search(r'\{([^{}]+)\}', reference)
                references = ([reference[:group.start()] + choice + reference[group.end():]
                               for choice in group[1].split(',')] if group else [reference])
                for candidate in references:
                    check((ROOT / '.codex' / candidate.removeprefix('~/.codex/')).exists(),
                          name + ': broken installed reference: ' + candidate)
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                if target == 'URL' or target.startswith(('#', '~/', 'https://', 'http://', 'mailto:')):
                    continue  # Placeholder, fragment, or external reference.
                destination = (path.parent / target.split('#')[0]).resolve()
                check(destination.exists(), name + ': broken local link: ' + target)
    reviewer = agents['pr-review']
    match = re.fullmatch(r'gpt-(.+)-(sol|astra|luna)', reviewer['model'])
    check(match is not None, 'Default reviewer model needs an explicit attribution check')
    attribution = f"Reviewed by GPT-{match[1]} {match[2].title()} {reviewer['model_reasoning_effort']}."
    check(attribution in reviewer['developer_instructions'], 'Default reviewer attribution differs from settings')
    profile_path = ROOT / '.codex/agents/scripts/claude-review.toml'
    profile = tomllib.loads(profile_path.read_text())
    check('-'.join(profile['label'].lower().split()).replace('.', '-') == profile['model'],
          'Claude display name differs from model identifier')
    check(profile['effort'] in {'low', 'medium', 'high', 'xhigh', 'max'},
          'Claude profile has invalid CLI effort')
    check(isinstance(profile['allowed_tools'], list) and 'Bash' in profile['allowed_tools']
          and all(isinstance(tool, str) for tool in profile['allowed_tools']),
          'Claude profile needs a tool list with trusted shell access')
    check('claude-review.toml' in agents['pr-review-high']['developer_instructions'],
          'Escalated reviewer must reference its execution profile')
    print(f'Validated {len(agents)} agents, {skill_count} skills, YAML/TOML, Python, local links, and public-file checks.')


if __name__ == '__main__':
    try:
        validate()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error)) from None
