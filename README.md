# Mission Control

Run locally (Tailscale access on port 7777):

```bash
python3 -m pip install fastapi uvicorn
python3 -m uvicorn mission_control.app:app --host 0.0.0.0 --port 7777
```

Open:
https://marks-mac-mini.tail1751ee.ts.net:7777/
