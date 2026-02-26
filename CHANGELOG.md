# Mission Control Changelog

## 2026-02-26

### Added
- Strategy emoji selector support in both create modal and strategy edit panel.
- Native emoji suggestion list (`datalist`) for quick emoji picking.

### Changed
- Strategy create flow now accepts and persists selected emoji.
- Strategy editor emoji input now uses selector list while still allowing manual emoji entry.
- Trading bot config emoji input now uses an emoji selector list (manual entry still allowed).
- Bot config panel now hides STRATEGY.md, TRADE_STATE.md, and TRADE_LOG.md editors (strategy is dropdown-selected; state/log reserved for reporting).
- Bot config now supports Trading Mode toggle buttons (Paper vs Live) instead of dropdown.
- Bot creation now standardizes folder names to lowercase_slug (e.g., "Kerr Avon" -> `kerr_avon`) while keeping display name in config.
- Bot config now uses a bot name text field (instead of dropdown); saving can rename bot folder to slugified name.
- Bot list action changed to a single status-aware toggle button (green Start when off, red Stop when on).
- Trading mode toggle now persists immediately in bot config on save flow.
