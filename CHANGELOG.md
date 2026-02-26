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
- Trading mode toggle now persists immediately in bot config on click.
- Bot list columns adjusted for more even spacing; status/mode/pid/action are aligned and action button size is consistent.
- Bot config field order updated: Name, Emoji/Avatar, Trading Mode, Strategy, then Config.
- Switching between bots now warns if there are unsaved changes.
- Bot config panel now uses remaining width while bot list remains fixed at 25%.
- Bot config JSON textbox moved below SOUL and set to read-only.
- Trading mode toggle now refreshes bot list/status view and reloads bot config after change.
- Bot row spacing and action column sizing tuned for more consistent button visibility.
- Fixed bot row grid sizing in narrow left panel so Start/Stop toggle is always visible.
- Bot config panel now explicitly flexes to fill remaining horizontal space.
- Trading Bots config panel now stretches vertically to fill remaining page height.
- PID handling now preserves and displays last known PID after start/stop transitions.
- Mode/PID display split onto two lines for clearer readability.
- Removed PID from bot list row display to keep the list cleaner.
- SOUL editor now expands to fill available vertical space in bot config panel.
- Trading mode changes now require modal confirmation before applying.
- Added new sidebar section **Tools** with **Back-Testing** menu item and a dedicated placeholder page.
- Refactored UI template into smaller component files (styles, sidebar, main content, modals, scripts) to keep template code maintainable.
- Sidebar navigation updated: restored **Tools** with **Back-Testing** and added separate **Report** section with **Back-Testing Reports**.
- Added **Readiness Checklist** report page with production-readiness milestones for automated trading rollout.
- Added **Strategy Research** page under Tools with JSON feed storage for popular/latest strategy leads.
- Strategy Research page now renders feed items as blog-style cards with synopsis and action buttons (Discard / Investigate).
- Added a **Confidence Model** info button + modal on Strategy Research page explaining score components and weighting.
- Added `BACKLOG.md` entry for future Discord channel -> agent -> model routing.
- Utility bot naming adjusted to **Dax** display name.
- Trading mode controls are now hidden for utility bots in bot config.
- Added utility bot scaffold **DAX** (`agents/utility/dax`) and validated a test run writing into `strategy_research.json`.
- Added **Changelog** page in the Mission Control UI (Configuration section), backed by `CHANGELOG.md`.
- Added a richer **Mission Control Overview** block on the Home dashboard summarizing current capabilities and key missing pieces for full automation.
- Added utility bot **Bashir** (`agents/utility/bashir`) and wired Investigate action to trigger deep research runs.
- Sidebar updated with a dedicated **Strategy Research** category and Research Feed item.
- Added **Strategy Research Reports** page with report list, report viewer, and one-click backtest trigger + result display.
- Bot page UX polish: utility page now uses same split layout as trading (left list + right config panel), utility rows hide paper/live text, and top header/sidebar divider alignment improved.
- Bot config panel now dynamically adapts by bot type (utility hides trading-mode and strategy controls) for cleaner utility workflows.
- Standardized top divider alignment by tying sidebar header and page header to the same `--topbar-height` token.
- Fixed CSS selector collision so sidebar header and page header both use explicit, synchronized topbar styles.
- Added hard topbar sync rules to keep sidebar/header divider perfectly aligned even on scroll-heavy pages.
- Added process note to keep Home Overview + Readiness Checklist updated as changes are implemented.
- Investigate now produces synthesized strategy output and writes both strategy markdown and research report artifacts.
- Updated **Dax** strategy scan behavior to return up to 5 ideas per run and avoid repeating previously returned strategy titles.
- Dax live scan now uses real-source RSS collection and populates research feed with non-example links.
