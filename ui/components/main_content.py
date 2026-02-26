MAIN_CONTENT = r"""<main>
            <section id="home" class="section">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Dashboard</div>
              </div>
              <div class="bot-list" style="gap:16px;">
                <div class="config-panel">
                  <div class="section-title" style="margin-bottom:8px;">Mission Control Overview</div>
                  <div class="bot-col" style="text-align:left; line-height:1.6;">
                    <strong>What is already in place</strong><br/>
                    • Python bot management UI (Trading + Utility bots)<br/>
                    • Start/Stop bot controls and live/paper mode toggles<br/>
                    • Per-bot config + SOUL editing, with unsaved-change warnings<br/>
                    • Strategy manager (create/edit/archive/delete/reorder)<br/>
                    • Strategy markdown version snapshots and changelog tracking<br/>
                    • Back-Testing and Reports navigation scaffolding
                  </div>
                </div>
                <div class="config-panel">
                  <div class="section-title" style="margin-bottom:8px;">To reach full automation</div>
                  <div class="bot-col" style="text-align:left; line-height:1.6;">
                    • Standard bot runtime contract (health/status/signal/state)<br/>
                    • Strategy → Python code generator pipeline<br/>
                    • Reliable market data + indicator pipeline with freshness checks<br/>
                    • Order execution engine with retries/idempotency/partial-fill handling<br/>
                    • Risk engine (size caps, kill switches, daily loss limits)<br/>
                    • GPT confluence gate (ALLOW/BLOCK/REDUCE_SIZE with fallback)<br/>
                    • Backtesting, walk-forward, and reporting workflows<br/>
                    • Exchange reconciliation and alerting/diagnostics
                  </div>
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
                    <div class="config-row" id="tradingModeRow" style="flex:0;">
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
                    <div class="config-row" style="flex:1; min-height:0;">
                      <div style="flex:1; min-height:0; display:flex; flex-direction:column;">
                        <label>SOUL.md</label>
                        <textarea id="soulText" style="flex:1; min-height:220px;"></textarea>
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

            <section id="strategy-research" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div class="section-title">Strategy Research Feed</div>
                <div style="display:flex; gap:8px; align-items:center;">
                  <button class="btn-secondary" onclick="showConfidenceInfoModal()">Confidence Model</button>
                  <button class="btn-primary" onclick="refreshResearchFeed()">Refresh</button>
                </div>
              </div>
              <div class="config-panel" style="min-height:70vh;">
                <div id="strategyResearchCards" class="bot-list" style="gap:12px;"></div>
              </div>
            </section>

            <section id="strategy-research-reports" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Strategy Research Reports</div>
              </div>
              <div class="bots-layout" style="align-items: stretch; min-height: 70vh;">
                <div class="bot-list-wrap">
                  <div class="bot-list" id="researchReportsList"></div>
                </div>
                <div class="inline-config visible full-height-card" style="flex:1;" id="researchReportPanel">
                  <div class="config-panel">
                    <div class="inline-config-header">
                      <div class="section-title" id="researchReportTitle">Research Report</div>
                    </div>
                    <div class="config-row" style="flex:0;">
                      <div style="flex:1; display:flex; gap:8px; justify-content:flex-end;">
                        <button class="btn-primary" onclick="runBacktestForCurrentReport()">Run Backtest</button>
                      </div>
                    </div>
                    <div class="config-row" style="flex:1; min-height:0;">
                      <div style="flex:1; min-height:0; display:flex; flex-direction:column;">
                        <label>Report</label>
                        <textarea id="researchReportMarkdown" readonly style="flex:1; min-height:260px;"></textarea>
                      </div>
                    </div>
                    <div class="config-row" style="flex:0;">
                      <div style="flex:1; min-height:0; display:flex; flex-direction:column;">
                        <label>Backtest Result</label>
                        <textarea id="researchBacktestResult" readonly style="min-height:180px;"></textarea>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section id="back-testing" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Back-Testing Reports</div>
              </div>
              <div class="config-panel">
                <div class="bot-col">Back-testing tools are coming next (dataset selection, strategy replay, and performance reports).</div>
              </div>
            </section>

            <section id="readiness" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Production Readiness Checklist</div>
              </div>
              <div class="config-panel">
                <div class="bot-list" style="gap:10px;">
                  <div class="bot-row"><div class="bot-col bot-name">🧩 Bot Runtime Contract</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Standard status/health/signal interface</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🧠 Strategy → Code Generator</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Parse strategy markdown into runnable Python</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">📡 Market Data Pipeline</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Candles/funding/mark-index with freshness checks</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🛒 Execution Engine</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Idempotent orders, retries, partial-fill handling</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🛡️ Risk Engine</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Hard caps, max daily loss, kill switches</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🤖 GPT Confluence Gate</div><div class="bot-col">⬜ Pending</div><div class="bot-col">ALLOW/BLOCK/REDUCE_SIZE decision with fallback</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🧪 Backtesting + Walk-forward</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Cost-aware validation before paper/live</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🗃️ Trade State DB + Reports</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Orders/fills/positions/equity with reporting</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🔄 Exchange Reconciliation</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Auto-detect and resolve local vs exchange drift</div><div class="bot-col"></div></div>
                  <div class="bot-row"><div class="bot-col bot-name">🚨 Alerting + Diagnostics</div><div class="bot-col">⬜ Pending</div><div class="bot-col">Notify on failures, stalled bots, risk breaches</div><div class="bot-col"></div></div>
                </div>
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

            <section id="changelog" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Changelog</div>
              </div>
              <div class="config-panel">
                <div class="config-row" style="margin-bottom:0;">
                  <div style="flex:1; min-height:0; display:flex; flex-direction:column;">
                    <label>CHANGELOG.md</label>
                    <textarea id="changelogText" readonly style="min-height:60vh;"></textarea>
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
          </main>"""
