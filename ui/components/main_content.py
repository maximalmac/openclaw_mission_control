MAIN_CONTENT = r"""<main>
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

            <section id="back-testing" class="section" style="margin-top:24px;">
              <div class="section-header" style="margin-bottom:16px;">
                <div class="section-title">Back-Testing Reports</div>
              </div>
              <div class="config-panel">
                <div class="bot-col">Back-testing tools are coming next (dataset selection, strategy replay, and performance reports).</div>
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
          </main>"""
