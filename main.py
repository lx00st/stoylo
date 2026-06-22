# main.py - мобильная версия с упрощенной верхней панелью

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import random
import time
import threading
from datetime import datetime
from typing import List, Dict, Any
import asyncio
#from detect_onx import detect_vehicles  
from detect_utl import detect_vehicles  

app = FastAPI(title="Dynamic Parking Map Service")

# Разрешаем CORS для запросов с карты
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовые данные парковок (неизменяемые)
BASE_PARKINGS = [
    {"id": 1, "lat": 59.938732, "lon": 30.315868, "name": "Palace Square", "total": 50, "address": "Palace Sq., 1"},
    {"id": 2, "lat": 59.935101, "lon": 30.324104, "name": "Nevsky Prospekt 30", "total": 30, "address": "Nevsky Ave., 30"},
    {"id": 3, "lat": 59.934280, "lon": 30.306633, "name": "St. Isaac's Cathedral", "total": 40, "address": "Isaac's Sq., 4"},
    {"id": 4, "lat": 59.932800, "lon": 30.295700, "name": "Mariinsky Theatre", "total": 25, "address": "Theatre Sq., 1"},
    {"id": 5, "lat": 59.944700, "lon": 30.323700, "name": "Summer Garden", "total": 35, "address": "Kutuzov Emb., 2"},
    {"id": 6, "lat": 59.956800, "lon": 30.308300, "name": "Petrograd Embankment", "total": 80, "address": "Petrograd Emb., 20"},
    {"id": 7, "lat": 59.961200, "lon": 30.300500, "name": "Kronverksky Ave", "total": 15, "address": "Kronverksky Ave., 49"},
    {"id": 8, "lat": 59.959500, "lon": 30.319000, "name": "Kamenny Island Ave", "total": 60, "address": "Kamenny Island Ave., 35"},
    {"id": 9, "lat": 59.942500, "lon": 30.282200, "name": "Vasileostrovsky Market", "total": 45, "address": "Bolshoy Ave. V.O., 16"},
    {"id": 10, "lat": 59.940300, "lon": 30.275800, "name": "Makarov Embankment", "total": 25, "address": "Makarov Emb., 2"},
    {"id": 11, "lat": 59.945100, "lon": 30.270600, "name": "Sea Port", "total": 120, "address": "Maritime Glory Sq., 1"},
    {"id": 12, "lat": 59.922100, "lon": 30.319400, "name": "Moscow Station", "total": 55, "address": "Uprising Sq., 2"},
    {"id": 13, "lat": 59.900800, "lon": 30.329700, "name": "Victory Park", "total": 70, "address": "Moskovsky Ave., 188"},
    {"id": 14, "lat": 59.895500, "lon": 30.335600, "name": "Elektrosila", "total": 35, "address": "Moskovsky Ave., 139"},
    {"id": 15, "lat": 59.928500, "lon": 30.342900, "name": "Tauride Garden", "total": 40, "address": "Tchaikovsky St., 50"},
    {"id": 16, "lat": 59.924400, "lon": 30.351200, "name": "Smolny Cathedral", "total": 45, "address": "Proletarian Dictatorship Sq., 1"},
    {"id": 17, "lat": 59.914500, "lon": 30.295800, "name": "Institute of Technology", "total": 20, "address": "Moskovsky Ave., 26"},
    {"id": 18, "lat": 59.927800, "lon": 30.262200, "name": "Mining University", "total": 55, "address": "21st Line V.O., 2"},
    {"id": 19, "lat": 59.950300, "lon": 30.241700, "name": "Primorsky Victory Park", "total": 100, "address": "Krestovsky Ave., 23"},
    {"id": 20, "lat": 59.953200, "lon": 30.220600, "name": "Gazprom Arena Stadium", "total": 800, "address": "Football Alley, 1"},
    {"id": 21, "lat": 59.969500, "lon": 30.344500, "name": "Piskaryovsky Ave", "total": 90, "address": "Piskaryovsky Ave., 25"},
    {"id": 22, "lat": 59.886600, "lon": 30.319700, "name": "Kupchino", "total": 110, "address": "Malaya Balkanskaya St., 23"},
    {"id": 23, "lat": 59.864100, "lon": 30.265300, "name": "Zvezdnaya", "total": 75, "address": "Dunaisky Ave., 48"},
    {"id": 24, "lat": 59.979200, "lon": 30.265600, "name": "Ozerki", "total": 60, "address": "Vyborgskoye Sh., 23"}
]

# Текущие данные парковок с динамическими свободными местами
active_parkings: List[Dict[str, Any]] = []

# Асинхронный апдейтер
async def background_updater():
    global active_parkings
    while True:
        await asyncio.sleep(3)
        for i, p in enumerate(active_parkings):
            if i == 0:
                nimg = random.randint(1, 4)

                n_cars = detect_vehicles(f"images/t{nimg}.jpg", 
                                        conf_threshold=0.1, 
                                        output_path=f'tuned_{nimg}_26x_01.jpg')
                
                active_parkings[i] = {**p, "free": n_cars, "last_update": datetime.now().isoformat()}
            else:
                change = random.randint(-3, 3)
                new_free = max(0, min(p["total"], p["free"] + change))
                if random.random() < 0.1:
                    new_free = max(0, min(p["total"], new_free + random.randint(-8, 8)))
                active_parkings[i] = {**p, "free": new_free, "last_update": datetime.now().isoformat()}
    

        print(f"🔄 Updated at {datetime.now().strftime('%H:%M:%S')}")


@app.on_event("startup")
async def startup_event():
    for p in BASE_PARKINGS:
        active_parkings.append({**p, "free": random.randint(0, p["total"]), "last_update": datetime.now().isoformat()})
    asyncio.create_task(background_updater())
    print("✅ Service started on Render!")

@app.get("/", response_class=HTMLResponse)
async def get_map():
    return generate_html_page()

@app.get("/api/parkings")
async def get_parkings():
    return JSONResponse(content={
        "parkings": active_parkings,
        "timestamp": datetime.now().isoformat(),
        "count": len(active_parkings)
    })

@app.get("/api/parking/{parking_id}")
async def get_parking(parking_id: int):
    parking = next((p for p in active_parkings if p["id"] == parking_id), None)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return JSONResponse(content=parking)

def generate_html_page() -> str:
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes, viewport-fit=cover, maximum-scale=1.0">
    <title>Parking Finder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f2f5f9;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            touch-action: none;
        }

        /* ===== ВЕРХНЯЯ ПАНЕЛЬ ===== */
        .app-header {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: max(8px, env(safe-area-inset-top, 8px)) 12px 10px 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
            border-bottom: 1px solid rgba(0,0,0,0.04);
        }

        .app-header-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .app-title {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .app-title h1 {
            font-size: 17px;
            font-weight: 700;
            color: #1a2a3a;
            letter-spacing: -0.3px;
        }

        .app-title .badge {
            background: #2ecc71;
            color: white;
            font-size: 8px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 30px;
            letter-spacing: 0.3px;
            animation: pulse-badge 2s ease-in-out infinite;
        }

        @keyframes pulse-badge {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #2ecc71;
            display: inline-block;
            animation: pulse-dot 1.5s ease-in-out infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.7); }
        }

        .status-dot.error {
            background: #e74c3c;
        }

        .status-time {
            font-size: 9px;
            color: #8a9aa8;
            font-weight: 500;
        }

        /* ===== ИНФОРМАЦИЯ О ВЫБРАННОЙ ПАРКОВКЕ ===== */
        .parking-info {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            background: rgba(0,0,0,0.03);
            border-radius: 10px;
            padding: 6px 12px 6px 14px;
            min-height: 38px;
            transition: all 0.3s ease;
        }

        .parking-info.hidden {
            display: none;
        }

        .parking-info .info-content {
            flex: 1;
            min-width: 0;
        }

        .parking-info .info-name {
            font-size: 13px;
            font-weight: 600;
            color: #1a2a3a;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .parking-info .info-details {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 1px;
        }

        .parking-info .info-spots {
            font-size: 11px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .parking-info .info-spots .free {
            color: #2ecc71;
        }

        .parking-info .info-spots .total {
            color: #8a9aa8;
        }

        .parking-info .info-status {
            font-size: 9px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 30px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .parking-info .info-status.green {
            background: #e8f8ef;
            color: #1a8a4a;
        }

        .parking-info .info-status.yellow {
            background: #fef6e0;
            color: #b87a0a;
        }

        .parking-info .info-status.red {
            background: #fde8e8;
            color: #c0392b;
        }

        /* Кнопка маршрута */
        .route-btn {
            flex-shrink: 0;
            background: #2ecc71;
            color: white;
            border: none;
            border-radius: 30px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s ease;
            touch-action: manipulation;
            user-select: none;
            white-space: nowrap;
            height: 30px;
        }

        .route-btn:active {
            transform: scale(0.92);
            background: #27ae60;
        }

        .route-btn .icon {
            font-size: 14px;
        }

        /* ===== ПОИСКОВАЯ СТРОКА ===== */
        .search-wrapper {
            position: relative;
            width: 100%;
            margin-top: 6px;
        }

        .search-wrapper input {
            width: 100%;
            padding: 7px 14px 7px 34px;
            font-size: 13px;
            font-weight: 400;
            border: 1px solid #e8edf2;
            border-radius: 10px;
            outline: none;
            background: #f8fafc;
            transition: all 0.25s ease;
            color: #1a2a3a;
            height: 34px;
        }

        .search-wrapper input:focus {
            border-color: #3498db;
            background: white;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.10);
        }

        .search-wrapper input::placeholder {
            color: #9aabb8;
            font-weight: 400;
        }

        .search-icon {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #9aabb8;
            font-size: 14px;
            pointer-events: none;
        }

        .search-clear {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #b0c0cc;
            font-size: 14px;
            cursor: pointer;
            padding: 4px;
            display: none;
            border-radius: 50%;
            transition: background 0.2s;
            width: 22px;
            height: 22px;
            align-items: center;
            justify-content: center;
        }

        .search-clear:hover {
            background: #eef2f6;
        }

        .search-clear.visible {
            display: flex;
        }

        /* ===== РЕЗУЛЬТАТЫ ПОИСКА ===== */
        .search-results {
            display: none;
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            right: 0;
            background: white;
            border-radius: 14px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            max-height: 260px;
            overflow-y: auto;
            z-index: 1001;
            padding: 4px 0;
            -webkit-overflow-scrolling: touch;
        }

        .search-results.active {
            display: block;
        }

        .search-results .result-item {
            padding: 10px 14px;
            cursor: pointer;
            border-bottom: 1px solid #f0f4f8;
            transition: background 0.15s;
        }

        .search-results .result-item:active {
            background: #f0f7ff;
        }

        .result-item .title {
            font-weight: 600;
            font-size: 13px;
            color: #1a2a3a;
        }

        .result-item .address {
            font-size: 11px;
            color: #8a9aa8;
            margin-top: 1px;
        }

        .result-item .stats {
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .spot-badge {
            font-size: 10px;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 30px;
            display: inline-flex;
            align-items: center;
            gap: 3px;
        }

        .spot-badge.green { background: #e8f8ef; color: #1a8a4a; }
        .spot-badge.yellow { background: #fef6e0; color: #b87a0a; }
        .spot-badge.red { background: #fde8e8; color: #c0392b; }

        .nearby-tag {
            font-size: 9px;
            color: #5a8db5;
            background: #e8f2fa;
            padding: 2px 8px;
            border-radius: 30px;
        }

        .result-empty {
            padding: 16px 14px;
            text-align: center;
            color: #8a9aa8;
            font-size: 13px;
        }

        /* ===== КАРТА ===== */
        .map-container {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #dce5ed;
        }

        #map {
            width: 100%;
            height: 100%;
        }

        /* ===== ЛЕГЕНДА ===== */
        .legend {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 10px 8px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            z-index: 800;
            pointer-events: none;
            border: 1px solid rgba(255,255,255,0.3);
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 8px;
            color: #2a3a4a;
            padding: 2px 0;
            font-weight: 500;
        }

        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
            border: 1px solid rgba(255,255,255,0.5);
        }

        /* ===== КАСТОМНЫЕ МАРКЕРЫ ===== */
        .marker {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: 700;
            font-size: 12px;
            font-family: -apple-system, Arial, sans-serif;
            border: 2.5px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
            touch-action: manipulation;
            user-select: none;
        }
        .marker:active { transform: scale(0.85) !important; }

        .cluster-marker {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            border: 2.5px solid white;
            box-shadow: 0 3px 12px rgba(0,0,0,0.25);
            cursor: pointer;
            transition: transform 0.2s;
            touch-action: manipulation;
            user-select: none;
            background: #3498db;
        }
        .cluster-marker:active { transform: scale(0.92); }
        .cluster-marker .count { font-size: 15px; line-height: 1; }
        .cluster-marker .percent { font-size: 8px; opacity: 0.85; line-height: 1; }

        /* ===== ВЫБРАННАЯ ТОЧКА ===== */
        .selected-marker {
            width: 44px;
            height: 44px;
            background: #e74c3c;
            border: 3px solid white;
            border-radius: 50%;
            box-shadow: 0 4px 16px rgba(231,76,60,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: white;
            cursor: pointer;
            animation: pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        @keyframes pop-in {
            0% { transform: scale(0.2); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }

        /* ===== SCROLLBAR ===== */
        .search-results::-webkit-scrollbar {
            width: 3px;
        }
        .search-results::-webkit-scrollbar-track {
            background: transparent;
        }
        .search-results::-webkit-scrollbar-thumb {
            background: #d0d8e0;
            border-radius: 10px;
        }

        /* ===== АДАПТИВ ===== */
        @media (max-width: 480px) {
            .app-header { padding: max(6px, env(safe-area-inset-top, 6px)) 8px 8px 8px; }
            .app-title h1 { font-size: 15px; }
            .parking-info { padding: 4px 10px 4px 12px; min-height: 34px; }
            .parking-info .info-name { font-size: 12px; }
            .parking-info .info-spots { font-size: 10px; }
            .parking-info .info-status { font-size: 8px; padding: 1px 8px; }
            .route-btn { font-size: 11px; padding: 5px 12px; height: 28px; }
            .search-wrapper input { font-size: 12px; height: 32px; padding: 6px 12px 6px 30px; }
            .search-icon { font-size: 12px; left: 8px; }
            .legend { padding: 8px 6px; right: 6px; }
            .legend-item { font-size: 7px; }
            .legend-dot { width: 8px; height: 8px; }
        }

        @media (max-width: 380px) {
            .parking-info .info-status { display: none; }
            .route-btn .label { display: none; }
            .route-btn { padding: 5px 10px; }
        }
    </style>
</head>
<body>

    <!-- ===== ВЕРХНЯЯ ПАНЕЛЬ ===== -->
    <div class="app-header">
        <!-- Строка с заголовком и статусом -->
        <div class="app-header-top">
            <div class="app-title">
                <h1>🅿️ Parking</h1>
                <span class="badge">LIVE</span>
            </div>
            <div class="header-actions">
                <span class="status-time" id="statusTime">--:--:--</span>
                <span class="status-dot" id="statusDot"></span>
            </div>
        </div>

        <!-- ИНФОРМАЦИЯ О ПАРКОВКЕ + КНОПКА ROUTE -->
        <div class="parking-info hidden" id="parkingInfo">
            <div class="info-content">
                <div class="info-name" id="infoName">Parking Name</div>
                <div class="info-details">
                    <span class="info-spots">
                        🅿️ <span class="free" id="infoFree">0</span> / <span class="total" id="infoTotal">0</span>
                    </span>
                    <span class="info-status green" id="infoStatus">Free</span>
                </div>
            </div>
            <button class="route-btn" id="routeBtn">
                <span class="icon">📍</span>
                <span class="label">Route</span>
            </button>
        </div>

        <!-- ПОИСК -->
        <div class="search-wrapper">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" placeholder="Search parking or address..." autocomplete="off">
            <button class="search-clear" id="searchClear">✕</button>
        </div>

        <!-- Результаты поиска -->
        <div class="search-results" id="searchResults"></div>
    </div>

    <!-- ===== КАРТА ===== -->
    <div class="map-container">
        <div id="map"></div>
    </div>

    <!-- ===== ЛЕГЕНДА ===== -->
    <div class="legend">
        <div class="legend-item"><span class="legend-dot" style="background:#2ecc71;"></span> Free</div>
        <div class="legend-item"><span class="legend-dot" style="background:#f39c12;"></span> Medium</div>
        <div class="legend-item"><span class="legend-dot" style="background:#e74c3c;"></span> Full</div>
        <div class="legend-item"><span class="legend-dot" style="background:#3498db;"></span> Cluster</div>
    </div>

    <script src="https://api-maps.yandex.ru/v3/?apikey=bb36a041-64be-4fd6-b306-a246fe863173&lang=en_US"></script>

    <script>
        // ===== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ =====
        let map = null;
        let clusterer = null;
        let selectedMarker = null;
        let updateInterval = null;
        let currentParkings = [];
        let markerFns = null;
        let selectedParking = null;
        let selectedCoords = null;

        // ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
        function haversine(lat1, lon1, lat2, lon2) {
            const R = 6371000;
            const φ1 = lat1 * Math.PI / 180, φ2 = lat2 * Math.PI / 180;
            const Δφ = (lat2 - lat1) * Math.PI / 180, Δλ = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(Δφ/2)**2 + Math.cos(φ1)*Math.cos(φ2)*Math.sin(Δλ/2)**2;
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        }

        function countNearby(lat, lon, radius=300) {
            let total = 0;
            for (const p of currentParkings) {
                if (haversine(lat, lon, p.lat, p.lon) <= radius) total += p.free;
            }
            return total;
        }

        function getColor(free, total) {
            if (total === 0) return '#95a5a6';
            const pct = free / total * 100;
            if (pct > 40) return '#2ecc71';
            if (pct > 15) return '#f39c12';
            return '#e74c3c';
        }

        function getStatusClass(free, total) {
            if (total === 0) return 'red';
            const pct = free / total * 100;
            if (pct > 40) return 'green';
            if (pct > 15) return 'yellow';
            return 'red';
        }

        function getStatusText(free, total) {
            if (total === 0) return 'Full';
            const pct = free / total * 100;
            if (pct > 40) return 'Free';
            if (pct > 15) return 'Medium';
            return 'Full';
        }

        function updateStatus(message, isOk = true) {
            const timeEl = document.getElementById('statusTime');
            const dot = document.getElementById('statusDot');
            if (timeEl) {
                const now = new Date();
                timeEl.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            }
            if (dot) {
                dot.className = 'status-dot' + (isOk ? '' : ' error');
            }
        }

        // ===== ОБНОВЛЕНИЕ ИНФО-ПАНЕЛИ =====
        function updateParkingInfo(parking) {
            const info = document.getElementById('parkingInfo');
            if (!parking) {
                info.classList.add('hidden');
                return;
            }

            info.classList.remove('hidden');
            document.getElementById('infoName').textContent = parking.name || 'Selected point';
            document.getElementById('infoFree').textContent = parking.free ?? 0;
            document.getElementById('infoTotal').textContent = parking.total ?? 0;

            const statusEl = document.getElementById('infoStatus');
            const cls = getStatusClass(parking.free, parking.total);
            statusEl.className = 'info-status ' + cls;
            statusEl.textContent = getStatusText(parking.free, parking.total);

            selectedParking = parking;
        }

        // ===== ЗАГРУЗКА ДАННЫХ =====
        async function fetchParkings() {
            try {
                const resp = await fetch('/api/parkings');
                const data = await resp.json();
                if (data.parkings && Array.isArray(data.parkings)) {
                    currentParkings = data.parkings;
                    updateStatus(`✅ ${currentParkings.length} spots`, true);
                    return true;
                }
                return false;
            } catch(e) {
                console.warn(e);
                updateStatus('❌ Error', false);
                return false;
            }
        }

        // ===== ОБНОВЛЕНИЕ МАРКЕРОВ =====
        async function refreshMarkers() {
            if (!map || !markerFns) return;
            const ok = await fetchParkings();
            if (!ok) return;

            const features = currentParkings.map(p => ({
                type: 'Feature',
                id: p.id,
                geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
                properties: { ...p, lat: p.lat, lon: p.lon }
            }));

            if (clusterer) map.removeChild(clusterer);

            const { YMapClusterer, clusterByGrid } = markerFns;
            clusterer = new YMapClusterer({
                features,
                method: clusterByGrid({ gridSize: 70 }),
                marker: createMarkerFn,
                cluster: createClusterFn
            });
            map.addChild(clusterer);

            // Обновляем инфо о выбранной парковке
            if (selectedParking) {
                const updated = currentParkings.find(p => p.id === selectedParking.id);
                if (updated) {
                    updateParkingInfo(updated);
                }
            }
        }

        // ===== ФАБРИКИ МАРКЕРОВ =====
        let createMarkerFn, createClusterFn;

        function buildMarker(feature) {
            const p = feature.properties;
            const color = getColor(p.free, p.total);
            const el = document.createElement('div');
            el.className = 'marker';
            el.style.background = color;
            el.textContent = p.free;
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                selectPoint(p.lat, p.lon, p);
            });
            return new ymaps3.YMapMarker({ coordinates: feature.geometry.coordinates }, el);
        }

        function buildCluster(coords, features) {
            const count = features.length;
            let totalFree = 0, totalSpots = 0;
            features.forEach(f => {
                totalFree += f.properties.free;
                totalSpots += f.properties.total;
            });
            const pct = totalSpots > 0 ? Math.round(totalFree / totalSpots * 100) : 0;
            const el = document.createElement('div');
            el.className = 'cluster-marker';
            el.innerHTML = `<span class="count">${count}</span><span class="percent">${pct}%</span>`;
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                map.setLocation({ center: [coords[0], coords[1]], zoom: 15, duration: 400 });
                // При клике на кластер не выбираем конкретную парковку
                const fakeParking = { name: `Cluster (${count} spots)`, free: totalFree, total: totalSpots, id: -1 };
                selectPoint(coords[1], coords[0], fakeParking);
            });
            return new ymaps3.YMapMarker({ coordinates: coords }, el);
        }

        // ===== ВЫБОР ТОЧКИ =====
        function selectPoint(lat, lon, parkingData) {
            removeSelected();
            selectedCoords = { lat, lon };

            const el = document.createElement('div');
            el.className = 'selected-marker';
            el.textContent = '📍';
            const marker = new ymaps3.YMapMarker({ coordinates: [lon, lat] }, el);
            map.addChild(marker);
            selectedMarker = marker;

            // Обновляем информацию
            if (parkingData && parkingData.id !== -1) {
                updateParkingInfo(parkingData);
            } else if (parkingData && parkingData.name) {
                // Это кластер
                updateParkingInfo(parkingData);
            } else {
                // Просто точка на карте
                const fake = { name: 'Selected point', free: 0, total: 0, id: -2 };
                updateParkingInfo(fake);
            }

            // Кнопка маршрута
            const routeBtn = document.getElementById('routeBtn');
            routeBtn.onclick = () => {
                window.open(`https://yandex.ru/maps/?rtext=${lat},${lon}&rtt=auto`, '_blank');
            };
        }

        function removeSelected() {
            if (selectedMarker) {
                map.removeChild(selectedMarker);
                selectedMarker = null;
            }
        }

        // ===== ИНИЦИАЛИЗАЦИЯ КАРТЫ =====
        async function initMap() {
            try {
                if (typeof ymaps3 === 'undefined') throw new Error('Yandex Maps API not loaded');
                await ymaps3.ready;

                const { YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer, YMapMarker, YMapListener } = ymaps3;
                const clusterMod = await ymaps3.import('@yandex/ymaps3-clusterer@0.0.1');
                const { YMapClusterer, clusterByGrid } = clusterMod;

                markerFns = { YMapClusterer, clusterByGrid };
                createMarkerFn = buildMarker;
                createClusterFn = buildCluster;

                map = new YMap(document.getElementById('map'), {
                    location: { center: [30.315868, 59.938732], zoom: 13 }
                });
                map.addChild(new YMapDefaultSchemeLayer());
                map.addChild(new YMapDefaultFeaturesLayer());

                // Загружаем данные
                await fetchParkings();
                const features = currentParkings.map(p => ({
                    type: 'Feature',
                    id: p.id,
                    geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
                    properties: { ...p, lat: p.lat, lon: p.lon }
                }));

                clusterer = new YMapClusterer({
                    features,
                    method: clusterByGrid({ gridSize: 70 }),
                    marker: createMarkerFn,
                    cluster: createClusterFn
                });
                map.addChild(clusterer);

                // Клик по карте
                map.addChild(new YMapListener({
                    layer: 'any',
                    onClick: (layer, coords, obj) => {
                        if (coords && coords.length === 2) {
                            // Ищем ближайшую парковку
                            let nearest = null;
                            let minDist = Infinity;
                            for (const p of currentParkings) {
                                const d = haversine(coords[1], coords[0], p.lat, p.lon);
                                if (d < minDist && d < 200) {
                                    minDist = d;
                                    nearest = p;
                                }
                            }
                            if (nearest) {
                                selectPoint(nearest.lat, nearest.lon, nearest);
                            } else {
                                const fake = { name: 'Selected point', free: 0, total: 0, id: -2 };
                                selectPoint(coords[1], coords[0], fake);
                            }
                        }
                    }
                }));

                // ===== ПОИСК =====
                const searchInput = document.getElementById('searchInput');
                const resultsEl = document.getElementById('searchResults');
                const clearBtn = document.getElementById('searchClear');

                searchInput.addEventListener('input', () => {
                    clearBtn.classList.toggle('visible', searchInput.value.length > 0);
                    debounceSearch(searchInput.value);
                });

                searchInput.addEventListener('focus', () => {
                    if (searchInput.value.length >= 2) debounceSearch(searchInput.value);
                });

                clearBtn.addEventListener('click', () => {
                    searchInput.value = '';
                    clearBtn.classList.remove('visible');
                    resultsEl.classList.remove('active');
                    searchInput.focus();
                });

                document.addEventListener('click', (e) => {
                    if (!searchInput.contains(e.target) && !resultsEl.contains(e.target)) {
                        resultsEl.classList.remove('active');
                    }
                });

                let debounceTimer;
                function debounceSearch(q) {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => performSearch(q), 300);
                }

                async function performSearch(query) {
                    if (!query || query.length < 2) {
                        resultsEl.classList.remove('active');
                        return;
                    }

                    const results = await geocode(query);
                    resultsEl.innerHTML = '';

                    if (results.length === 0) {
                        resultsEl.innerHTML = '<div class="result-empty">No parking found nearby</div>';
                        resultsEl.classList.add('active');
                        return;
                    }

                    for (const r of results) {
                        const div = document.createElement('div');
                        div.className = 'result-item';
                        const cls = getStatusClass(r.freeSpots, 100);
                        div.innerHTML = `
                            <div class="title">${escapeHtml(r.name)}</div>
                            <div class="address">${escapeHtml(r.address.substring(0, 70))}</div>
                            <div class="stats">
                                <span class="spot-badge ${cls}">🅿️ ${r.freeSpots} free</span>
                                <span class="nearby-tag">📍 within 300m</span>
                            </div>
                        `;
                        div.addEventListener('click', () => {
                            map.setLocation({ center: [r.lon, r.lat], zoom: 16, duration: 400 });
                            // Находим парковку в данных
                            let found = null;
                            for (const p of currentParkings) {
                                if (haversine(r.lat, r.lon, p.lat, p.lon) < 50) {
                                    found = p;
                                    break;
                                }
                            }
                            if (found) {
                                selectPoint(r.lat, r.lon, found);
                            } else {
                                const fake = { name: r.name, free: r.freeSpots, total: 100, id: -2 };
                                selectPoint(r.lat, r.lon, fake);
                            }
                            resultsEl.classList.remove('active');
                            searchInput.value = r.name;
                            clearBtn.classList.toggle('visible', true);
                        });
                        resultsEl.appendChild(div);
                    }
                    resultsEl.classList.add('active');
                }

                async function geocode(query) {
                    try {
                        const url = `https://geocode-maps.yandex.ru/1.x/?apikey=8fc5e4ba-8ce3-4230-8529-4898346c54ab&geocode=${encodeURIComponent(query)}&format=json&results=8`;
                        const resp = await fetch(url);
                        const data = await resp.json();
                        const members = data.response?.GeoObjectCollection?.featureMember || [];
                        const out = [];
                        for (const m of members) {
                            const geo = m.GeoObject;
                            const name = geo.name;
                            const address = geo.metaDataProperty?.GeocoderMetaData?.text || '';
                            const pos = geo.Point?.pos;
                            if (pos) {
                                const [lon, lat] = pos.split(' ').map(Number);
                                const freeSpots = countNearby(lat, lon, 300);
                                out.push({ name, address, lat, lon, freeSpots });
                            }
                        }
                        return out;
                    } catch(e) {
                        console.warn(e);
                        return [];
                    }
                }

                function escapeHtml(str) {
                    const div = document.createElement('div');
                    div.textContent = str;
                    return div.innerHTML;
                }

                // ===== АВТООБНОВЛЕНИЕ =====
                updateInterval = setInterval(refreshMarkers, 10000);
                updateStatus('✅ Live', true);

                console.log('✅ Parking Finder initialized');

            } catch(err) {
                console.error(err);
                document.getElementById('map').innerHTML = `
                    <div style="padding:30px;background:white;margin:20px;border-radius:16px;text-align:center;">
                        <div style="font-size:40px;margin-bottom:12px;">⚠️</div>
                        <div style="font-weight:600;color:#2a3a4a;">${err.message}</div>
                        <div style="font-size:13px;color:#8a9aa8;margin-top:8px;">Please check your connection</div>
                    </div>
                `;
            }
        }

        // ===== СТАРТ =====
        document.addEventListener('DOMContentLoaded', initMap);
    </script>
</body>
</html>'''
    
    return html

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)