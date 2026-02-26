STYLES = r"""<style>
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
          .sidebar-header { height: 66px; padding: 0 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
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
          header { height: 66px; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; border-bottom: 1px solid var(--border); background: var(--card-bg); position: sticky; top: 0; z-index: 50; }
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
          #trading-bots .bots-layout { min-height: calc(100vh - 170px); }
          .bot-list-wrap { width: 25%; min-width: 280px; flex: 0 0 25%; }
          .inline-config { flex: 1 1 0; width: auto; min-width: 0; display: none; }
          .inline-config.visible { display: flex; }
          .inline-config .config-panel { flex: 1; display: flex; flex-direction: column; }
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
        </style>"""
