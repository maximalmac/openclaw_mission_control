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
STRATEGY_MD_DIR = BASE / "strategies"
STATE_FILE = MC_DIR / "state.json"
USAGE_FILE = MC_DIR / "usage.json"
STRATEGIES_FILE = MC_DIR / "strategies.json"
BOT_ORDER_FILE = MC_DIR / "bot_order.json"
TEMPLATE_DIR = AGENTS_ROOT / "bot-template"

for d in [AGENTS_ROOT, TRADING_BOTS_DIR, UTILITY_BOTS_DIR, STRATEGY_MD_DIR]:
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


def load_strategies():
    if STRATEGIES_FILE.exists():
        return json.loads(STRATEGIES_FILE.read_text())
    return {"list": []}


def save_strategies(data):
    STRATEGIES_FILE.write_text(json.dumps(data, indent=2))
    names = data.get("list", []) if isinstance(data, dict) else []
    for n in names:
        safe = str(n).strip().replace("/", "-")
        if not safe:
            continue
        p = STRATEGY_MD_DIR / f"{safe}.md"
        if not p.exists():
            p.write_text(f"# {safe}\n\nDescribe this strategy here.\n")


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
        <div class="bot-row" draggable="true" data-bot="{b}" onclick="openConfig('{b}')">
          <div class="bot-col bot-name">{avatar_html} {b}</div>
          <div class="bot-col"><span class="card-badge {badge_class}">{status['status']}</span></div>
          <div class="bot-col">PID: {status['pid'] or '-'}</div>
          <div class="bot-col actions" onclick="event.stopPropagation()">
            <button class="btn-primary" onclick="fetch('/api/bot/{b}/start',{{method:'POST'}}).then(()=>location.reload())">Start</button>
            <button class="btn-secondary" onclick="fetch('/api/bot/{b}/stop',{{method:'POST'}}).then(()=>location.reload())">Stop</button>
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

    d = bot_dir(name)
    if not d:
        raise HTTPException(404, "Bot folder not found")
    bot_py = d / "bot.py"
    if not bot_py.exists():
        raise HTTPException(404, "bot.py not found")

    proc = subprocess.Popen(["python3", str(bot_py)], cwd=str(d))

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


@app.post("/api/bot/create")
def api_bot_create(payload: dict):
    name = payload.get("name", "").strip()
    if not name:
        raise HTTPException(400, "Name required")
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
    cfg_path.write_text(json.dumps(cfg, indent=2))
    return {"ok": True, "name": name}


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
