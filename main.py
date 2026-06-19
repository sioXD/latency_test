import asyncio
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).resolve().parent

app = FastAPI(title="Latency Test")
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")


@app.get("/")
async def root():
    return HTMLResponse((HERE / "static" / "index.html").read_text())


async def poll_loop(ws: WebSocket, client: httpx.AsyncClient, target: str, interval_ms: int):
    try:
        while True:
            start = time.monotonic()
            t0 = time.monotonic()
            try:
                resp = await client.get(target, timeout=max(interval_ms / 1000 * 2, 1.0))
                t1 = time.monotonic()
                latency = round((t1 - t0) * 1000, 1)
                await ws.send_json({"t": t0, "latency": latency})
            except Exception as e:
                await ws.send_json({"t": t0, "latency": None, "error": str(e)})

            elapsed = time.monotonic() - start
            sleep_time = max(0, interval_ms / 1000 - elapsed)
            await asyncio.sleep(sleep_time)
    except asyncio.CancelledError:
        pass


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    client = httpx.AsyncClient(timeout=5.0)
    poll_task: asyncio.Task | None = None
    target: str | None = None

    try:
        while True:
            data = await ws.receive_json()
            action = data.get("action")

            if action == "start":
                new_target = data.get("target", "").strip()
                if not new_target:
                    await ws.send_json({"error": "No target URL specified"})
                    continue
                if not new_target.startswith(("http://", "https://")):
                    new_target = "http://" + new_target

                interval_ms = data.get("interval_ms", 10)
                if not isinstance(interval_ms, int) or interval_ms < 1:
                    interval_ms = 10

                if poll_task is not None:
                    poll_task.cancel()
                    poll_task = None

                target = new_target
                poll_task = asyncio.create_task(poll_loop(ws, client, target, interval_ms))
                await ws.send_json({"status": "started", "target": target, "interval_ms": interval_ms})

            elif action == "stop":
                if poll_task is not None:
                    poll_task.cancel()
                    poll_task = None
                await ws.send_json({"status": "stopped"})

            elif action == "ping":
                await ws.send_json({"pong": True})

    except WebSocketDisconnect:
        pass
    finally:
        if poll_task is not None:
            poll_task.cancel()
        await client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
