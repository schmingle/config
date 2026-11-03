#!/usr/bin/env python3
"""Derive a native review signoff from the agent's execution fields."""
import argparse
from pathlib import Path
import tomllib

AGENTS = Path(__file__).resolve().parents[1]


def native_attribution(settings, contribution='Reviewed by'):
    model = settings['model']
    effort = settings['model_reasoning_effort']
    if model.startswith('gpt-'):
        _, version, *family = model.split('-')
        label = 'GPT-' + version
        if family:
            label += ' ' + ' '.join(part.title() for part in family)
    else:
        label = model  # Preserve an unknown identifier instead of guessing its public name.
    return f'{contribution} {label} {effort}.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    approach_roles = ('pr-review-approach',)
    parser.add_argument('agent', choices=['pr-review', 'pr-review-high', 'pr-risk', *approach_roles])
    args = parser.parse_args()
    settings = tomllib.loads((AGENTS / (args.agent + '.toml')).read_text())
    contribution = 'Approach analysis by' if args.agent in approach_roles else 'Reviewed by'
    print(native_attribution(settings, contribution))


if __name__ == '__main__':
    main()
