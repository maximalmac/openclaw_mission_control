DASHBOARD_HTML = r"""
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

          .btn-primary, .btn-secondary, .btn-danger, .btn-success { padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; border: 1px solid var(--border); transition: all 0.15s ease; }
          .btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
          .btn-primary:hover { background: #4c9aed; border-color: #4c9aed; }
          .btn-secondary { background: var(--card-bg); color: var(--text); }
          .btn-secondary:hover { background: var(--card-hover); border-color: var(--accent); }
          .btn-danger { background: var(--red); color: #fff; border: 1px solid var(--red); }
          .btn-danger:hover { background: #df4a42; border-color: #df4a42; }
          .btn-success { background: var(--green); color: #fff; border: 1px solid var(--green); }
          .btn-success:hover { background: #35a545; border-color: #35a545; }

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
          .bot-row { display: grid; grid-template-columns: 1.4fr 0.9fr 1.1fr 0.9fr; gap: 10px; align-items: center; background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 12px; min-width: 0; }
          .bot-row:hover { background: var(--card-hover); border-color: var(--accent); }
          .bot-row.dragging { opacity: 0.5; }
          .bot-row.drop-target { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset; }
          .bot-col { font-size: 0.82rem; color: var(--text-muted); text-align: center; min-width: 0; }
          .bot-name { color: var(--text); font-weight: 600; display:flex; align-items:center; gap:8px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
          .actions { justify-content: center; display:flex; }
          .actions button { min-width: 84px; width: 84px; }
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
          .bots-layout { display: flex; gap: 16px; align-items: stretch; }
          .bot-list-wrap { width: 25%; min-width: 280px; flex: 0 0 25%; }
          .inline-config { flex: 1 1 0; width: auto; min-width: 0; display: none; }
          .inline-config.visible { display: block; }
          .full-height-card .config-panel { height: 100%; display: flex; flex-direction: column; }
          .full-height-card .config-row { flex: 1; display: flex; }
          .full-height-card .config-row > div { display: flex; flex-direction: column; }
          .full-height-card textarea { flex: 1; min-height: 0; }
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
            <div class="nav-section-title">Home</div>
            <a id="nav-home" class="nav-item" href="/"><span class="nav-icon">🏠</span><span>Dashboard</span></a>
            <div class="nav-section-title">Bots</div>
            <a id="nav-trading-bots" class="nav-item" href="/trading-bots"><span class="nav-icon">📈</span><span>Trading Bots</span></a>
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
            </div>
            <div class="header-right">
              <div class="subtle">0.0.0.0:7777</div>
              <button class="theme-toggle" onclick="toggleTheme()">Toggle theme</button>
              <div class="status-pill connected"><span class="pulse"></span>Live</div>
            </div>
          </header>

          <main>
            <section id="home" class="section">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Dashboard</div>
              </div>
              <div class="bot-list" style="gap:16px;">
                <div class="config-panel">
                  <div class="section-title" style="margin-bottom:8px;">Trading Stats</div>
                  <div class="bot-col">Coming next: equity, open positions, daily/weekly P&L, win rate, drawdown.</div>
                </div>
                <div class="config-panel">
                  <div class="section-title" style="margin-bottom:8px;">System Overview</div>
                  <div class="bot-col">Bots online/offline, exchange connectivity, and risk summary will appear here.</div>
                </div>
              </div>
            </section>

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
                        <label>Name</label>
                        <input id="botNameInput" placeholder="e.g. Kerr Avon" />
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>Emoji</label>
                        <input id="emojiInput" list="botEmojiList" placeholder="🤖" />
                      </div>
                      <div style="flex:2;">
                        <label>Avatar URL (optional)</label>
                        <input id="avatarInput" placeholder="https://..." />
                      </div>
                    </div>
                    <div class="config-row" style="flex:0;">
                      <div style="flex:1;">
                        <label>Trading Mode</label>
                        <div style="display:flex; gap:8px;">
                          <button id="modePaperBtn" class="btn-secondary" type="button" onclick="setTradingMode('paper')">Paper Trading</button>
                          <button id="modeLiveBtn" class="btn-secondary" type="button" onclick="setTradingMode('live')">Live Trading</button>
                        </div>
                      </div>
                    </div>
                    <div class="config-row" style="flex:0;">
                      <div style="flex:1;">
                        <label>Strategy</label>
                        <select id="strategySelect"></select>
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
                        <label>Config (config.json)</label>
                        <textarea id="configText" readonly></textarea>
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
              <div class="section-header" style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div class="section-title">Strategies</div>
                <div style="display:flex; gap:8px; align-items:center;">
                  <label style="font-size:.8rem; color: var(--text-muted); display:flex; gap:6px; align-items:center;">
                    <input type="checkbox" id="showArchivedStrategies" onchange="loadStrategies()" />
                    Show archived
                  </label>
                  <button class="btn-primary" onclick="showCreateStrategyModal()">Create Strategy</button>
                </div>
              </div>
              <div class="bots-layout" style="align-items: stretch; min-height: 70vh;">
                <div class="bot-list-wrap">
                  <div class="bot-list" id="strategiesList"></div>
                </div>
                <div class="inline-config visible full-height-card" id="strategyPanel">
                  <div class="config-panel">
                    <div class="inline-config-header">
                      <div class="section-title" id="strategyPanelTitle">Strategy</div>
                    </div>
                    <div class="config-row" style="flex:0;">
                      <div style="flex:1;">
                        <label>Emoji</label>
                        <input id="strategyEmoji" list="strategyEmojiList" placeholder="🧠" style="max-width:120px;" />
                      </div>
                    </div>
                    <div class="config-row">
                      <div style="flex:1;">
                        <label>Markdown</label>
                        <textarea id="strategyMarkdown"></textarea>
                      </div>
                    </div>
                    <div class="config-actions" style="justify-content: space-between; align-items: center;">
                      <div>
                        <button class="btn-primary" onclick="saveStrategyMarkdown()">Save Strategy</button>
                      </div>
                      <div style="display:flex; gap:8px;">
                        <button class="btn-secondary" onclick="toggleArchiveStrategy()" id="archiveStrategyBtn">Archive</button>
                        <button class="btn-danger" onclick="deleteStrategy()">Delete</button>
                      </div>
                    </div>
                  </div>
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

        <div class="modal-overlay" id="createStrategyModal">
          <div class="modal">
            <div class="modal-title">Create Strategy</div>
            <div class="modal-text">Enter a strategy name.</div>
            <div class="config-row" style="margin-bottom: 8px;">
              <div style="flex:1;">
                <input id="createStrategyName" placeholder="e.g. mean-reversion" />
              </div>
            </div>
            <div class="config-row" style="margin-bottom: 8px;">
              <div style="flex:1; max-width:140px;">
                <input id="createStrategyEmoji" list="strategyEmojiList" placeholder="🧠" />
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideCreateStrategyModal()">Cancel</button>
              <button class="btn-primary" onclick="confirmCreateStrategy()">Create</button>
            </div>
          </div>
        </div>

        <div class="modal-overlay" id="deleteStrategyModal">
          <div class="modal">
            <div class="modal-title">Delete Strategy</div>
            <div class="modal-text" id="deleteStrategyText">Are you sure you want to delete this strategy?</div>
            <div class="modal-actions">
              <button class="btn-secondary" onclick="hideDeleteStrategyModal()">Cancel</button>
              <button class="btn-danger" onclick="confirmDeleteStrategy()">Delete</button>
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

        <datalist id="botEmojiList">
          <option value="🤖"></option>
          <option value="📈"></option>
          <option value="📉"></option>
          <option value="⚡"></option>
          <option value="🎯"></option>
          <option value="🛡️"></option>
          <option value="🔥"></option>
          <option value="🧠"></option>
        </datalist>

        <datalist id="strategyEmojiList">
          <option value="🧠"></option>
          <option value="📈"></option>
          <option value="📉"></option>
          <option value="⚡"></option>
          <option value="🎯"></option>
          <option value="🛡️"></option>
          <option value="🔁"></option>
          <option value="🌊"></option>
          <option value="🔥"></option>
          <option value="🤖"></option>
        </datalist>

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
            if (data.bots.length) {
              const remembered = localStorage.getItem('mc-selected-bot');
              const pick = (remembered && data.bots.includes(remembered)) ? remembered : data.bots[0];
              openConfig(pick);
            }
          }

          let currentTradingMode = 'paper';

          async function setTradingMode(mode, persist=true) {
            currentTradingMode = mode === 'live' ? 'live' : 'paper';
            const paperBtn = document.getElementById('modePaperBtn');
            const liveBtn = document.getElementById('modeLiveBtn');
            if (paperBtn && liveBtn) {
              paperBtn.className = currentTradingMode === 'paper' ? 'btn-primary' : 'btn-secondary';
              liveBtn.className = currentTradingMode === 'live' ? 'btn-primary' : 'btn-secondary';
            }
            if (persist && currentConfigBot) {
              const res = await fetch('/api/bot/' + currentConfigBot + '/config');
              const cfg = await res.json();
              cfg.trading_mode = currentTradingMode;
              await fetch('/api/bot/' + currentConfigBot + '/config', {
                method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(cfg)
              });
              await loadConfig(currentConfigBot);
              location.reload();
            }
          }

          async function loadConfig(bot) {
            const res = await fetch('/api/bot/' + bot + '/config');
            const data = await res.json();
            document.getElementById('configText').value = JSON.stringify(data, null, 2);
            document.getElementById('botNameInput').value = data.display_name || bot;
            document.getElementById('emojiInput').value = data.emoji || '';
            document.getElementById('avatarInput').value = data.avatar || '';
            setTradingMode(data.trading_mode || 'paper', false);
          }

          async function loadFiles(bot) {
            const res = await fetch('/api/bot/' + bot + '/files');
            const data = await res.json();
            document.getElementById('soulText').value = data.SOUL || '';
          }

          async function saveConfigData() {
            const bot = currentConfigBot;
            if (!bot) return false;
            const res = await fetch('/api/bot/' + bot + '/config');
            const text = await res.text();
            let payload;
            try { payload = JSON.parse(text); } catch (e) { alert('Invalid JSON'); return false; }
            const strat = document.getElementById('strategySelect').value;
            payload.strategy = strat;
            payload.trading_mode = currentTradingMode || 'paper';
            payload.emoji = document.getElementById('emojiInput').value || '🤖';
            payload.avatar = document.getElementById('avatarInput').value || '';
            payload.display_name = document.getElementById('botNameInput').value.trim() || bot;
            await fetch('/api/bot/' + bot + '/config', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            return true;
          }

          async function saveFilesData() {
            const bot = currentConfigBot;
            if (!bot) return false;
            const payload = {
              SOUL: document.getElementById('soulText').value
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

          async function maybeRenameBot() {
            const bot = currentConfigBot;
            const newName = (document.getElementById('botNameInput').value || '').trim();
            if (!bot || !newName) return bot;
            const res = await fetch('/api/bot/' + bot + '/rename', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ new_name: newName })
            });
            if (!res.ok) {
              const err = await res.json().catch(()=>({}));
              alert(err.detail || 'Failed to rename bot');
              return null;
            }
            const data = await res.json();
            currentConfigBot = data.name;
            localStorage.setItem('mc-selected-bot', data.name);
            return data.name;
          }

          async function confirmSaveAll() {
            const renamed = await maybeRenameBot();
            if (renamed === null) return;
            const ok = await saveConfigData();
            if (!ok) return;
            await saveFilesData();
            hideSaveModal();
            botFormBaseline = getBotFormSnapshot();
            location.reload();
          }

          let pendingCreateKind = 'trading';

          function createBot() {
            pendingCreateKind = (activePage === 'utility-bots') ? 'utility' : 'trading';
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
            await fetch('/api/bot/create', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name, bot_kind: pendingCreateKind}) });
            hideCreateModal();
            location.reload();
          }

          let pendingDeleteBot = null;

          async function deleteBot() {
            const bot = currentConfigBot;
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

          let currentStrategy = null;
          let currentStrategyMeta = null;

          async function loadStrategies() {
            const res = await fetch('/api/strategies');
            const data = await res.json();
            const all = data.list || []; // [{id,name,archived}]
            const showArchived = !!document.getElementById('showArchivedStrategies')?.checked;
            const list = showArchived ? all : all.filter(s => !s.archived);

            const sel = document.getElementById('strategySelect');
            if (sel) sel.innerHTML = all.map(s => '<option value="' + s.id + '">' + (s.emoji || '🧠') + ' ' + s.name + '</option>').join('');

            const container = document.getElementById('strategiesList');
            if (container) {
              container.innerHTML = list.map(s => '<div class="bot-row strategy-row" draggable="true" data-strategy-id="' + s.id + '" onclick="openStrategy(\'' + s.id.replace(/'/g, "\\'") + '\')"><div class="bot-col bot-name">' + (s.emoji || '🧠') + ' ' + s.name + (s.archived ? ' <span style="opacity:.6">(archived)</span>' : '') + '</div></div>').join('');
            }

            wireStrategyDragAndDrop();

            if (list.length) {
              const remembered = localStorage.getItem('mc-selected-strategy');
              const ids = list.map(x => x.id);
              const pick = (remembered && ids.includes(remembered)) ? remembered : list[0].id;
              openStrategy(pick);
            }
          }

          function wireStrategyDragAndDrop() {
            let dragged = null;
            const rows = document.querySelectorAll('.strategy-row');
            rows.forEach(row => {
              row.addEventListener('dragstart', () => {
                dragged = row;
                row.classList.add('dragging');
              });
              row.addEventListener('dragend', () => {
                row.classList.remove('dragging');
                document.querySelectorAll('.strategy-row').forEach(r => r.classList.remove('drop-target'));
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
                const order = Array.from(parent.querySelectorAll('.strategy-row')).map(el => el.getAttribute('data-strategy-id'));
                await fetch('/api/strategies/order', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ order }) });
                await loadStrategies();
              });
            });
          }

          async function openStrategy(id) {
            currentStrategy = id;
            localStorage.setItem('mc-selected-strategy', id);
            const all = (await (await fetch('/api/strategies')).json()).list || [];
            currentStrategyMeta = all.find(x => x.id === id) || null;
            const res = await fetch('/api/strategy/' + encodeURIComponent(id) + '/md');
            const data = await res.json();
            document.getElementById('strategyPanelTitle').innerText = 'Strategy: ' + (data.name || id);
            document.getElementById('strategyMarkdown').value = data.markdown || '';
            document.getElementById('strategyEmoji').value = (currentStrategyMeta && currentStrategyMeta.emoji) ? currentStrategyMeta.emoji : '🧠';
            const btn = document.getElementById('archiveStrategyBtn');
            if (btn) btn.innerText = (currentStrategyMeta && currentStrategyMeta.archived) ? 'Unarchive' : 'Archive';
          }

          async function saveStrategyMarkdown() {
            if (!currentStrategy) return;
            const markdown = document.getElementById('strategyMarkdown').value;
            const emoji = (document.getElementById('strategyEmoji').value || '🧠').trim();
            await fetch('/api/strategy/' + encodeURIComponent(currentStrategy) + '/meta', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ emoji })
            });
            await fetch('/api/strategy/' + encodeURIComponent(currentStrategy) + '/md', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ markdown })
            });
            await loadStrategies();
            openStrategy(currentStrategy);
          }

          async function toggleArchiveStrategy() {
            if (!currentStrategy) return;
            const archived = !(currentStrategyMeta && currentStrategyMeta.archived);
            await fetch('/api/strategy/' + encodeURIComponent(currentStrategy) + '/archive', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ archived })
            });
            await loadStrategies();
            if (!archived) openStrategy(currentStrategy);
          }

          function deleteStrategy() {
            if (!currentStrategy) return;
            document.getElementById('deleteStrategyText').innerText = 'Delete strategy "' + (currentStrategyMeta?.name || currentStrategy) + '"? This cannot be undone.';
            document.getElementById('deleteStrategyModal').classList.add('visible');
          }

          function hideDeleteStrategyModal() {
            document.getElementById('deleteStrategyModal').classList.remove('visible');
          }

          async function confirmDeleteStrategy() {
            if (!currentStrategy) return;
            await fetch('/api/strategy/' + encodeURIComponent(currentStrategy) + '/delete', { method:'POST' });
            hideDeleteStrategyModal();
            currentStrategy = null; currentStrategyMeta = null;
            await loadStrategies();
          }

          function showCreateStrategyModal() {
            document.getElementById('createStrategyName').value = '';
            document.getElementById('createStrategyEmoji').value = '🧠';
            document.getElementById('createStrategyModal').classList.add('visible');
            setTimeout(() => document.getElementById('createStrategyName').focus(), 50);
          }

          function hideCreateStrategyModal() {
            document.getElementById('createStrategyModal').classList.remove('visible');
          }

          async function confirmCreateStrategy() {
            const name = document.getElementById('createStrategyName').value.trim();
            if (!name) return;
            const emoji = (document.getElementById('createStrategyEmoji').value || '🧠').trim();
            const res = await fetch('/api/strategy/create', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ name, emoji })
            });
            const data = await res.json();
            hideCreateStrategyModal();
            await loadStrategies();
            openStrategy(data.id || name);
          }

          let currentConfigBot = null;
          let botFormBaseline = null;

          function getBotFormSnapshot() {
            return {
              name: document.getElementById('botNameInput')?.value || '',
              emoji: document.getElementById('emojiInput')?.value || '',
              avatar: document.getElementById('avatarInput')?.value || '',
              mode: currentTradingMode || 'paper',
              strategy: document.getElementById('strategySelect')?.value || '',
              config: document.getElementById('configText')?.value || '',
              soul: document.getElementById('soulText')?.value || ''
            };
          }

          function hasUnsavedBotChanges() {
            if (!botFormBaseline) return false;
            return JSON.stringify(botFormBaseline) !== JSON.stringify(getBotFormSnapshot());
          }

          async function openConfig(bot) {
            if (currentConfigBot && bot !== currentConfigBot && hasUnsavedBotChanges()) {
              const proceed = confirm('You have unsaved changes for this bot. Switch anyway and discard them?');
              if (!proceed) return;
            }
            currentConfigBot = bot;
            localStorage.setItem('mc-selected-bot', bot);
            document.getElementById('configPanel').classList.add('visible');
            await loadConfig(bot);
            await loadFiles(bot);
            await loadStrategies();
            botFormBaseline = getBotFormSnapshot();
          }

          async function toggleBot(bot, status) {
            const action = status === 'running' ? 'stop' : 'start';
            await fetch('/api/bot/' + bot + '/' + action, { method:'POST' });
            location.reload();
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
          document.getElementById('home').style.display = activePage === 'home' ? 'block' : 'none';
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

          document.getElementById('createStrategyName')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') confirmCreateStrategy();
          });

        </script>
      </body>
    </html>"""
