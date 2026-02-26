from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import os
import signal
import subprocess
import time
import shutil
from mission_control.ui.template import DASHBOARD_HTML

BASE = Path(os.getenv("OPENCLAW_WORKSPACE", "/Users/markfiebiger/.openclaw/workspace")).resolve()
MC_DIR = Path(__file__).resolve().parent
AGENTS_ROOT = BASE / "agents"
TRADING_BOTS_DIR = AGENTS_ROOT / "trading"
UTILITY_BOTS_DIR = AGENTS_ROOT / "utility"
STRATEGY_MD_DIR = MC_DIR / "strategies"
STRATEGY_VERSIONS_DIR = STRATEGY_MD_DIR / "versions"
STATE_FILE = MC_DIR / "state.json"
USAGE_FILE = MC_DIR / "usage.json"
STRATEGIES_FILE = MC_DIR / "strategies.json"
BOT_ORDER_FILE = MC_DIR / "bot_order.json"
TEMPLATE_DIR = AGENTS_ROOT / "bot-template"

for d in [AGENTS_ROOT, TRADING_BOTS_DIR, UTILITY_BOTS_DIR, STRATEGY_MD_DIR, STRATEGY_VERSIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

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


def strategy_slug(name: str) -> str:
    s = ''.join(ch.lower() if ch.isalnum() else '_' for ch in str(name).strip())
    while '__' in s:
        s = s.replace('__', '_')
    return s.strip('_')


def normalize_strategies(data: dict) -> dict:
    lst = data.get("list", []) if isinstance(data, dict) else []
    out = []
    for item in lst:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            sid = str(item.get("id", "")).strip() or strategy_slug(name)
            archived = bool(item.get("archived", False))
            emoji = str(item.get("emoji", "🧠")).strip() or "🧠"
        else:
            name = str(item).strip()
            sid = strategy_slug(name)
            archived = False
            emoji = "🧠"
        if not name or not sid:
            continue
        out.append({"id": sid, "name": name, "archived": archived, "emoji": emoji})
    # dedupe by id preserving order
    seen = set(); dedup=[]
    for x in out:
        if x['id'] in seen: continue
        seen.add(x['id']); dedup.append(x)
    return {"list": dedup}


def load_strategies():
    if STRATEGIES_FILE.exists():
        try:
            return normalize_strategies(json.loads(STRATEGIES_FILE.read_text()))
        except Exception:
            pass
    return {"list": []}


def save_strategies(data):
    norm = normalize_strategies(data if isinstance(data, dict) else {})
    STRATEGIES_FILE.write_text(json.dumps(norm, indent=2))
    for item in norm.get("list", []):
        sid = item["id"]
        title = item["name"]
        p = STRATEGY_MD_DIR / f"{sid}.md"
        if not p.exists():
            p.write_text(f"# {title}\n\nDescribe this strategy here.\n")


def bot_dir(name: str):
    for base in [TRADING_BOTS_DIR, UTILITY_BOTS_DIR, AGENTS_ROOT]:
        d = base / name
        if d.exists() and d.is_dir():
            return d
    return None


def list_bots():
    bots = []
    for base in [TRADING_BOTS_DIR, UTILITY_BOTS_DIR]:
        if not base.exists():
            continue
        for d in base.iterdir():
            if d.is_dir():
                bot_py = d / "bot.py"
                if bot_py.exists():
                    bots.append(d.name)
    return sorted(set(bots))


def bot_kind(name: str) -> str:
    d = bot_dir(name)
    if d and d.parent == UTILITY_BOTS_DIR:
        return "utility"
    cfg = (d / "config.json") if d else None
    if cfg and cfg.exists():
        try:
            data = json.loads(cfg.read_text())
            kind = str(data.get("bot_kind") or data.get("type") or data.get("category") or "").lower()
            if kind == "utility":
                return "utility"
        except Exception:
            pass
    return "trading"


def bot_profile(name: str) -> dict:
    d = bot_dir(name)
    cfg = (d / "config.json") if d else None
    if cfg and cfg.exists():
        try:
            data = json.loads(cfg.read_text())
            return {
                "emoji": data.get("emoji", "🤖"),
                "avatar": data.get("avatar", ""),
                "display_name": data.get("display_name", name.replace('_', ' ').title()),
                "trading_mode": data.get("trading_mode", "paper"),
            }
        except Exception:
            pass
    return {"emoji": "🤖", "avatar": "", "display_name": name.replace('_', ' ').title(), "trading_mode": "paper"}


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
    return {"status": "stopped", "pid": bot_state.get("last_pid")}


def render_dashboard(active_page="trading-bots"):
    bots = apply_bot_order(list_bots())
    trading_rows = []
    utility_rows = []
    for b in bots:
        status = bot_status(b)
        profile = bot_profile(b)
        badge_class = "badge-live" if status['status'] == "running" else "badge-idle"
        avatar_html = f"<img src='{profile['avatar']}' class='bot-avatar' />" if profile.get('avatar') else f"<span class='bot-emoji'>{profile.get('emoji') or '🤖'}</span>"
        mode_badge = "🟢 Live" if profile.get('trading_mode') == 'live' else "📝 Paper"
        toggle_label = "Stop" if status['status'] == "running" else "Start"
        toggle_class = "btn-danger" if status['status'] == "running" else "btn-success"
        row_html = f"""
        <div class="bot-row" draggable="true" data-bot="{b}" onclick="openConfig('{b}')">
          <div class="bot-col bot-name">{avatar_html} {profile.get('display_name', b)}</div>
          <div class="bot-col"><span class="card-badge {badge_class}">{status['status']}</span></div>
          <div class="bot-col">{mode_badge}</div>
          <div class="bot-col actions" onclick="event.stopPropagation()">
            <button class="{toggle_class}" onclick="toggleBot('{b}','{status['status']}')">{toggle_label}</button>
          </div>
        </div>
        """
        if bot_kind(b) == "utility":
            utility_rows.append(row_html)
        else:
            trading_rows.append(row_html)

    utility_html = "".join(utility_rows) if utility_rows else '<div class="bot-col">No utility bots yet.</div>'
    html = DASHBOARD_HTML
    html = html.replace("{{TRADING_ROWS}}", "".join(trading_rows))
    html = html.replace("{{UTILITY_ROWS}}", utility_html)
    html = html.replace("{{ACTIVE_PAGE}}", active_page)
    return HTMLResponse(html)



@app.get("/", response_class=HTMLResponse)
def home():
    return render_dashboard("home")


@app.get("/trading-bots", response_class=HTMLResponse)
def trading_bots_page():
    return render_dashboard("trading-bots")


@app.get("/utility-bots", response_class=HTMLResponse)
def utility_bots_page():
    return render_dashboard("utility-bots")


@app.get("/back-testing", response_class=HTMLResponse)
def back_testing_page():
    return render_dashboard("back-testing")


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

    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot folder not found")
    bot_py = d / "bot.py"
    if not bot_py.exists():
        raise HTTPException(404, "bot.py not found")

    proc = subprocess.Popen(["python3", str(bot_py)], cwd=str(d))

    state = load_state()
    state.setdefault("bots", {})[name] = {"pid": proc.pid, "last_pid": proc.pid, "started_at": int(time.time())}
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

    bot_state["last_pid"] = pid
    bot_state["pid"] = None
    state.setdefault("bots", {})[name] = bot_state
    save_state(state)
    return {"ok": True}


@app.get("/api/bot/{name}/config")
def api_bot_config(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot not found")
    cfg = d / "config.json"
    if not cfg.exists():
        return {}
    return JSONResponse(json.loads(cfg.read_text()))


@app.post("/api/bot/{name}/config")
def api_bot_config_save(name: str, payload: dict):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot not found")
    cfg = d / "config.json"
    cfg.write_text(json.dumps(payload, indent=2))
    return {"ok": True}


@app.get("/api/bot/{name}/files")
def api_bot_files(name: str):
    if name not in list_bots():
        raise HTTPException(404, "Bot not found")
    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot not found")
    base = d
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
    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot not found")
    base = d
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


@app.post("/api/strategies/order")
def api_strategies_order(payload: dict):
    order = payload.get("order", [])
    if not isinstance(order, list):
        raise HTTPException(400, "order must be list")
    data = load_strategies()
    items = data.get("list", [])
    by_id = {x.get("id"): x for x in items if isinstance(x, dict) and x.get("id")}
    reordered = [by_id[sid] for sid in order if sid in by_id]
    for x in items:
        sid = x.get("id") if isinstance(x, dict) else None
        if sid and sid not in order:
            reordered.append(x)
    save_strategies({"list": reordered})
    return {"ok": True}


@app.post("/api/strategy/create")
def api_strategy_create(payload: dict):
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(400, "Name required")
    sid = strategy_slug(name)
    emoji = str(payload.get("emoji", "🧠")).strip() or "🧠"
    data = load_strategies()
    lst = data.get("list", [])
    if not any(x.get("id") == sid for x in lst):
        lst.append({"id": sid, "name": name, "emoji": emoji, "archived": False})
    save_strategies({"list": lst})
    return {"ok": True, "name": name, "id": sid}


@app.get("/api/strategy/{sid}/md")
def api_strategy_md(sid: str):
    safe = strategy_slug(sid)
    data = load_strategies()
    display = next((x.get("name") for x in data.get("list", []) if x.get("id") == safe), safe)
    p = STRATEGY_MD_DIR / f"{safe}.md"
    if not p.exists():
        p.write_text(f"# {display}\n\nDescribe this strategy here.\n")
    return {"id": safe, "name": display, "markdown": p.read_text()}


@app.post("/api/strategy/{sid}/md")
def api_strategy_md_save(sid: str, payload: dict):
    safe = strategy_slug(sid)
    p = STRATEGY_MD_DIR / f"{safe}.md"
    new_md = str(payload.get("markdown", ""))
    old_md = p.read_text() if p.exists() else ""
    if old_md != new_md and p.exists():
        vdir = STRATEGY_VERSIONS_DIR / safe
        vdir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        (vdir / f"{ts}.md").write_text(old_md)
    p.write_text(new_md)
    return {"ok": True}


@app.post("/api/strategy/{sid}/archive")
def api_strategy_archive(sid: str, payload: dict):
    safe = strategy_slug(sid)
    archived = bool(payload.get("archived", True))
    data = load_strategies()
    changed = False
    for item in data.get("list", []):
        if item.get("id") == safe:
            item["archived"] = archived
            changed = True
            break
    if not changed:
        raise HTTPException(404, "Strategy not found")
    save_strategies(data)
    return {"ok": True}


@app.post("/api/strategy/{sid}/meta")
def api_strategy_meta(sid: str, payload: dict):
    safe = strategy_slug(sid)
    data = load_strategies()
    changed = False
    for item in data.get("list", []):
        if item.get("id") == safe:
            if "emoji" in payload:
                item["emoji"] = str(payload.get("emoji") or "🧠")
            if "name" in payload and str(payload.get("name","")).strip():
                item["name"] = str(payload.get("name")).strip()
            changed = True
            break
    if not changed:
        raise HTTPException(404, "Strategy not found")
    save_strategies(data)
    return {"ok": True}


@app.post("/api/strategy/{sid}/delete")
def api_strategy_delete(sid: str):
    safe = strategy_slug(sid)
    data = load_strategies()
    data["list"] = [x for x in data.get("list", []) if x.get("id") != safe]
    save_strategies(data)
    p = STRATEGY_MD_DIR / f"{safe}.md"
    if p.exists():
        p.unlink()
    return {"ok": True}


@app.post("/api/bot/create")
def api_bot_create(payload: dict):
    raw_name = str(payload.get("name", "")).strip()
    if not raw_name:
        raise HTTPException(400, "Name required")
    name = strategy_slug(raw_name)
    kind = str(payload.get("bot_kind", "trading")).lower()
    parent = UTILITY_BOTS_DIR if kind == "utility" else TRADING_BOTS_DIR
    target = parent / name
    if target.exists() or bot_dir(name):
        raise HTTPException(400, "Bot already exists")
    if TEMPLATE_DIR.exists():
        shutil.copytree(TEMPLATE_DIR, target)
        if not (target / "bot.py").exists():
            (target / "bot.py").write_text("#!/usr/bin/env python3\nprint('Bot runner not implemented yet')\n")
    else:
        target.mkdir(parents=True)
        (target / "bot.py").write_text("#!/usr/bin/env python3\nprint('Bot runner not implemented yet')\n")
        (target / "config.json").write_text(json.dumps({}, indent=2))
    cfg_path = target / "config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg["bot_kind"] = "utility" if kind == "utility" else "trading"
    cfg["display_name"] = raw_name
    cfg.setdefault("trading_mode", "paper")
    cfg_path.write_text(json.dumps(cfg, indent=2))
    return {"ok": True, "name": name, "display_name": raw_name}


@app.post("/api/bot/{name}/rename")
def api_bot_rename(name: str, payload: dict):
    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot not found")
    new_raw = str(payload.get("new_name", "")).strip()
    if not new_raw:
        raise HTTPException(400, "new_name required")
    new_slug = strategy_slug(new_raw)
    if not new_slug:
        raise HTTPException(400, "invalid new_name")
    if new_slug != name and bot_dir(new_slug):
        raise HTTPException(400, "Bot name already exists")

    parent = d.parent
    new_dir = parent / new_slug
    if new_slug != name:
        d.rename(new_dir)
    else:
        new_dir = d

    cfg_path = new_dir / "config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg["display_name"] = new_raw
    cfg_path.write_text(json.dumps(cfg, indent=2))

    state = load_state()
    if "bots" in state and name in state["bots"] and new_slug != name:
        state["bots"][new_slug] = state["bots"].pop(name)
        save_state(state)

    order = load_bot_order()
    order = [new_slug if x == name else x for x in order]
    save_bot_order(order)
    return {"ok": True, "name": new_slug, "display_name": new_raw}


@app.post("/api/bot/{name}/delete")
def api_bot_delete(name: str):
    if name == "bot-template":
        raise HTTPException(400, "Cannot delete template")
    target = bot_dir(name)
    if not target or not target.exists() or not target.is_dir():
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
