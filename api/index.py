from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

app = FastAPI()

# CORS: allow requests from any origin.
# FastAPI middleware is the only place handling CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

# Telemetry records: (region, latency_ms, uptime_pct)
DATA = [
    ("apac", 115.35, 98.491),
    ("apac", 184.66, 99.283),
    ("apac", 117.78, 99.303),
    ("apac", 134.42, 98.426),
    ("apac", 220.38, 98.346),
    ("apac", 168.04, 98.223),
    ("apac", 205.86, 98.845),
    ("apac", 210.74, 98.486),
    ("apac", 180.56, 97.518),
    ("apac", 228.40, 97.323),
    ("apac", 216.04, 98.719),
    ("apac", 155.29, 97.413),

    ("emea", 181.75, 99.039),
    ("emea", 181.60, 98.568),
    ("emea", 126.41, 98.121),
    ("emea", 218.43, 97.804),
    ("emea", 217.02, 97.154),
    ("emea", 218.39, 98.085),
    ("emea", 153.71, 98.244),
    ("emea", 133.04, 97.223),
    ("emea", 201.29, 98.422),
    ("emea", 124.71, 98.121),
    ("emea", 123.06, 98.304),
    ("emea", 179.95, 98.456),

    ("amer", 103.32, 98.359),
    ("amer", 210.41, 97.356),
    ("amer", 125.16, 97.813),
    ("amer", 176.70, 98.981),
    ("amer", 104.18, 97.369),
    ("amer", 136.98, 98.682),
    ("amer", 136.00, 97.107),
    ("amer", 174.73, 98.664),
    ("amer", 119.56, 97.813),
    ("amer", 120.72, 97.881),
    ("amer", 129.63, 98.793),
    ("amer", 139.88, 98.568),
]


class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: float


def percentile95(values: list[float]) -> float:
    """Calculate the 95th percentile using linear interpolation."""
    values = sorted(values)
    position = 0.95 * (len(values) - 1)

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return values[lower]

    return (
        values[lower]
        + (values[upper] - values[lower]) * (position - lower)
    )


@app.post("/")
def analytics(request: AnalyticsRequest):
    results = []

    for region in request.regions:
        records = [
            row for row in DATA
            if row[0] == region
        ]

        if not records:
            continue

        latencies = [row[1] for row in records]
        uptimes = [row[2] for row in records]

        results.append({
            "region": region,
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
        })

    return {"results": results}
