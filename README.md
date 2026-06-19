<h1>
  <img src="static/favicon.svg" width="32" height="32" alt="" style="vertical-align: middle;">
  Latency Test
</h1>

Live‑Überwachung von HTTP‑Latenzen mit Echtzeit‑Diagramm und konfigurierbarer Schwelle.

![Screenshot](screenshots/Screenshot1.png)

## Features

- **Schnelle Abfragen** – bis zu alle 5 ms (einstellbar)
- **Live‑Chart** – scrollendes Diagramm mit Farbkodierung (grün/rot)
- **Übersichtsleiste** – gesamter Datenverlauf mit Auswahl-Zoom
- **Konfigurierbare Schwelle** – Farbumschlag frei einstellbar
- **Statistiken** – Current, Min, Max, Avg, Fehlerquote
- **IP / URL** – direkte Eingabe ohne `http://`

## Starten

```bash
uv run python main.py
```

→ Browser auf [http://localhost:8000](http://localhost:8000) öffnen, Ziel eingeben, **Start** klicken.
