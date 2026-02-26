from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import os
import signal
import subprocess
import time
import shutil

BASE = Path(os.getenv("OPENCLAW_WORKSPACE", "/Users/markfiebiger/.openclaw/workspace")).resolve()
MC_DIR = Path(__file__).resolve().parent
AGENTS_DIR = BASE / "agents"
STATE_FILE = MC_DIR / "state.json"
USAGE_FILE = MC_DIR / "usage.json"
STRATEGIES_FILE = MC_DIR / "strategies.json"
BOT_ORDER_FILE = MC_DIR / "bot_order.json"
TEMPLATE_DIR = AGENTS_DIR / "bot-template"

app = FastAPI()


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"bots": {}}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_usage():
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {"total": {"tokens_in": 0, "tokens_out": 0, "cost": 0}, "bots": {}}


def save_usage(data):
    USAGE_FILE.write_text(json.dumps(data, indent=2))


def load_strategies():
    if STRATEGIES_FILE.exists():
        return json.loads(STRATEGIES_FILE.read_text())
    return {"list": []}


def save_strategies(data):
    STRATEGIES_FILE.write_text(json.dumps(data, indent=2))


def list_bots():
    bots = []
    if not AGENTS_DIR.exists():
        return bots
    for d in AGENTS_DIR.iterdir():
        if d.is_dir() and d.name != "bot-template":
            bot_py = d / "bot.py"
            if bot_py.exists():
                bots.append(d.name)
    return bots


def bot_kind(name: str) -> str:
    cfg = AGENTS_DIR / name / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text())
            kind = str(data.get("bot_kind") or data.get("type") or data.get("category") or "").lower()
            if kind == "utility":
                return "utility"
        except Exception:
            pass
    return "trading"


def bot_profile(name: str) -> dict:
    cfg = AGENTS_DIR / name / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text())
            return {
                "emoji": data.get("emoji", "🤖"),
                "avatar": data.get("avatar", ""),
            }
        except Exception:
            pass
    return {"emoji": "🤖", "avatar": ""}


def load_bot_order() -> list:
    if BOT_ORDER_FILE.exists():
        try:
            data = json.loads(BOT_ORDER_FILE.read_text())
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_bot_order(order: list):
    BOT_ORDER_FILE.write_text(json.dumps(order, indent=2))


def apply_bot_order(bots: list) -> list:
    order = load_bot_order()
    ordered = [b for b in order if b in bots]
    remaining = [b for b in bots if b not in ordered]
    return ordered + sorted(remaining)


def is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def bot_status(name: str):
    state = load_state()
    bot_state = state.get("bots", {}).get(name, {})
    pid = bot_state.get("pid")
    if pid and is_pid_running(pid):
        return {"status": "running", "pid": pid}
    return {"status": "stopped", "pid": None}


def render_dashboard(active_page="trading-bots"):
    bots = apply_bot_order(list_bots())
    trading_rows = []
    utility_rows = []
    for b in bots:
        status = bot_status(b)
        profile = bot_profile(b)
        badge_class = "badge-live" if status['status'] == "running" else "badge-idle"
        avatar_html = f"<img src='{profile['avatar']}' class='bot-avatar' />" if profile.get('avatar') else f"<span class='bot-emoji'>{profile.get('emoji') or '🤖'}</span>"
        row_html = f"""
        <div class="bot-row" draggable="true" data-bot="{b}">
          <div class="bot-col bot-name">{avatar_html} {b}</div>
          <div class="bot-col"><span class="card-badge {badge_class}">{status['status']}</span></div>
          <div class="bot-col">PID: {status['pid'] or '-'}</div>
          <div class="bot-col actions">
            <button class="btn-primary" onclick="fetch('/api/bot/{b}/start',{{method:'POST'}}).then(()=>location.reload())">Start</button>
            <button class="btn-secondary" onclick="fetch('/api/bot/{b}/stop',{{method:'POST'}}).then(()=>location.reload())">Stop</button>
            <button class="btn-secondary config-btn" data-bot="{b}" onclick="openConfig('{b}')">Config</button>
          </div>
        </div>
        """
        if bot_kind(b) == "utility":
            utility_rows.append(row_html)
        else:
            trading_rows.append(row_html)

    html = """
    <html>
      <head>
        <title>Mission Control</title>
        <style>
          :root {
            --bg: #0d1117;
            --card-bg: #161b22;
            --card-hover: #1c2128;
            --border: #30363d;
            --text: #c9d1d9;
            --text-muted: #8b949e;
            --accent: #58a6ff;
            --green: #3fb950;
            --yellow: #d29922;
            --red: #f85149;
            --purple: #a371f7;
            --orange: #db6d28;
            --sidebar-width: 220px;
          }
          [data-theme="light"] {
            --bg: #f5f7fb;
            --card-bg: #ffffff;
            --card-hover: #f1f4f8;
            --border: #d7dde6;
            --text: #0b1220;
            --text-muted: #5b6776;
            --accent: #2f6df6;
            --green: #1f9d55;
            --yellow: #d29922;
            --red: #e53935;
            --purple: #8b5cf6;
            --orange: #db6d28;
          }
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; overflow: hidden; }

          .btn-primary, .btn-secondary, .btn-danger { padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; border: 1px solid var(--border); transition: all 0.15s ease; }
          .btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
          .btn-primary:hover { background: #4c9aed; border-color: #4c9aed; }
          .btn-secondary { background: var(--card-bg); color: var(--text); }
          .btn-secondary:hover { background: var(--card-hover); border-color: var(--accent); }
          .btn-danger { background: var(--red); color: #fff; border: 1px solid var(--red); }
          .btn-danger:hover { background: #df4a42; border-color: #df4a42; }

          .sidebar { width: var(--sidebar-width); background: var(--card-bg); border-right: 1px solid var(--border); height: 100vh; position: fixed; top: 0; left: 0; display: flex; flex-direction: column; z-index: 60; }
          .sidebar-header { padding: 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
          .sidebar-title { font-size: 0.9rem; font-weight: 600; white-space: nowrap; }
          .sidebar-toggle { margin-left: auto; background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 6px; border-radius: 6px; font-size: 1rem; }
          .sidebar-toggle:hover { background: var(--bg); color: var(--text); }
          .sidebar-nav { flex: 1; padding: 12px 8px; overflow-y: auto; }
          .nav-section-title { font-size: 0.65rem; text-transform: uppercase; color: var(--text-muted); padding: 8px 12px 4px; letter-spacing: 0.5px; }
          .nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; color: var(--text-muted); transition: all 0.15s; text-decoration: none; }
          .nav-item:hover { background: var(--bg); color: var(--text); }
          .nav-item.active { background: rgba(88, 166, 255, 0.15); color: var(--accent); }
          .nav-icon { font-size: 1rem; width: 20px; text-align: center; }

          .main-wrapper { flex: 1; margin-left: var(--sidebar-width); display: flex; flex-direction: column; height: 100vh; overflow-y: auto; scroll-behavior: smooth; }
          header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid var(--border); background: var(--card-bg); position: sticky; top: 0; z-index: 50; }
          .page-title { font-size: 1.1rem; font-weight: 600; }
          .status-pill { display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(63, 185, 80, 0.15); border-radius: 20px; font-size: 0.8rem; color: var(--green); }
          .pulse { width: 8px; height: 8px; background: var(--green); border-radius: 50%; animation: pulse 2s infinite; }
          @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

          main { padding: 24px; flex: 1; }
          .bot-list { display: flex; flex-direction: column; gap: 10px; }
          .bot-row { display: grid; grid-template-columns: 1.2fr 0.6fr 0.8fr 1fr; gap: 10px; align-items: center; background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
          .bot-row:hover { background: var(--card-hover); border-color: var(--accent); }
          .bot-row.dragging { opacity: 0.5; }
          .bot-row.drop-target { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset; }
          .bot-col { font-size: 0.85rem; color: var(--text-muted); }
          .bot-name { color: var(--text); font-weight: 600; display:flex; align-items:center; gap:8px; }
          .bot-avatar { width:20px; height:20px; border-radius:50%; object-fit:cover; }
          .bot-emoji { font-size: 1rem; line-height: 1; }
          .card-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
          .card-icon { width: 40px; height: 40px; background: var(--bg); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; }
          .card-icon.main { background: rgba(163, 113, 247, 0.15); }
          .card-title { font-size: 0.9rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
          .card-subtitle { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }
          .card-preview { font-size: 0.75rem; color: var(--text-muted); margin-top: 6px; font-style: italic; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
          .card-badge { padding: 3px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 500; flex-shrink: 0; }
          .badge-live { background: rgba(63, 185, 80, 0.2); color: var(--green); }
          .badge-idle { background: rgba(139, 148, 158, 0.15); color: var(--text-muted); }
          .card-stats { display: flex; gap: 16px; padding: 10px 0; border-top: 1px solid var(--border); margin-top: 8px; }
          .card-stat { display: flex; align-items: center; gap: 4px; font-size: 0.75rem; color: var(--text-muted); }
          .card-stat-value { color: var(--text); font-weight: 500; }
          .actions { display: flex; gap: 8px; }

          .theme-toggle { background: var(--card-bg); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 999px; cursor: pointer; font-size: 12px; }
          .header-right { display: flex; align-items: center; gap: 12px; }
          .subtle { color: var(--text-muted); font-size: 12px; }

          .config-panel { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
          .config-row { display: flex; gap: 12px; margin-bottom: 12px; }
          .config-row label { font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 6px; }
          .config-row input, .config-row select, textarea { width: 100%; padding: 8px 10px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg); color: var(--text); }
          textarea { min-height: 140px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.8rem; }
          .config-actions { display: flex; gap: 8px; margin-top: 12px; }

          /* Inline config panel */
          .bots-layout { display: flex; gap: 16px; align-items: flex-start; }
          .bot-list-wrap { width: 25%; min-width: 280px; }
          .inline-config { width: 75%; display: none; }
          .inline-config.visible { display: block; }
          .inline-config-header { display:flex; justify-content: space-between; align-items:center; margin-bottom: 10px; }
          .close-btn { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-muted); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; }

          /* Modal */
          .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.55); display: none; align-items: center; justify-content: center; z-index: 200; }
          .modal-overlay.visible { display: flex; }
          .modal { width: 420px; max-width: 92vw; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
          .modal-title { font-weight: 600; margin-bottom: 8px; }
          .modal-text { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 14px; }
          .modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
        </style>
      </head>
      <body>
        <aside class="sidebar">
          <div class="sidebar-header">
            <div class="sidebar-logo">🛰️</div>
            <div class="sidebar-title">Command Center</div>
            <button class="sidebar-toggle" onclick="toggleTheme()">🌗</button>
          </div>
          <div class="sidebar-nav">
            <div class="nav-section-title">Bots</div>
            <a id="nav-trading-bots" class="nav-item" href="/"><span class="nav-icon">📈</span><span>Trading Bots</span></a>
            <a id="nav-utility-bots" class="nav-item" href="/utility-bots"><span class="nav-icon">🛠️</span><span>Utility Bots</span></a>
            <div class="nav-section-title">Configuration</div>
            <a id="nav-usage" class="nav-item" href="/usage"><span class="nav-icon">📊</span><span>Usage</span></a>
            <a id="nav-strategies" class="nav-item" href="/strategies"><span class="nav-icon">🧠</span><span>Strategies</span></a>
          </div>
        </aside>

        <div class="main-wrapper">
          <header>
            <div class="header-left">
              <div class="page-title">Mission Control</div>
              <div class="status-pill connected"><span class="pulse"></span>Live</div>
            </div>
            <div class="header-right">
              <div class="subtle">0.0.0.0:7777</div>
              <button class="theme-toggle" onclick="toggleTheme()">Toggle theme</button>
            </div>
          </header>

          <main>
            <section id="trading-bots" class="section">
              <div class="section-header" style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div class="section-title">Trading Bots</div>
                <button class="btn-primary" onclick="createBot()">Create Bot</button>
              </div>
              <div class="bots-layout">
                <div class="bot-list-wrap">
                  <div class="bot-list">
                    {{TRADING_ROWS}}
                  </div>
                </div>
                <div class="inline-config" id="configPanel">
                  <div class="config-panel">
                    <div class="inline-config-header">
                      <div class="section-title">Bot Config</div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>Bot</label>
                        <select id="botSelect"></select>
                      </div>
                      <div style="flex:1;">
                        <label>Strategy</label>
                        <select id="strategySelect"></select>
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>Emoji</label>
                        <input id="emojiInput" placeholder="🤖" />
                      </div>
                      <div style="flex:2;">
                        <label>Avatar URL (optional)</label>
                        <input id="avatarInput" placeholder="https://..." />
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>Config (config.json)</label>
                        <textarea id="configText"></textarea>
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>SOUL.md</label>
                        <textarea id="soulText"></textarea>
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>STRATEGY.md</label>
                        <textarea id="strategyText"></textarea>
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>TRADE_STATE.md</label>
                        <textarea id="stateText"></textarea>
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>TRADE_LOG.md</label>
                        <textarea id="logText"></textarea>
                      </div>
                    </div>
                    <div class="config-actions" style="justify-content: space-between; align-items: center;">
                      <div>
                        <button class="btn-primary" onclick="saveAll()">Save</button>
                      </div>
                      <button class="btn-danger" onclick="deleteBot()">Delete Bot</button>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section id="utility-bots" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Utility Bots</div>
              </div>
              <div class="bot-list">
                {{UTILITY_ROWS}}
              </div>
            </section>

            <section id="usage" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Usage</div>
              </div>
              <div class="config-panel" id="usagePanel">
                <div class="config-row">
                  <div style="flex:1;">
                    <label>Total Tokens In</label>
                    <input id="totalTokensIn" disabled />
                  </div>
                  <div style="flex:1;">
                    <label>Total Tokens Out</label>
                    <input id="totalTokensOut" disabled />
                  </div>
                  <div style="flex:1;">
                    <label>Total Cost</label>
                    <input id="totalCost" disabled />
                  </div>
                </div>
                <div class="config-row">
                  <div style="flex:1;">
                    <label>Per‑Bot Usage (JSON)</label>
                    <textarea id="perBotUsage" readonly></textarea>
                  </div>
                </div>
              </div>
            </section>

            <section id="strategies" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Strategies</div>
              </div>
              <div class="config-panel">
                <div class="config-row">
                  <div style="flex:1;">
                    <label>Strategy List (JSON)</label>
                    <textarea id="strategiesText"></textarea>
                  </div>
                </div>
                <div class="config-actions">
                  <button class="btn-primary" onclick="saveStrategies()">Save Strategies</button>
                </div>
              </div>
            </section>
          </main>
        </div>

        <div class="modal-overlay" id="createModal">
          <div class="modal">
            <div class="modal-title">Create Bot</div>
            <div class="modal-text">Enter a name for the new bot.</div>
            <div class="config-row" style="margin-bottom: 8px;">
              <div style="flex:1;">
                <input id="createBotName" placeholder="e.g. cally-eth" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideCreateModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmCreateBot()">Create</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="saveModal">
          <div class="modal">
            <div class="modal-title">Save Changes</div>
            <div class="modal-text">Save config and all bot files for this bot?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideSaveModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmSaveAll()">Save</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="deleteModal">
          <div class="modal">
            <div class="modal-title">Delete Bot</div>
            <div class="modal-text" id="deleteModalText">Are you sure you want to delete this bot?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideDeleteModal()">Cancel</button>
              <button class="btn-danger" onclick="confirmDeleteBot()">Delete</button>
            </div>
          </div>
        </div>

        <script>
          const saved = localStorage.getItem('mc-theme') || 'dark';
          document.documentElement.dataset.theme = saved === 'light' ? 'light' : 'dark';
          function toggleTheme() {
            const current = document.documentElement.dataset.theme;
            const next = current === 'light' ? 'dark' : 'light';
            document.documentElement.dataset.theme = next;
            localStorage.setItem('mc-theme', next);
          }

          async function loadBots() {
            const res = await fetch('/api/bots');
            const data = await res.json();
            const sel = document.getElementById('botSelect');
            sel.innerHTML = data.bots.map(b => '<option value="' + b + '">' + b + '</option>').join('');
            if (data.bots.length) {
              openConfig(data.bots[0]);
            }
          }

          async function loadConfig(bot) {
            const res = await fetch('/api/bot/' + bot + '/config');
            const data = await res.json();
            document.getElementById('configText').value = JSON.stringify(data, null, 2);
            document.getElementById('botSelect').value = bot;
            document.getElementById('emojiInput').value = data.emoji || '';
            document.getElementById('avatarInput').value = data.avatar || '';
          }

          async function loadFiles(bot) {
            const res = await fetch('/api/bot/' + bot + '/files');
            const data = await res.json();
            document.getElementById('soulText').value = data.SOUL || '';
            document.getElementById('strategyText').value = data.STRATEGY || '';
            document.getElementById('stateText').value = data.TRADE_STATE || '';
            document.getElementById('logText').value = data.TRADE_LOG || '';
          }

          async function saveConfigData() {
            const bot = document.getElementById('botSelect').value;
            const text = document.getElementById('configText').value;
            let payload;
            try { payload = JSON.parse(text); } catch (e) { alert('Invalid JSON'); return false; }
            const strat = document.getElementById('strategySelect').value;
            payload.strategy = strat;
            payload.emoji = document.getElementById('emojiInput').value || '🤖';
            payload.avatar = document.getElementById('avatarInput').value || '';
            await fetch('/api/bot/' + bot + '/config', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            return true;
          }

          async function saveFilesData() {
            const bot = document.getElementById('botSelect').value;
            const payload = {
              SOUL: document.getElementById('soulText').value,
              STRATEGY: document.getElementById('strategyText').value,
              TRADE_STATE: document.getElementById('stateText').value,
              TRADE_LOG: document.getElementById('logText').value
            };
            await fetch('/api/bot/' + bot + '/files', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            return true;
          }

          function saveAll() {
            document.getElementById('saveModal').classList.add('visible');
          }

          function hideSaveModal() {
            document.getElementById('saveModal').classList.remove('visible');
          }

          async function confirmSaveAll() {
            const ok = await saveConfigData();
            if (!ok) return;
            await saveFilesData();
            hideSaveModal();
          }

          function createBot() {
            document.getElementById('createBotName').value = '';
            document.getElementById('createModal').classList.add('visible');
            setTimeout(() => document.getElementById('createBotName').focus(), 50);
          }

          function hideCreateModal() {
            document.getElementById('createModal').classList.remove('visible');
          }

          async function confirmCreateBot() {
            const name = document.getElementById('createBotName').value.trim();
            if (!name) return;
            await fetch('/api/bot/create', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name}) });
            hideCreateModal();
            location.reload();
          }

          let pendingDeleteBot = null;

          async function deleteBot() {
            const bot = document.getElementById('botSelect').value;
            if (!bot) return;
            pendingDeleteBot = bot;
            document.getElementById('deleteModalText').innerText = 'Are you sure you want to delete "' + bot + '"? This cannot be undone.';
            document.getElementById('deleteModal').classList.add('visible');
          }

          function hideDeleteModal() {
            pendingDeleteBot = null;
            document.getElementById('deleteModal').classList.remove('visible');
          }

          async function confirmDeleteBot() {
            if (!pendingDeleteBot) return;
            await fetch('/api/bot/' + pendingDeleteBot + '/delete', { method:'POST' });
            hideDeleteModal();
            location.reload();
          }

          async function loadUsage() {
            const res = await fetch('/api/usage');
            const data = await res.json();
            document.getElementById('totalTokensIn').value = data.total?.tokens_in ?? 0;
            document.getElementById('totalTokensOut').value = data.total?.tokens_out ?? 0;
            document.getElementById('totalCost').value = data.total?.cost ?? 0;
            document.getElementById('perBotUsage').value = JSON.stringify(data.bots || {}, null, 2);
          }

          async function loadStrategies() {
            const res = await fetch('/api/strategies');
            const data = await res.json();
            document.getElementById('strategiesText').value = JSON.stringify(data, null, 2);
            const sel = document.getElementById('strategySelect');
            sel.innerHTML = (data.list || []).map(s => '<option value="' + s + '">' + s + '</option>').join('');
          }

          async function saveStrategies() {
            let payload;
            try { payload = JSON.parse(document.getElementById('strategiesText').value); } catch (e) { alert('Invalid JSON'); return; }
            await fetch('/api/strategies', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            await loadStrategies();
            alert('Saved strategies');
          }

          let currentConfigBot = null;

          function updateConfigButtons() {
            document.querySelectorAll('.config-btn').forEach(btn => {
              const isCurrent = btn.getAttribute('data-bot') === currentConfigBot;
              btn.disabled = isCurrent;
              btn.style.opacity = isCurrent ? '0.6' : '1';
              btn.style.cursor = isCurrent ? 'not-allowed' : 'pointer';
            });
          }

          function openConfig(bot) {
            currentConfigBot = bot;
            updateConfigButtons();
            document.getElementById('configPanel').classList.add('visible');
            loadConfig(bot);
            loadFiles(bot);
            loadStrategies();
          }

          function closePanel() {
            document.getElementById('configPanel').classList.remove('visible');
          }

          function wireDragAndDrop() {
            let dragged = null;
            const rows = document.querySelectorAll('.bot-row');
            rows.forEach(row => {
              row.addEventListener('dragstart', () => {
                dragged = row;
                row.classList.add('dragging');
              });
              row.addEventListener('dragend', () => {
                row.classList.remove('dragging');
                document.querySelectorAll('.bot-row').forEach(r => r.classList.remove('drop-target'));
              });
              row.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (row !== dragged) row.classList.add('drop-target');
              });
              row.addEventListener('dragleave', () => row.classList.remove('drop-target'));
              row.addEventListener('drop', async (e) => {
                e.preventDefault();
                row.classList.remove('drop-target');
                if (!dragged || row === dragged) return;
                const parent = row.parentNode;
                parent.insertBefore(dragged, row);
                const order = Array.from(parent.querySelectorAll('.bot-row')).map(el => el.getAttribute('data-bot'));
                await fetch('/api/bots/order', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ order }) });
                location.reload();
              });
            });
          }

          const activePage = '{{ACTIVE_PAGE}}';
          document.getElementById('nav-' + activePage)?.classList.add('active');
          document.getElementById('trading-bots').style.display = activePage === 'trading-bots' ? 'block' : 'none';
          document.getElementById('utility-bots').style.display = activePage === 'utility-bots' ? 'block' : 'none';
          document.getElementById('usage').style.display = activePage === 'usage' ? 'block' : 'none';
          document.getElementById('strategies').style.display = activePage === 'strategies' ? 'block' : 'none';

          if (activePage === 'trading-bots' || activePage === 'utility-bots') {
            loadBots();
            loadStrategies();
            setTimeout(wireDragAndDrop, 50);
          }
          if (activePage === 'usage') {
            loadUsage();
          }
          if (activePage === 'strategies') {
            loadStrategies();
          }

          document.getElementById('createBotName')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') confirmCreateBot();
          });

          document.getElementById('botSelect')?.addEventListener('change', (e) => {
            const bot = e.target.value;
            currentConfigBot = bot;
            updateConfigButtons();
            loadConfig(bot);
            loadFiles(bot);
          });
        </script>
      </body>
    </html>
    """
    utility_html = "".join(utility_rows) if utility_rows else '<div class="bot-col">No utility bots yet.</div>'
    html = html.replace("{{TRADING_ROWS}}", "".join(trading_rows))
    html = html.replace("{{UTILITY_ROWS}}", utility_html)
    html = html.replace("{{ACTIVE_PAGE}}", active_page)
    return HTMLResponse(html)



@app.get("/", response_class=HTMLResponse)
def home():
    return render_dashboard("trading-bots")


@app.get("/utility-bots", response_class=HTMLResponse)
def utility_bots_page():
    return render_dashboard("utility-bots")


@app.get("/usage", response_class=HTMLResponse)
def usage_page():
    return render_dashboard("usage")


@app.get("/strategies", response_class=HTMLResponse)
def strategies_page():
    return render_dashboard("strategies")


@app.get("/api/bots")
def api_bots():
    bots = apply_bot_order(list_bots())
    return JSONResponse({"bots": bots})


@app.post("/api/bots/order")
def api_bots_order(payload: dict):
    order = payload.get("order", [])
    if not isinstance(order, list):
        raise HTTPException(400, "order must be a list")
    valid = set(list_bots())
    cleaned = [b for b in order if b in valid]
    save_bot_order(cleaned)
    return {"ok": True}


@app.get("/api/bot/{name}/status")
def api_bot_status(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    return bot_status(name)


@app.post("/api/bot/{name}/start")
def api_bot_start(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    status = bot_status(name)
    if status["status"] == "running":
        return {"ok": True, "message": "Already running"}

    bot_dir = AGENTS_DIR / name
    bot_py = bot_dir / "bot.py"
    if not bot_py.exists():
        raise HTTPException(404, "bot.py not found")

    proc = subprocess.Popen(["python3", str(bot_py)], cwd=str(bot_dir))

    state = load_state()
    state.setdefault("bots", {})[name] = {"pid": proc.pid, "started_at": int(time.time())}
    save_state(state)
    return {"ok": True, "pid": proc.pid}


@app.post("/api/bot/{name}/stop")
def api_bot_stop(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    state = load_state()
    bot_state = state.get("bots", {}).get(name, {})
    pid = bot_state.get("pid")
    if not pid:
        return {"ok": True, "message": "Already stopped"}

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass

    bot_state["pid"] = None
    state.setdefault("bots", {})[name] = bot_state
    save_state(state)
    return {"ok": True}


@app.get("/api/bot/{name}/config")
def api_bot_config(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    cfg = AGENTS_DIR / name / "config.json"
    if not cfg.exists():
        return {}
    return JSONResponse(json.loads(cfg.read_text()))


@app.post("/api/bot/{name}/config")
def api_bot_config_save(name: str, payload: dict):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    cfg = AGENTS_DIR / name / "config.json"
    cfg.write_text(json.dumps(payload, indent=2))
    return {"ok": True}


@app.get("/api/bot/{name}/files")
def api_bot_files(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    base = AGENTS_DIR / name
    files = {
        "SOUL": (base / "SOUL.md").read_text() if (base / "SOUL.md").exists() else "",
        "STRATEGY": (base / "STRATEGY.md").read_text() if (base / "STRATEGY.md").exists() else "",
        "TRADE_STATE": (base / "TRADE_STATE.md").read_text() if (base / "TRADE_STATE.md").exists() else "",
        "TRADE_LOG": (base / "TRADE_LOG.md").read_text() if (base / "TRADE_LOG.md").exists() else "",
    }
    return JSONResponse(files)


@app.post("/api/bot/{name}/files")
def api_bot_files_save(name: str, payload: dict):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    base = AGENTS_DIR / name
    if "SOUL" in payload:
        (base / "SOUL.md").write_text(payload.get("SOUL", ""))
    if "STRATEGY" in payload:
        (base / "STRATEGY.md").write_text(payload.get("STRATEGY", ""))
    if "TRADE_STATE" in payload:
        (base / "TRADE_STATE.md").write_text(payload.get("TRADE_STATE", ""))
    if "TRADE_LOG" in payload:
        (base / "TRADE_LOG.md").write_text(payload.get("TRADE_LOG", ""))
    return {"ok": True}


@app.get("/api/strategies")
def api_strategies():
    return load_strategies()


@app.post("/api/strategies")
def api_strategies_save(payload: dict):
    save_strategies(payload)
    return {"ok": True}


@app.post("/api/bot/create")
def api_bot_create(payload: dict):
    name = payload.get("name", "").strip()
    if not name:
        raise HTTPException(400, "Name required")
    target = AGENTS_DIR / name
    if target.exists():
        raise HTTPException(400, "Bot already exists")
    if TEMPLATE_DIR.exists():
        shutil.copytree(TEMPLATE_DIR, target)
        # ensure a bot.py exists for runnable bots
        if not (target / "bot.py").exists():
            (target / "bot.py").write_text("#!/usr/bin/env python3\nprint('Bot runner not implemented yet')\n")
    else:
        target.mkdir(parents=True)
        (target / "bot.py").write_text("#!/usr/bin/env python3\nprint('Bot runner not implemented yet')\n")
        (target / "config.json").write_text(json.dumps({}, indent=2))
    return {"ok": True, "name": name}


@app.post("/api/bot/{name}/delete")
def api_bot_delete(name: str):
    if name == "bot-template":
        raise HTTPException(400, "Cannot delete template")
    target = AGENTS_DIR / name
    if not target.exists() or not target.is_dir():
        raise HTTPException(404, "Bot not found")
    shutil.rmtree(target)
    # cleanup runtime state if present
    state = load_state()
    if "bots" in state and name in state["bots"]:
        del state["bots"][name]
        save_state(state)
    return {"ok": True}


@app.get("/api/usage")
def api_usage():
    return load_usage()


@app.post("/api/usage/{name}")
def api_usage_update(name: str, payload: dict):
    data = load_usage()
    bot = data.setdefault("bots", {}).setdefault(name, {"tokens_in": 0, "tokens_out": 0, "cost": 0})
    bot["tokens_in"] = int(payload.get("tokens_in", bot["tokens_in"]))
    bot["tokens_out"] = int(payload.get("tokens_out", bot["tokens_out"]))
    bot["cost"] = float(payload.get("cost", bot["cost"]))
    bot["last_seen"] = int(time.time())

    # recompute totals
    total_in = sum(b.get("tokens_in", 0) for b in data["bots"].values())
    total_out = sum(b.get("tokens_out", 0) for b in data["bots"].values())
    total_cost = sum(b.get("cost", 0.0) for b in data["bots"].values())
    data["total"] = {"tokens_in": total_in, "tokens_out": total_out, "cost": total_cost}
    save_usage(data)
    return {"ok": True}
