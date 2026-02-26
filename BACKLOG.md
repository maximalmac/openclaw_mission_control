# Mission Control Backlog

## Planned

- [ ] Discord channel -> agent -> model routing
  - Goal: allow different Discord channels to run different AI models.
  - Approach: create per-channel agents with dedicated primary models, then bind channels to those agents.
  - Notes: prefer this over ad-hoc per-session overrides for long-term stability.
