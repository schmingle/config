# Claude porting decisions

Record approved, public-safe Claude-specific decisions here so repeated
[porter reviews](agents/port-to-claude.md) preserve their intent. This file holds
scoped exceptions to the Codex configuration, not a second copy of that configuration.

Only add or change a decision with explicit user approval. The porter reads this
file but does not edit it. New explicit user instructions supersede older entries;
other conflicts require a human decision. Private context belongs outside this
public repository. Use a short approval reference rather than copying chat content.

## Active decisions

None recorded yet.

## Entry template

Copy this template into Active decisions when a rule is approved. Replace the
placeholders and remove “None recorded yet.” Keep expired or superseded rules
clearly marked as inactive so they are not applied on later runs.

```markdown
### <Decision name>
- Rule: <Claude-specific behavior to preserve>
- Scope: <Affected paths, roles, or workflows>
- Rationale: <Why this differs from Codex>
- Approved: <Date and retrievable approval reference>
- Revisit: <Optional expiry or condition; otherwise until superseded>
```
