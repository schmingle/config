#!/usr/bin/env python3
"""Validate public agent/skill configuration without local Codex state or services."""
import ast
from pathlib import Path
import re
import subprocess
import tomllib

import yaml

from check_privacy import inspect_blob
from agent_launcher import ROLE_CAPABILITIES, capabilities

ROOT = Path(__file__).resolve().parents[1]
EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'}
EXECUTION_PROSE = re.compile(r'(?i)\b(?:gpt-\d[\w.-]*|claude-(?:opus|sonnet|haiku)[\w.-]*|Sol|Astra|Luna|Terra|Opus|Sonnet|Haiku)\b|\b(?:low|medium|high|xhigh|max|ultra)\s+effort\b')



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


def validate_capabilities(agents):
    check(set(agents) == set(ROLE_CAPABILITIES), 'Launcher capabilities must cover exactly the public roles')
    for role in agents:
        limits = capabilities(role)
        check(set(limits) == {'provider', 'default_sandbox', 'source_writes', 'approval_policy',
                             'approvals_reviewer', 'external_actions', 'requires_network_reads'},
              role + ': invalid capability fields')
        check(limits['provider'] in {'codex', 'claude'}, role + ': invalid executor provider')
        check(isinstance(limits['source_writes'], bool), role + ': source_writes must be boolean')
        check(isinstance(limits['requires_network_reads'], bool), role + ': requires_network_reads must be boolean')
        check(limits['default_sandbox'] in {'read-only', 'workspace-write'}, role + ': invalid default sandbox')
        check(limits['source_writes'] or limits['default_sandbox'] == 'read-only',
              role + ': analysis roles must default to read-only')
        check(limits['external_actions'] in {'none', 'task-authorized', 'comment-review', 'ci-rerun'},
              role + ': invalid external action ceiling')
        if limits['provider'] == 'codex':
            needs_approval = (limits['requires_network_reads'] or limits['source_writes']
                              or limits['external_actions'] != 'none')
            expected = 'on-request' if needs_approval else 'never'
            check(limits['approval_policy'] == expected, role + ': missing or excessive approval path')
            check(limits['approvals_reviewer'] == ('auto_review' if expected == 'on-request' else 'user'),
                  role + ': invalid approval reviewer')
        else:
            check(limits['approval_policy'] == limits['approvals_reviewer'] == 'provider-native',
                  role + ': preserve native provider permissions')
    for role in ('pr-risk', 'pr-review-high', 'port-to-claude'):
        check(not capabilities(role)['source_writes'] and capabilities(role)['external_actions'] == 'none',
              role + ': generic analysis must not write or publish')
    check(capabilities('pr-risk')['requires_network_reads'], 'pr-risk: live evidence requires network reads')
    for role, action in (('pr-review', 'comment-review'), ('pr-green', 'ci-rerun')):
        check(not capabilities(role)['source_writes'] and capabilities(role)['external_actions'] == action,
              role + ': preserve read-only source and narrowly scoped external action ceiling')


def validate():
    # Git supplies the actual public payload, including new files but excluding .system.
    paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others',
                                     '--exclude-standard', '-z']).decode().split('\0')
    agents = {}
    claude_agents = {}
    skills = {}
    skill_count = 0
    for name in sorted(set(paths) - {''}):
        path = ROOT / name
        check(not path.is_symlink(), name + ': inspect symlinks before publishing')
        if not path.exists():
            continue  # A tracked file scheduled for deletion.
        payload = path.read_bytes()
        inspect_blob(name, '100644', payload)
        text = payload.decode('utf-8')
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
                check(not EXECUTION_PROSE.search(value['description']),
                      name + ': keep routing descriptions free of model/effort settings')
                if value['name'] != 'pr-review-high':
                    check(not EXECUTION_PROSE.search(value['developer_instructions']),
                          name + ': native execution values belong only in execution fields')
                check('~/.codex/agents/context.md' in value['developer_instructions'],
                      name + ': missing shared context-selection policy')
                agents[value['name']] = value
        if path.suffix in ('.yaml', '.yml'):
            yaml_mapping(text, name)
        if path.parent == ROOT / '.claude/agents' and path.suffix == '.md':
            check(text.startswith('---\n'), name + ': missing agent frontmatter')
            front = yaml_mapping(text.split('---', 2)[1], name)
            check(front.get('name') == path.stem and bool(front.get('description')),
                  name + ': missing or mismatched agent identity')
            check(bool(front.get('model')) and front.get('effort') in EFFORTS,
                  name + ': missing model or invalid effort')
            check(not EXECUTION_PROSE.search(front['description']),
                  name + ': keep routing descriptions free of model/effort settings')
            claude_agents[path.stem] = front
        if path.name == 'SKILL.md':
            check(text.startswith('---\n'), name + ': missing frontmatter')
            front = yaml_mapping(text.split('---', 2)[1], name)
            check(front.get('name') == path.parent.name and bool(front.get('description')),
                  name + ': missing or mismatched skill identity')
            if front.get('disable-model-invocation') is True and name.startswith('.codex/'):
                metadata = yaml_mapping((path.parent / 'agents/openai.yaml').read_text(), name)
                check(metadata.get('policy', {}).get('allow_implicit_invocation') is False,
                      name + ': explicit-only skill needs matching native invocation policy')
            skills[name] = front
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
        if path.suffix in ('.md', '.toml', '.sh'):
            for reference in re.findall(r"~/.claude/(?:agents|agent-guides|skills|bin)/[^\s`\x27\x22]+", text):
                reference = reference.rstrip('.,;)')
                if '<' in reference or '*' in reference:
                    continue  # Placeholder or glob.
                group = re.search(r'\{([^{}]+)\}', reference)
                references = ([reference[:group.start()] + choice + reference[group.end():]
                               for choice in group[1].split(',')] if group else [reference])
                for candidate in references:
                    check((ROOT / '.claude' / candidate.removeprefix('~/.claude/')).exists(),
                          name + ': broken installed reference: ' + candidate)
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                if target == 'URL' or target.startswith(('#', '~/', 'https://', 'http://', 'mailto:')):
                    continue  # Placeholder, fragment, or external reference.
                destination = (path.parent / target.split('#')[0]).resolve()
                check(destination.exists(), name + ': broken local link: ' + target)
    validate_capabilities(agents)
    check(agents.keys() <= claude_agents.keys(),
          'Missing Claude agent counterparts: ' + ', '.join(sorted(agents.keys() - claude_agents.keys())))
    for source, front in skills.items():
        if not source.startswith('.codex/skills/'):
            continue
        target = source.replace('.codex/skills/', '.claude/skills/', 1)
        check(target in skills, source + ': missing Claude skill counterpart')
        check(skills[target].get('disable-model-invocation') == front.get('disable-model-invocation'),
              source + ': Claude invocation policy differs')
    for name in ('pr-review', 'pr-risk'):
        check('reviewer_attribution.py' in agents[name]['developer_instructions'],
              name + ': derive signoff from execution fields')
    profile_path = ROOT / '.codex/agents/scripts/claude-review.toml'
    profile = tomllib.loads(profile_path.read_text())
    check('-'.join(profile['label'].lower().split()).replace('.', '-') == profile['model'],
          'Claude display name differs from model identifier')
    check(profile['effort'] in {'low', 'medium', 'high', 'xhigh', 'max'},
          'Claude profile has invalid CLI effort')
    check(isinstance(profile['allowed_tools'], list) and 'Bash' in profile['allowed_tools']
          and all(isinstance(tool, str) for tool in profile['allowed_tools']),
          'Claude profile needs a tool list with trusted shell access')
    for name in ('pr-review-high', 'delegate-xhigh'):
        check('claude-review.toml' in agents[name]['developer_instructions'],
              name + ': Claude wrapper must reference the shared execution profile')
    print(f'Validated {len(agents)} Codex agents, {len(claude_agents)} Claude agents, {skill_count} skills, YAML/TOML, Python, local links, and public-file checks.')


if __name__ == '__main__':
    try:
        validate()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error)) from None
