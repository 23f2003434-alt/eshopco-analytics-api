from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import math

app = FastAPI()

# Enable CORS only through FastAPI middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load your personal telemetry file
DATA_FILE = Path(__file__).parent / "q-vercel-latency.json"

with open(DATA_FILE, encoding="utf-8") as f:
    telemetry_data = json.load(f)


class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: float


def percentile95(values):
    values = sorted(values)
    n = len(values)

    if n == 0:
        return 0

    position = (n - 1) * 0.95
    lower = int(position)

    if lower + 1 >= n:
        return values[lower]

    fraction = position - lower
    return values[lower] + fraction * (
        values[lower + 1] - values[lower]
    )


@app.get("/api")
def read_root():
    return {"status": "ok"}


@app.post("/api")
def analyze_latency(request: AnalyticsRequest):
    results = {}

    for region in request.regions:
        rows = [
            row for row in telemetry_data
            if row.get("region") == region
        ]

        if not rows:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0,
            }
            continue

        latencies = [row["latency_ms"] for row in rows]
        uptimes = [row["uptime_pct"] for row in rows]

        results[region] = {
            "avg_latency": round(
                sum(latencies) / len(latencies), 2
            ),
            "p95_latency": round(
                percentile95(latencies), 2
            ),
            "avg_uptime": round(
                sum(uptimes) / len(uptimes), 3
            ),
            "breaches": sum(
                latency > request.threshold_ms
                for latency in latencies
            ),
        }

    return {"regions": results}
