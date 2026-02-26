SCRIPTS = r"""<script>
          const saved = localStorage.getItem('mc-theme') || 'dark';
          document.documentElement.dataset.theme = saved === 'light' ? 'light' : 'dark';
          function toggleTheme() {
            const current = document.documentElement.dataset.theme;
            const next = current === 'light' ? 'dark' : 'light';
            document.documentElement.dataset.theme = next;
            localStorage.setItem('mc-theme', next);
          }

          let researchFeed = { items: [] };

          function researchCardHtml(item, idx) {
            const status = item.status || 'new';
            const badge = status === 'investigate' ? '🟡 Investigate' : status === 'discarded' ? '⚪ Discarded' : '🆕 New';
            const confidence = (item.confidence !== undefined && item.confidence !== null) ? ('Confidence: ' + item.confidence) : '';
            const url = item.url ? '<a href="' + item.url + '" target="_blank" rel="noopener">Source</a>' : '';
            return '<div class="config-panel" style="margin-bottom:10px;">'
              + '<div style="display:flex; justify-content:space-between; gap:10px; align-items:center;">'
              + '<div style="font-weight:600;">' + (item.title || 'Untitled strategy') + '</div>'
              + '<div class="bot-col">' + badge + '</div>'
              + '</div>'
              + '<div class="bot-col" style="text-align:left; margin-top:6px;">'
              + (item.synopsis || item.notes || 'No synopsis yet.')
              + '</div>'
              + '<div class="bot-col" style="text-align:left; margin-top:8px;">'
              + (item.source ? ('Source: ' + item.source + ' · ') : '') + confidence + (url ? (' · ' + url) : '')
              + '</div>'
              + '<div style="display:flex; gap:8px; justify-content:flex-end; margin-top:10px;">'
              + '<button class="btn-secondary" onclick="markResearchDiscard(' + idx + ')">Discard</button>'
              + '<button class="btn-primary" onclick="markResearchInvestigate(' + idx + ')">Investigate</button>'
              + '</div>'
              + '</div>';
          }

          function renderResearchFeed() {
            const container = document.getElementById('strategyResearchCards');
            if (!container) return;
            const items = researchFeed.items || [];
            if (!items.length) {
              container.innerHTML = '<div class="bot-col">No strategy leads yet.</div>';
              return;
            }
            container.innerHTML = items.map((x, i) => researchCardHtml(x, i)).join('');
          }

          async function loadResearchFeed() {
            const res = await fetch('/api/strategy-research');
            researchFeed = await res.json();
            researchFeed.items = researchFeed.items || [];
            renderResearchFeed();
          }

          async function saveResearchFeed() {
            await fetch('/api/strategy-research', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(researchFeed)
            });
          }

          async function markResearchDiscard(i) {
            if (!researchFeed.items || !researchFeed.items[i]) return;
            researchFeed.items[i].status = 'discarded';
            await saveResearchFeed();
            renderResearchFeed();
          }

          async function markResearchInvestigate(i) {
            if (!researchFeed.items || !researchFeed.items[i]) return;
            await fetch('/api/strategy-research/investigate', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ index: i })
            });
            await loadResearchFeed();
          }

          async function refreshResearchFeed() {
            await loadResearchFeed();
          }

          let currentResearchReportId = null;

          async function loadResearchReports() {
            const res = await fetch('/api/strategy-research-reports');
            const data = await res.json();
            const items = data.items || [];
            const list = document.getElementById('researchReportsList');
            if (!list) return;
            if (!items.length) {
              list.innerHTML = '<div class="bot-col">No reports yet. Trigger Investigate on a research card first.</div>';
              return;
            }
            list.innerHTML = items.map(r => '<div class="bot-row" onclick="openResearchReport(\'' + r.id.replace(/'/g, "\\'") + '\')"><div class="bot-col bot-name">📄 ' + r.title + '</div></div>').join('');
            const remembered = localStorage.getItem('mc-selected-research-report');
            const ids = items.map(x => x.id);
            const pick = (remembered && ids.includes(remembered)) ? remembered : items[0].id;
            openResearchReport(pick);
          }

          async function openResearchReport(reportId) {
            currentResearchReportId = reportId;
            localStorage.setItem('mc-selected-research-report', reportId);
            const res = await fetch('/api/strategy-research-report/' + encodeURIComponent(reportId));
            const data = await res.json();
            document.getElementById('researchReportTitle').innerText = 'Research Report: ' + reportId;
            document.getElementById('researchReportMarkdown').value = data.markdown || '';
            await loadBacktestResult(reportId);
          }

          async function runBacktestForCurrentReport() {
            if (!currentResearchReportId) return;
            await fetch('/api/backtest/run', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ report_id: currentResearchReportId })
            });
            await loadBacktestResult(currentResearchReportId);
          }

          async function loadBacktestResult(reportId) {
            const res = await fetch('/api/backtest/results?report_id=' + encodeURIComponent(reportId));
            const data = await res.json();
            const el = document.getElementById('researchBacktestResult');
            if (!el) return;
            if (!data.exists) {
              el.value = 'No backtest result yet. Click Run Backtest.';
              return;
            }
            el.value = JSON.stringify(data, null, 2);
          }

          function showConfidenceInfoModal() {
            document.getElementById('confidenceInfoModal').classList.add('visible');
          }

          function hideConfidenceInfoModal() {
            document.getElementById('confidenceInfoModal').classList.remove('visible');
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
          let pendingTradingMode = null;

          function renderTradingModeButtons() {
            const paperBtn = document.getElementById('modePaperBtn');
            const liveBtn = document.getElementById('modeLiveBtn');
            if (paperBtn && liveBtn) {
              paperBtn.className = currentTradingMode === 'paper' ? 'btn-primary' : 'btn-secondary';
              liveBtn.className = currentTradingMode === 'live' ? 'btn-primary' : 'btn-secondary';
            }
          }

          async function setTradingMode(mode, persist=true) {
            const nextMode = mode === 'live' ? 'live' : 'paper';
            if (persist) {
              if (nextMode === currentTradingMode) return;
              pendingTradingMode = nextMode;
              document.getElementById('modeConfirmText').innerText = 'Switch to ' + (nextMode === 'live' ? 'Live Trading' : 'Paper Trading') + '?';
              document.getElementById('modeConfirmModal').classList.add('visible');
              return;
            }
            currentTradingMode = nextMode;
            renderTradingModeButtons();
          }

          function hideModeConfirmModal() {
            pendingTradingMode = null;
            document.getElementById('modeConfirmModal').classList.remove('visible');
          }

          async function confirmTradingModeChange() {
            if (!pendingTradingMode || !currentConfigBot) return;
            currentTradingMode = pendingTradingMode;
            renderTradingModeButtons();
            const res = await fetch('/api/bot/' + currentConfigBot + '/config');
            const cfg = await res.json();
            cfg.trading_mode = currentTradingMode;
            await fetch('/api/bot/' + currentConfigBot + '/config', {
              method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(cfg)
            });
            hideModeConfirmModal();
            await loadConfig(currentConfigBot);
            location.reload();
          }

          async function loadConfig(bot) {
            const res = await fetch('/api/bot/' + bot + '/config');
            const data = await res.json();
            document.getElementById('configText').value = JSON.stringify(data, null, 2);
            document.getElementById('botNameInput').value = data.display_name || bot;
            document.getElementById('emojiInput').value = data.emoji || '';
            document.getElementById('avatarInput').value = data.avatar || '';
            const modeRow = document.getElementById('tradingModeRow');
            if (modeRow) modeRow.style.display = (data.bot_kind === 'utility') ? 'none' : 'block';
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
          document.getElementById('strategy-research').style.display = activePage === 'strategy-research' ? 'block' : 'none';
          document.getElementById('strategy-research-reports').style.display = activePage === 'strategy-research-reports' ? 'block' : 'none';
          document.getElementById('back-testing').style.display = (activePage === 'back-testing' || activePage === 'back-testing-reports') ? 'block' : 'none';
          document.getElementById('readiness').style.display = activePage === 'readiness' ? 'block' : 'none';
          document.getElementById('usage').style.display = activePage === 'usage' ? 'block' : 'none';
          document.getElementById('changelog').style.display = activePage === 'changelog' ? 'block' : 'none';
          document.getElementById('strategies').style.display = activePage === 'strategies' ? 'block' : 'none';

          if (activePage === 'trading-bots' || activePage === 'utility-bots') {
            loadBots();
            loadStrategies();
            setTimeout(wireDragAndDrop, 50);
          }
          if (activePage === 'strategy-research') {
            loadResearchFeed();
          }
          if (activePage === 'strategy-research-reports') {
            loadResearchReports();
          }
          if (activePage === 'usage') {
            loadUsage();
          }
          if (activePage === 'changelog') {
            fetch('/api/changelog').then(r => r.text()).then(t => {
              const el = document.getElementById('changelogText');
              if (el) el.value = t;
            });
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

        </script>"""
