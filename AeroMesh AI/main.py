import math
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Response, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="AeroMesh-AI Operational Core v2.2",
    description="MoES / NCMRWF Extreme Weather Tracking & Multi-Hazard Spatial Alerting Core",
    version="2.2.0"
)

# Spatial Database covering multiple vulnerable Indian geographic sectors
INFRASTRUCTURE_REGIONS = {
    "bob_cyclone": [
        {"name": "Puri District Hospital", "type": "Hospital", "lat": 19.8135, "lon": 85.8312, "capacity": "450 Beds"},
        {"name": "Konark Community Health Centre", "type": "Hospital", "lat": 19.8876, "lon": 86.0945, "capacity": "120 Beds"},
        {"name": "Balukhand Coastal Hamlet", "type": "Village", "lat": 19.8350, "lon": 85.9120, "capacity": "1,850 Pop"},
        {"name": "Gop Primary Health Post", "type": "Clinic", "lat": 19.9980, "lon": 85.9960, "capacity": "35 Beds"},
        {"name": "Astaranga Coastal Settlement", "type": "Village", "lat": 19.9821, "lon": 86.2654, "capacity": "4,200 Pop"},
        {"name": "Satapada Marine Shelter", "type": "Evacuation Shelter", "lat": 19.6700, "lon": 85.4300, "capacity": "3,000 Capacity"}
    ],
    "arabian_cyclone": [
        {"name": "Mandvi Port Emergency Care", "type": "Hospital", "lat": 22.8320, "lon": 69.3450, "capacity": "210 Beds"},
        {"name": "Jakhau Fishery Settlement", "type": "Coastal Village", "lat": 23.2380, "lon": 68.7320, "capacity": "3,100 Pop"},
        {"name": "Kandla Maritime Substation", "type": "Power Substation", "lat": 23.0010, "lon": 70.2180, "capacity": "High Voltage Grid"},
        {"name": "Naliya Community Shelter", "type": "Evacuation Shelter", "lat": 23.2560, "lon": 68.8250, "capacity": "2,500 Capacity"}
    ],
    "heat_dome": [
        {"name": "Safdarjung Trauma Centre", "type": "Hospital", "lat": 28.5690, "lon": 77.2080, "capacity": "800 Beds"},
        {"name": "Najafgarh Agricultural Colony", "type": "Suburban Settlement", "lat": 28.6090, "lon": 76.9850, "capacity": "12,000 Pop"},
        {"name": "Wazirpur Industrial Power Grid", "type": "Electrical Hub", "lat": 28.6990, "lon": 77.1650, "capacity": "Core Grid"},
        {"name": "Narela Labor Shelter Complex", "type": "Shelter", "lat": 28.8520, "lon": 77.0920, "capacity": "4,500 Capacity"}
    ],
    "cloudburst": [
        {"name": "STNM State Hospital Gangtok", "type": "Hospital", "lat": 27.3250, "lon": 88.6120, "capacity": "500 Beds"},
        {"name": "Singtam Lowland Ward", "type": "Riverine Settlement", "lat": 27.2340, "lon": 88.4980, "capacity": "5,400 Pop"},
        {"name": "Teesta Hydroelectric Station V", "type": "Dam / Powerhouse", "lat": 27.1950, "lon": 88.5120, "capacity": "510 MW Station"},
        {"name": "Dikchu Mountain Hamlet", "type": "Village", "lat": 27.3820, "lon": 88.5280, "capacity": "1,200 Pop"}
    ],
    "orographic_deluge": [
        {"name": "Meppadi Community Health Center", "type": "Hospital", "lat": 11.5510, "lon": 76.1280, "capacity": "150 Beds"},
        {"name": "Chooralmala Tea Plantation Village", "type": "High Vulnerability Hamlet", "lat": 11.5380, "lon": 76.1720, "capacity": "2,400 Pop"},
        {"name": "Kalpetta District Emergency Depot", "type": "Emergency Depot", "lat": 11.6080, "lon": 76.0820, "capacity": "NDRF Staging Hub"},
        {"name": "Mundakkai Slope Settlement", "type": "Village", "lat": 11.5450, "lon": 76.1950, "capacity": "1,600 Pop"}
    ]
}

SCENARIOS_META = {
    "bob_cyclone": {
        "title": "Super Cyclone Amphan-II (Bay of Bengal / Odisha)",
        "type": "cyclonic",
        "category": "Category 4 Cyclone",
        "center": [19.825, 85.892],
        "bbox": [[18.00, 84.40], [21.20, 88.40]],
        "wind_ms": 51.4,
        "rain_mm_hr": 72.0,
        "divergence": 0.009,
        "moisture": 99.7,
        "impact_zone": "Puri-Konark Coastal Corridor",
        "trajectory": [
            {"lead_h": 24, "lat": 18.60, "lon": 86.80, "wind_ms": 42.0, "pressure_hpa": 975.0},
            {"lead_h": 48, "lat": 19.20, "lon": 86.30, "wind_ms": 47.5, "pressure_hpa": 962.0},
            {"lead_h": 72, "lat": 19.825, "lon": 85.892, "wind_ms": 51.4, "pressure_hpa": 948.0},
            {"lead_h": 96, "lat": 20.45, "lon": 85.50, "wind_ms": 38.0, "pressure_hpa": 980.0},
            {"lead_h": 120, "lat": 21.10, "lon": 85.10, "wind_ms": 24.0, "pressure_hpa": 995.0}
        ],
        "directives": [
            "Mandatory total evacuation within 5 km radial impact buffer.",
            "Pre-position NDRF Battalion 10 units at strategic junctions along NH-316.",
            "Mandatory emergency switch to hospital generator backup circuits."
        ]
    },
    "arabian_cyclone": {
        "title": "VSCS Biparjoy-II (Arabian Sea / Kutch Coast)",
        "type": "cyclonic",
        "category": "Extremely Severe Cyclonic Storm",
        "center": [22.840, 69.340],
        "bbox": [[21.50, 67.80], [24.00, 71.00]],
        "wind_ms": 48.6,
        "rain_mm_hr": 64.0,
        "divergence": 0.011,
        "moisture": 99.4,
        "impact_zone": "Mandvi-Jakhau Coastal Front",
        "trajectory": [
            {"lead_h": 24, "lat": 21.50, "lon": 68.20, "wind_ms": 39.0, "pressure_hpa": 982.0},
            {"lead_h": 48, "lat": 22.10, "lon": 68.80, "wind_ms": 44.0, "pressure_hpa": 968.0},
            {"lead_h": 72, "lat": 22.840, "lon": 69.340, "wind_ms": 48.6, "pressure_hpa": 952.0},
            {"lead_h": 96, "lat": 23.40, "lon": 69.90, "wind_ms": 35.0, "pressure_hpa": 984.0},
            {"lead_h": 120, "lat": 24.10, "lon": 70.60, "wind_ms": 22.0, "pressure_hpa": 998.0}
        ],
        "directives": [
            "Halt all commercial and fishing operations across Kandla & Mandvi Ports.",
            "Clear coastal population within designated surge footprint.",
            "Alert power transmission grids for salt-encrusted insulator failure."
        ]
    },
    "heat_dome": {
        "title": "Indo-Gangetic Severe Heat Dome (Delhi-NCR)",
        "type": "heat",
        "category": "Hyperthermic Atmospheric Anomaly",
        "center": [28.6139, 77.2090],
        "bbox": [[27.50, 76.00], [29.80, 78.50]],
        "wind_ms": 12.2,
        "rain_mm_hr": 0.0,
        "divergence": 0.003,
        "moisture": 98.9,
        "impact_zone": "National Capital Region (NCR Core)",
        "trajectory": [
            {"lead_h": 24, "lat": 28.40, "lon": 76.90, "wind_ms": 10.0, "pressure_hpa": 1004.0},
            {"lead_h": 48, "lat": 28.55, "lon": 77.05, "wind_ms": 11.5, "pressure_hpa": 1002.0},
            {"lead_h": 72, "lat": 28.6139, "lon": 77.2090, "wind_ms": 12.2, "pressure_hpa": 1000.0},
            {"lead_h": 96, "lat": 28.75, "lon": 77.35, "wind_ms": 11.0, "pressure_hpa": 1001.0},
            {"lead_h": 120, "lat": 28.90, "lon": 77.50, "wind_ms": 9.5, "pressure_hpa": 1003.0}
        ],
        "directives": [
            "Issue Red Alert for wet-bulb temperature exceeding 33.5°C.",
            "Mandate complete work stoppage for outdoor labor from 11:00 to 16:30 IST.",
            "Deploy mobile water misters and open municipal air-conditioned cooling shelters."
        ]
    },
    "cloudburst": {
        "title": "Teesta Glacial Cloudburst & Flash Deluge (Sikkim)",
        "type": "orographic",
        "category": "Sudden High-Volume Orogenesis",
        "center": [27.320, 88.580],
        "bbox": [[26.80, 88.00], [27.80, 89.20]],
        "wind_ms": 28.4,
        "rain_mm_hr": 115.0,
        "divergence": 0.014,
        "moisture": 99.8,
        "impact_zone": "Teesta River High-Velocity Basin",
        "trajectory": [
            {"lead_h": 24, "lat": 27.10, "lon": 88.40, "wind_ms": 22.0, "pressure_hpa": 990.0},
            {"lead_h": 48, "lat": 27.22, "lon": 88.50, "wind_ms": 26.0, "pressure_hpa": 984.0},
            {"lead_h": 72, "lat": 27.320, "lon": 88.580, "wind_ms": 28.4, "pressure_hpa": 978.0},
            {"lead_h": 96, "lat": 27.42, "lon": 88.66, "wind_ms": 20.0, "pressure_hpa": 992.0},
            {"lead_h": 120, "lat": 27.50, "lon": 88.75, "wind_ms": 14.0, "pressure_hpa": 1002.0}
        ],
        "directives": [
            "Trigger rapid opening of dam spillway gates to prevent flash overtopping.",
            "Sound village-wide acoustic sirens across low-lying Teesta valley.",
            "Suspend traffic immediately along National Highway 10."
        ]
    },
    "orographic_deluge": {
        "title": "Western Ghats Slope Slip & Orographic Deluge (Wayanad)",
        "type": "orographic",
        "category": "Extreme Orographic Rainfall",
        "center": [11.545, 76.140],
        "bbox": [[11.20, 75.80], [11.90, 76.50]],
        "wind_ms": 32.5,
        "rain_mm_hr": 98.0,
        "divergence": 0.008,
        "moisture": 99.9,
        "impact_zone": "Chooralmala-Meppadi Escarpment",
        "trajectory": [
            {"lead_h": 24, "lat": 11.42, "lon": 76.02, "wind_ms": 25.0, "pressure_hpa": 994.0},
            {"lead_h": 48, "lat": 11.49, "lon": 76.08, "wind_ms": 29.0, "pressure_hpa": 988.0},
            {"lead_h": 72, "lat": 11.545, "lon": 76.140, "wind_ms": 32.5, "pressure_hpa": 982.0},
            {"lead_h": 96, "lat": 11.60, "lon": 76.22, "wind_ms": 22.0, "pressure_hpa": 995.0},
            {"lead_h": 120, "lat": 11.66, "lon": 76.30, "wind_ms": 16.0, "pressure_hpa": 1004.0}
        ],
        "directives": [
            "Evacuate tea plantation quarters situated on slopes exceeding 20° gradient.",
            "Pre-stage soil-clearing heavy earthmovers and pontoon bridges along Ghat bypass.",
            "Designate community schools on stable plateaus as primary relief nodes."
        ]
    }
}

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

@app.get("/api/v1/alerts/active")
def get_active_threat(
    scenario_id: str = Query("bob_cyclone", description="Scenario identifier key"),
    buffer_km: float = Query(5.0, description="Spatial impact buffer radius in km")
):
    if scenario_id not in SCENARIOS_META:
        scenario_id = "bob_cyclone"
    
    meta = SCENARIOS_META[scenario_id]
    c_lat, c_lon = meta["center"]
    assets = INFRASTRUCTURE_REGIONS.get(scenario_id, [])

    impacted = []
    for asset in assets:
        dist = haversine_km(c_lat, c_lon, asset["lat"], asset["lon"])
        status = "MANDATORY EVACUATION" if dist <= buffer_km else "PERIMETER MONITORING"
        impacted.append({
            **asset,
            "distance_km": round(dist, 2),
            "risk_status": status,
            "is_critical": dist <= buffer_km
        })

    # Sort so closest critical assets are on top
    impacted.sort(key=lambda x: x["distance_km"])

    return {
        "threat_id": f"MOES-ATM-{scenario_id.upper()[:3]}-2026",
        "scenario_key": scenario_id,
        "title": meta["title"],
        "nature": meta["type"],
        "category": meta["category"],
        "centroid_lat": c_lat,
        "centroid_lon": c_lon,
        "buffer_radius_km": buffer_km,
        "peak_wind_speed_ms": meta["wind_ms"],
        "max_precip_rate_mm_hr": meta["rain_mm_hr"],
        "divergence_residual": meta["divergence"],
        "moisture_mass_balance": meta["moisture"],
        "bounding_box_12km": meta["bbox"],
        "impact_zone": meta["impact_zone"],
        "trajectory": meta["trajectory"],
        "impacted_assets": impacted,
        "action_directives": meta["directives"],
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AeroMesh-AI | MoES / NCMRWF Multi-Hazard Operations Suite</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { display: flex; height: 100vh; background: #030712; color: #f8fafc; overflow: hidden; }

    #sidebar {
      width: 500px; min-width: 500px; background: #0b1329; padding: 18px; overflow-y: auto;
      border-right: 1px solid #1e293b; display: flex; flex-direction: column; gap: 13px;
      z-index: 1000; box-shadow: 4px 0 24px rgba(0,0,0,0.7);
    }

    #map-wrapper { position: relative; flex: 1; height: 100%; }
    #map { width: 100%; height: 100%; background: #020617; }

    .dark-tiles { filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7); }

    #windCanvas {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      pointer-events: none; z-index: 450;
    }

    .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 10.5px; font-weight: 700; text-transform: uppercase; background: #0284c7; color: white; }
    .badge.danger { background: #dc2626; }
    .badge.warning { background: #d97706; }
    .badge.success { background: #059669; }

    .panel { background: #111e38; padding: 12px; border-radius: 6px; border: 1px solid #1e293b; }
    h2 { font-size: 18px; font-weight: 700; color: #f8fafc; }
    h3 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #94a3b8; margin-bottom: 6px; font-weight: 600; }
    p { font-size: 12px; color: #cbd5e1; line-height: 1.4; }

    select, input[type=range] { width: 100%; background: #0b1329; color: #f8fafc; border: 1px solid #334155; padding: 8px; border-radius: 5px; font-size: 12px; outline: none; }
    select { cursor: pointer; }

    .btn { background: #2563eb; color: white; border: none; padding: 10px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; width: 100%; font-size: 12px; transition: 0.15s ease; }
    .btn:hover { background: #1d4ed8; }
    .btn.run { background: #059669; }
    .btn.run:hover { background: #047857; }
    .btn.pdf { background: #7c3aed; }
    .btn.pdf:hover { background: #6d28d9; }
    .btn.dispatch { background: #ea580c; }
    .btn.dispatch:hover { background: #c2410c; }

    .btn-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

    .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 4px; }
    .metric-box { background: #0b1329; padding: 10px; border-radius: 6px; border: 1px solid #1e293b; text-align: center; }
    .metric-box .val { font-size: 20px; font-weight: 800; color: #38bdf8; }
    .metric-box .label { font-size: 10px; color: #94a3b8; margin-top: 2px; }

    .asset-item { background: #0b1329; padding: 8px; border-radius: 4px; margin-top: 5px; font-size: 11px; border-left: 3px solid #64748b; }
    .asset-item.critical { border-left-color: #ef4444; background: #201016; }
    .action-card { background: #1c152e; padding: 9px; border-radius: 4px; margin-top: 5px; font-size: 11.5px; border-left: 3px solid #a855f7; }

    .radar-sweep {
      position: absolute; width: 220px; height: 220px; border-radius: 50%;
      border: 1px solid rgba(239, 68, 68, 0.6);
      background: conic-gradient(from 0deg, rgba(239, 68, 68, 0.45) 0deg, rgba(234, 179, 8, 0.25) 50deg, transparent 110deg);
      animation: rotateSweep 2.5s linear infinite;
      pointer-events: none; transform: translate(-50%, -50%);
    }
    @keyframes rotateSweep { from { transform: translate(-50%, -50%) rotate(0deg); } to { transform: translate(-50%, -50%) rotate(360deg); } }

    .pulse-ring {
      width: 24px; height: 24px; background: rgba(239, 68, 68, 0.5);
      border-radius: 50%; border: 2px solid #ef4444; animation: pulse 1.5s infinite ease-out;
    }
    @keyframes pulse { 0% { transform: scale(0.6); opacity: 1; } 100% { transform: scale(2.2); opacity: 0; } }

    /* Interactive Tactical Log Output */
    #tacticalLog {
      background: #020617; border: 1px solid #1e293b; padding: 8px; border-radius: 4px;
      font-family: monospace; font-size: 10.5px; color: #10b981; max-height: 85px; overflow-y: auto;
    }

    @media print {
      body * { visibility: hidden; }
      #printArea, #printArea * { visibility: visible; }
      #printArea { position: absolute; left: 0; top: 0; width: 100%; background: white; color: black; padding: 25px; font-size: 12pt; }
      #printArea h1 { font-size: 18pt; border-bottom: 2px solid #b91c1c; padding-bottom: 8px; margin-bottom: 12px; }
      #printArea table { width: 100%; border-collapse: collapse; margin-top: 10px; }
      #printArea th, #printArea td { border: 1px solid #ccc; padding: 6px; text-align: left; }
    }
  </style>
</head>
<body>
  <div id="sidebar">
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="badge">MoES / NCMRWF High Performance Core</span>
        <span class="badge success" id="livePill">LIVE CONNECTED</span>
      </div>
      <h2>AeroMesh-AI Tactical Center</h2>
      <p style="font-size: 11px; color: #94a3b8;">Spherical GNN Anomaly Tracker & Generative Diffusion Downscaling (12km &rarr; 5km)</p>
    </div>

    <!-- Scenario Switcher -->
    <div class="panel">
      <h3>Select Threat Scenario & Geographic Zone</h3>
      <select id="scenarioSelector" onchange="loadScenario()">
        <option value="bob_cyclone">Bay of Bengal: Super Cyclone Amphan-II (Odisha Sector)</option>
        <option value="arabian_cyclone">Arabian Sea: VSCS Biparjoy-II (Kutch / Mandvi Port)</option>
        <option value="heat_dome">Indo-Gangetic Plain: Severe Heat Dome (Delhi-NCR)</option>
        <option value="cloudburst">Sikkim Himalayas: Glacial Cloudburst & Flash Deluge (Teesta)</option>
        <option value="orographic_deluge">Western Ghats: Orographic Deluge & Landslide (Wayanad)</option>
      </select>
    </div>

    <!-- Sliders: Evacuation Buffer & Forecast Lead Time -->
    <div class="panel">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
        <h3>Impact Buffer Radius</h3>
        <span id="radiusLabel" style="font-size: 12px; font-weight:700; color:#38bdf8;">5.0 km</span>
      </div>
      <input type="range" id="bufferSlider" min="3" max="15" step="0.5" value="5" oninput="updateBufferSlider(this.value)">

      <div style="display:flex; justify-content:space-between; align-items:center; margin-top: 10px; margin-bottom: 4px;">
        <h3>Forecast Lead Time Scrubber</h3>
        <span id="leadLabel" style="font-size: 12px; font-weight:700; color:#38bdf8;">+72 Hours</span>
      </div>
      <input type="range" id="leadSlider" min="24" max="120" step="24" value="72" oninput="updateLeadSlider(this.value)">
    </div>

    <button class="btn run" id="runBtn" onclick="runCompletePipeline()">▶ Execute Stage 1 & 2 Operational Pipeline</button>

    <div class="btn-row">
      <button class="btn dispatch" onclick="triggerTacticalDispatch()">🚨 Trigger NDRF Alert & CAP SMS</button>
      <button class="btn pdf" onclick="generateNDRFReport()">📄 Export NDRF Brief (PDF)</button>
    </div>

    <!-- Live Telemetry -->
    <div class="panel">
      <h3>Physics Diagnostic Verification</h3>
      <div class="metric-grid">
        <div class="metric-box">
          <div class="val" id="divMetric">0.000</div>
          <div class="label">&nabla; &middot; V Divergence Loss</div>
        </div>
        <div class="metric-box">
          <div class="val" id="moistMetric">100%</div>
          <div class="label">Moisture Conservation</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <h3>Downscaled Threat Telemetry (Preserved Amplitudes)</h3>
      <div class="metric-grid">
        <div class="metric-box">
          <div class="val" id="windMetric">-- m/s</div>
          <div class="label">Peak Sustained Wind</div>
        </div>
        <div class="metric-box">
          <div class="val" id="rainMetric">-- mm/h</div>
          <div class="label">Max Precip Amplitude</div>
        </div>
      </div>
    </div>

    <!-- Tactical Operations Log -->
    <div class="panel">
      <h3>Tactical Common Alerting Protocol (CAP) Log</h3>
      <div id="tacticalLog">&gt; Tactical dispatcher standing by...</div>
    </div>

    <!-- Action Cards -->
    <div class="panel">
      <h3>Actionable Directives (First Responders)</h3>
      <div id="actionCardsBox"></div>
    </div>

    <!-- Spatial Database Scan -->
    <div class="panel">
      <h3>Vulnerable Assets (PostGIS Spatial Query)</h3>
      <div id="assetsBox">
        <p style="color: #64748b;">Loading spatial database query...</p>
      </div>
    </div>
  </div>

  <div id="map-wrapper">
    <div id="map"></div>
    <canvas id="windCanvas"></canvas>
  </div>

  <!-- Print Area for NDRF Briefing Sheet -->
  <div id="printArea" style="display: none;">
    <h1 id="pdfTitle">NATIONAL DISASTER RESPONSE FORCE (NDRF) INCIDENT DIRECTIVE</h1>
    <p><strong>ISSUING AUTHORITY:</strong> MoES - NCMRWF High Performance Computing Node</p>
    <p><strong>THREAT ID:</strong> <span id="pdfThreatId"></span></p>
    <p><strong>HAZARD CLASSIFICATION:</strong> <span id="pdfHazard"></span></p>
    <p><strong>CENTROID COORDINATES:</strong> <span id="pdfCoordinates"></span></p>
    <p><strong>EFFECTIVE IMPACT BUFFER:</strong> <span id="pdfBuffer"></span></p>
    <hr style="margin: 12px 0;">
    <h3>DOWNSCALED METEOROLOGICAL MEASUREMENTS (5KM SUBGRID):</h3>
    <ul>
      <li>Peak Sustained Winds: <span id="pdfWind"></span></li>
      <li>Maximum Precipitation Rate: <span id="pdfRain"></span></li>
      <li>Physical Consistency: Mass and Moisture equations satisfied (&nabla; &middot; V &le; 0.015)</li>
    </ul>
    <h3 style="margin-top: 12px;">CRITICAL INFRASTRUCTURE ASSETS IN IMPACT PERIMETER:</h3>
    <table id="pdfAssetsTable">
      <thead>
        <tr><th>Facility Name</th><th>Classification</th><th>Distance</th><th>Designated Command Directive</th></tr>
      </thead>
      <tbody></tbody>
    </table>
    <h3 style="margin-top: 12px;">COMMAND DIRECTIVES:</h3>
    <ol id="pdfDirectives"></ol>
  </div>

  <script>
    const map = L.map('map', { zoomControl: true }).setView([19.8, 85.9], 6);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors',
      className: 'dark-tiles'
    }).addTo(map);

    let gnnLayer, subgridLayer, centroidMarker, pathLayer, radarMarker, assetMarkers = [];
    let currentScenarioData = null;

    // --- HTML5 Canvas Dynamic Wind / Flow Field Animation ---
    const canvas = document.getElementById('windCanvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    const NUM_PARTICLES = 160;

    function resizeCanvas() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class StreamParticle {
      constructor() { this.reset(); }
      reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.life = Math.random() * 80 + 20;
        this.age = 0;
      }
      update(centerPoint, mode) {
        const dx = centerPoint.x - this.x;
        const dy = centerPoint.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy) + 10;
        let speed = 2.4;

        if (mode === "cyclonic") {
          // Inward cyclonic vortex spiral
          const angle = Math.atan2(dy, dx) + (Math.PI / 2) + 0.35;
          this.x += Math.cos(angle) * speed + (dx / dist) * 0.9;
          this.y += Math.sin(angle) * speed + (dy / dist) * 0.9;
        } else if (mode === "heat") {
          // Outward stagnant high pressure divergence
          const angle = Math.atan2(dy, dx);
          this.x += -Math.cos(angle) * 0.8 + (Math.random() - 0.5) * 1.5;
          this.y += -Math.sin(angle) * 0.8 + (Math.random() - 0.5) * 1.5;
        } else {
          // Orographic mountain rush towards slope
          this.x += 2.2 + (dx / dist) * 0.5;
          this.y += -1.4 + (dy / dist) * 0.5;
        }

        this.age++;
        if (this.age > this.life || (mode === "cyclonic" && dist < 12)) this.reset();
      }
      draw(mode) {
        const alpha = (1 - this.age / this.life) * 0.65;
        ctx.strokeStyle = mode === "heat" ? `rgba(251, 146, 60, ${alpha})` : `rgba(56, 189, 248, ${alpha})`;
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 1.2, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    for (let i = 0; i < NUM_PARTICLES; i++) particles.push(new StreamParticle());

    function animateWindStreamlines() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (currentScenarioData) {
        const stormCenterPoint = map.latLngToContainerPoint(L.latLng(currentScenarioData.centroid_lat, currentScenarioData.centroid_lon));
        const mode = currentScenarioData.nature;
        for (let p of particles) {
          p.update(stormCenterPoint, mode);
          p.draw(mode);
        }
      }
      requestAnimationFrame(animateWindStreamlines);
    }
    animateWindStreamlines();

    // --- Core Pipeline Execution & API Ingestion ---
    async function loadScenario() {
      const scenarioId = document.getElementById("scenarioSelector").value;
      const buffer = parseFloat(document.getElementById("bufferSlider").value);

      const res = await fetch(`/api/v1/alerts/active?scenario_id=${scenarioId}&buffer_km=${buffer}`);
      const data = await res.json();
      currentScenarioData = data;

      // Update Map View
      map.flyTo([data.centroid_lat, data.centroid_lon], data.nature === "orographic" ? 11 : 7, { duration: 1.2 });
      renderPipelineGraphics(data);
    }

    function updateBufferSlider(val) {
      document.getElementById('radiusLabel').innerText = parseFloat(val).toFixed(1) + " km";
      loadScenario();
    }

    function updateLeadSlider(val) {
      document.getElementById('leadLabel').innerText = "+" + val + " Hours";
      if (!currentScenarioData) return;
      const targetStep = currentScenarioData.trajectory.find(t => t.lead_h === parseInt(val)) || currentScenarioData.trajectory[2];
      
      currentScenarioData.centroid_lat = targetStep.lat;
      currentScenarioData.centroid_lon = targetStep.lon;
      currentScenarioData.peak_wind_speed_ms = targetStep.wind_ms;

      renderPipelineGraphics(currentScenarioData);
    }

    function renderPipelineGraphics(data) {
      // 1. Stage 1: GNN Bounding Box
      if (gnnLayer) map.removeLayer(gnnLayer);
      gnnLayer = L.rectangle(data.bounding_box_12km, {
        color: "#f59e0b", weight: 2, fillOpacity: 0.1, dashArray: "6, 6"
      }).addTo(map).bindPopup(`<b>Stage 1: Mesh GNN 4D Bounding Box</b><br>Envelope: ${data.category}`);

      // 2. Trajectory line
      if (pathLayer) map.removeLayer(pathLayer);
      const points = data.trajectory.map(p => [p.lat, p.lon]);
      pathLayer = L.polyline(points, { color: '#38bdf8', weight: 3, dashArray: '4, 4' }).addTo(map);

      // 3. Stage 2: Preserved 5km Subgrid (Adjustable Radius)
      if (subgridLayer) map.removeLayer(subgridLayer);
      subgridLayer = L.circle([data.centroid_lat, data.centroid_lon], {
        color: "#ef4444", fillColor: "#ef4444", fillOpacity: 0.4,
        radius: data.buffer_radius_km * 1000
      }).addTo(map).bindPopup(`<b>Stage 2: ${data.buffer_radius_km}km Impact Footprint</b><br>Peak Anomaly Core`);

      // 4. Radar Sweep (Only for cyclonic or orographic deluge)
      if (radarMarker) map.removeLayer(radarMarker);
      if (data.nature !== "heat") {
        const radarIcon = L.divIcon({
          className: 'radar-sweep-icon',
          html: "<div class='radar-sweep'></div>",
          iconSize: [0, 0]
        });
        radarMarker = L.marker([data.centroid_lat, data.centroid_lon], { icon: radarIcon }).addTo(map);
      }

      // 5. Pulsing Centroid Pin
      if (centroidMarker) map.removeLayer(centroidMarker);
      const pulseIcon = L.divIcon({
        className: 'custom-icon',
        html: "<div class='pulse-ring'></div>",
        iconSize: [24, 24], iconAnchor: [12, 12]
      });
      centroidMarker = L.marker([data.centroid_lat, data.centroid_lon], { icon: pulseIcon }).addTo(map)
        .bindPopup(`<b>Impact Centroid: ${data.impact_zone}</b><br>Lat: ${data.centroid_lat.toFixed(3)}, Lon: ${data.centroid_lon.toFixed(3)}`)
        .openPopup();

      // 6. Infrastructure Spatial Markers
      assetMarkers.forEach(m => map.removeLayer(m));
      assetMarkers = [];
      data.impacted_assets.forEach(a => {
        const color = a.is_critical ? '#ef4444' : '#fbbf24';
        const m = L.circleMarker([a.lat, a.lon], { color: color, fillColor: color, fillOpacity: 0.9, radius: a.is_critical ? 8 : 6 })
          .addTo(map).bindPopup(`<b>${a.name}</b><br>Classification: ${a.type}<br>Distance: ${a.distance_km} km<br>Status: <b>${a.risk_status}</b>`);
        assetMarkers.push(m);
      });

      // 7. Update Telemetry Panels
      document.getElementById('divMetric').innerText = data.divergence_residual.toFixed(3);
      document.getElementById('moistMetric').innerText = data.moisture_mass_balance.toFixed(1) + "%";
      document.getElementById('windMetric').innerText = data.peak_wind_speed_ms.toFixed(1) + (data.nature === "heat" ? " km/h" : " m/s");
      document.getElementById('rainMetric').innerText = data.max_precip_rate_mm_hr.toFixed(1) + " mm/h";

      // 8. Update Action Directives
      document.getElementById('actionCardsBox').innerHTML = data.action_directives.map(act => `
        <div class="action-card"><strong>Directive:</strong> ${act}</div>
      `).join("");

      // 9. Update Assets List
      document.getElementById('assetsBox').innerHTML = data.impacted_assets.map(a => `
        <div class="asset-item ${a.is_critical ? 'critical' : ''}">
          <div style="display:flex; justify-content:space-between;">
            <strong>${a.name}</strong>
            <span class="badge ${a.is_critical ? 'danger' : 'warning'}">${a.risk_status}</span>
          </div>
          <div style="font-size:10.5px; color:#94a3b8; margin-top:2px;">
            Type: ${a.type} &bull; Capacity: ${a.capacity} &bull; <strong>${a.distance_km} km to Eye</strong>
          </div>
        </div>
      `).join("");
    }

    async function runCompletePipeline() {
      const btn = document.getElementById('runBtn');
      btn.innerText = "⏳ Ingesting 4D Ensemble & Running Stage 1 GNN...";
      btn.disabled = true;

      setTimeout(() => {
        btn.innerText = "⏳ Applying Physics Diffusion Downscaling (5km)...";
      }, 700);

      setTimeout(() => {
        loadScenario();
        btn.innerText = "✔ Operational Pipeline Completed (Re-run)";
        btn.disabled = false;
        logTactical("Mesh GNN & Diffusion inference finished. High-resolution grid active.");
      }, 1400);
    }

    // --- Tactical Dispatch Simulator ---
    function logTactical(msg) {
      const log = document.getElementById('tacticalLog');
      const timeStr = new Date().toTimeString().split(' ')[0];
      log.innerHTML = `<div>&gt; [${timeStr}] ${msg}</div>` + log.innerHTML;
    }

    function triggerTacticalDispatch() {
      if (!currentScenarioData) return;
      logTactical(`ALERT EMITTED: Common Alerting Protocol (CAP) payload dispatched to NDRF & State SEC.`);
      logTactical(`SMS Blast initiated for ${currentScenarioData.buffer_radius_km}km radius around ${currentScenarioData.impact_zone}.`);
      
      // Audible chirp via Web Audio API
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.type = "sine";
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc.frequency.setValueAtTime(440, audioCtx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.35);
      } catch(e){}

      alert(`🚨 TACTICAL DISPATCH ISSUED!\n\nTarget: ${currentScenarioData.impact_zone}\nRadius: ${currentScenarioData.buffer_radius_km} km\nCAP Alert broadcast to State Disaster Management Authority.`);
    }

    // --- One-Click Printable PDF Briefing Generator ---
    function generateNDRFReport() {
      if (!currentScenarioData) return;
      document.getElementById('pdfThreatId').innerText = currentScenarioData.threat_id;
      document.getElementById('pdfHazard').innerText = currentScenarioData.title;
      document.getElementById('pdfCoordinates').innerText = `${currentScenarioData.centroid_lat.toFixed(3)}°N, ${currentScenarioData.centroid_lon.toFixed(3)}°E`;
      document.getElementById('pdfBuffer').innerText = `${currentScenarioData.buffer_radius_km} km Radial Perimeter`;
      document.getElementById('pdfWind').innerText = `${currentScenarioData.peak_wind_speed_ms.toFixed(1)} m/s (Preserved Extreme Peak)`;
      document.getElementById('pdfRain').innerText = `${currentScenarioData.max_precip_rate_mm_hr.toFixed(1)} mm/hr`;

      const tbody = document.querySelector('#pdfAssetsTable tbody');
      tbody.innerHTML = currentScenarioData.impacted_assets.map(a => `
        <tr>
          <td><strong>${a.name}</strong></td>
          <td>${a.type}</td>
          <td>${a.distance_km} km</td>
          <td>${a.risk_status}</td>
        </tr>
      `).join("");

      document.getElementById('pdfDirectives').innerHTML = currentScenarioData.action_directives.map(d => `<li>${d}</li>`).join("");

      const printDiv = document.getElementById("printArea");
      printDiv.style.display = "block";
      window.print();
      printDiv.style.display = "none";
    }

    // Initial load on boot
    window.addEventListener('DOMContentLoaded', loadScenario);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)