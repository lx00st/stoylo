# main.py - исправленная версия

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import random
import time
import threading
from datetime import datetime
from typing import List, Dict, Any
import asyncio

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

# def update_parking_state():
#     """Фоновая функция для симуляции динамического обновления свободных мест"""
#     global active_parkings
    
#     # Инициализация начальными случайными значениями
#     for p in BASE_PARKINGS:
#         free = random.randint(0, p["total"])
#         active_parkings.append({
#             **p,
#             "free": free,
#             "last_update": datetime.now().isoformat()
#         })
    
#     # Цикл обновления данных
#     while True:
#         time.sleep(3)  # Обновляем каждые 3 секунды
        
#         for i, p in enumerate(active_parkings):
#             # Случайное изменение: от -3 до +3 мест
#             change = random.randint(-3, 3)
#             new_free = p["free"] + change
#             new_free = max(0, min(p["total"], new_free))
            
#             # Иногда добавляем более заметные изменения
#             if random.random() < 0.1:  # 10% шанс на событие
#                 big_change = random.randint(-8, 8)
#                 new_free = max(0, min(p["total"], new_free + big_change))
            
#             active_parkings[i] = {
#                 **p,
#                 "free": new_free,
#                 "last_update": datetime.now().isoformat()
#             }
        
#         print(f"🔄 Parking state updated at {datetime.now().strftime('%H:%M:%S')}")

# # Запускаем фоновый поток для обновления состояния
# background_thread = threading.Thread(target=update_parking_state, daemon=True)
# background_thread.start()

# Асинхронный апдейтер вместо threading
async def background_updater():
    global active_parkings
    while True:
        await asyncio.sleep(3)
        for i, p in enumerate(active_parkings):
            change = random.randint(-3, 3)
            new_free = max(0, min(p["total"], p["free"] + change))
            if random.random() < 0.1:
                new_free = max(0, min(p["total"], new_free + random.randint(-8, 8)))
            active_parkings[i] = {**p, "free": new_free, "last_update": datetime.now().isoformat()}
        print(f"🔄 Updated at {datetime.now().strftime('%H:%M:%S')}")

@app.on_event("startup")
async def startup_event():
    # Инициализация
    for p in BASE_PARKINGS:
        active_parkings.append({**p, "free": random.randint(0, p["total"]), "last_update": datetime.now().isoformat()})
    asyncio.create_task(background_updater())
    print("✅ Service started on Render!")

# @app.on_event("startup")
# async def startup_event():
#     print("✅ Dynamic parking service started!")
#     print("📊 State updates every 3 seconds")
#     print("📍 Client will fetch every 10 seconds")

@app.get("/", response_class=HTMLResponse)
async def get_map():
    """Главная страница с картой парковок (вся логика на клиенте)"""
    return generate_html_page()

@app.get("/api/parkings")
async def get_parkings():
    """Получить актуальные данные всех парковок (динамически обновляемые)"""
    return JSONResponse(content={
        "parkings": active_parkings,
        "timestamp": datetime.now().isoformat(),
        "count": len(active_parkings)
    })

@app.get("/api/parking/{parking_id}")
async def get_parking(parking_id: int):
    """Получить данные конкретной парковки"""
    parking = next((p for p in active_parkings if p["id"] == parking_id), None)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    return JSONResponse(content=parking)

def generate_html_page() -> str:
    """Генерирует HTML страницу с картой, которая забирает данные по API каждые 10 секунд"""
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes, viewport-fit=cover">
    <title>Dynamic Parking Map - Real-time Updates</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', 'Arial', sans-serif;
            background: #e9f0f5;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            padding: 0;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }

        .map-container {
            flex: 1;
            position: relative;
            background: #cbdde6;
            min-height: 0;
            width: 100%;
            height: 100%;
        }

        #map {
            height: 100%;
            width: 100%;
        }

        .top-combined-panel {
            position: absolute;
            top: max(12px, env(safe-area-inset-top, 12px));
            left: max(12px, env(safe-area-inset-left, 12px));
            right: max(12px, env(safe-area-inset-right, 12px));
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }

        .custom-search {
            width: 100%;
            background: white;
            border-radius: 48px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            pointer-events: auto;
            position: relative;
        }

        .custom-search input {
            width: 100%;
            padding: 14px 20px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 48px;
            outline: none;
            background: white;
            transition: all 0.2s;
        }

        .custom-search input:focus {
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.2);
        }

        .custom-search .results {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            max-height: 380px;
            overflow-y: auto;
            z-index: 1001;
            margin-top: 8px;
        }

        .custom-search .results.active {
            display: block;
        }

        .custom-search .result-item {
            padding: 12px 18px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
            transition: background 0.15s;
        }

        .custom-search .result-item:hover {
            background: #f0f7ff;
        }

        .result-title {
            font-weight: 600;
            font-size: 14px;
            color: #1a2a3a;
        }

        .result-address {
            font-size: 11px;
            color: #6c8a9e;
            margin-top: 2px;
        }

        .result-parking-stats {
            font-size: 11px;
            margin-top: 5px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
        }

        .free-spots-badge {
            background: #2ecc71;
            color: white;
            padding: 2px 10px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 11px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .free-spots-badge.low {
            background: #e74c3c;
        }

        .free-spots-badge.medium {
            background: #f39c12;
        }

        .nearby-info {
            color: #2c6e9e;
            font-size: 10px;
        }

        .route-panel-simple {
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(16px);
            border-radius: 60px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            pointer-events: auto;
            border: 1px solid rgba(255, 255, 255, 0.6);
            width: auto;
            align-self: center;
            max-width: 90%;
        }

        .simple-panel-inner {
            padding: 8px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .route-btn {
            background: #ffcc00;
            color: #1f2f38;
            border: none;
            padding: 10px 24px;
            border-radius: 60px;
            font-weight: bold;
            font-size: 15px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: 0.2s;
            text-decoration: none;
            white-space: nowrap;
        }

        .route-btn:hover {
            background: #e6b800;
            transform: translateY(-1px);
        }

        .legend {
            position: absolute;
            bottom: max(20px, env(safe-area-inset-bottom, 20px));
            right: max(12px, env(safe-area-inset-right, 12px));
            background: rgba(255,255,255,0.94);
            backdrop-filter: blur(4px);
            padding: 10px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-size: 10px;
            z-index: 1000;
            pointer-events: none;
            max-width: 160px;
        }

        .legend h4 {
            margin: 0 0 5px 0;
            font-size: 11px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 3px;
            font-size: 9px;
        }

        .legend-color {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 6px;
        }

        .legend-cluster {
            width: 18px;
            height: 18px;
            background: #3498db;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 6px;
            color: white;
            font-size: 8px;
            font-weight: bold;
        }

        .click-marker {
            width: 42px;
            height: 42px;
            background-color: #e74c3c;
            border: 3px solid white;
            border-radius: 50%;
            box-shadow: 0 3px 12px rgba(0,0,0,0.3);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: white;
            font-weight: bold;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.28); opacity: 0.9; }
            100% { transform: scale(1); opacity: 1; }
        }
        .click-marker.pulse {
            animation: pulse 0.35s ease-in-out;
        }

        .status-badge {
            position: absolute;
            bottom: max(20px, env(safe-area-inset-bottom, 20px));
            left: max(12px, env(safe-area-inset-left, 12px));
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            color: white;
            z-index: 1000;
            pointer-events: none;
            font-family: monospace;
            transition: all 0.3s;
        }

        .status-badge.updated {
            background: rgba(46, 204, 113, 0.9);
            transform: scale(1.02);
        }

        @media (max-width: 650px) {
            .top-combined-panel {
                top: max(10px, env(safe-area-inset-top, 10px));
                left: max(10px, env(safe-area-inset-left, 10px));
                right: max(10px, env(safe-area-inset-right, 10px));
                gap: 8px;
            }
            .custom-search input {
                padding: 12px 16px;
                font-size: 14px;
            }
            .route-btn {
                padding: 8px 20px;
                font-size: 14px;
            }
            .status-badge {
                font-size: 9px;
                bottom: max(15px, env(safe-area-inset-bottom, 15px));
            }
        }
    </style>
</head>
<body>

<div class="map-container">
    <div id="map"></div>
    
    <div class="top-combined-panel">
        <div class="custom-search">
            <input type="text" id="search-input" placeholder="🔍 Search for parking or address...">
            <div class="results" id="search-results"></div>
        </div>
        
        <div class="route-panel-simple">
            <div class="simple-panel-inner">
                <a href="#" id="dynamicRouteBtn" class="route-btn" target="_blank" rel="noopener noreferrer">
                    🚗 Yandex Maps
                </a>
            </div>
        </div>
    </div>
    
    <div class="legend">
        <h4>🚗 Parking</h4>
        <div class="legend-item"><div class="legend-color" style="background:#2ecc71;"></div><span>Free >40%</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#f39c12;"></div><span>15-40%</span></div>
        <div class="legend-item"><div class="legend-color" style="background:#e74c3c;"></div><span>&lt;15%</span></div>
        <div class="legend-item"><div class="legend-cluster">12</div><span>Cluster</span></div>
    </div>
    
    <div class="status-badge" id="statusBadge">
        🔄 Loading...
    </div>
</div>

<script src="https://api-maps.yandex.ru/v3/?apikey=bb36a041-64be-4fd6-b306-a246fe863173&lang=en_US"></script>

<script>
    // ========== ВСЯ ЛОГИКА НА КЛИЕНТЕ ==========
    let map = null;
    let clusterer = null;
    let currentClickMarker = null;
    let updateInterval = null;
    let currentParkings = [];
    let markerCreationFunctions = null; // Храним функции создания маркеров

    // Вспомогательные функции
    function haversineDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000;
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;
        
        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    function countFreeSpotsInRadius(lat, lon, radiusMeters = 300) {
        let totalFree = 0;
        for (const p of currentParkings) {
            const dist = haversineDistance(lat, lon, p.lat, p.lon);
            if (dist <= radiusMeters) {
                totalFree += p.free;
            }
        }
        return totalFree;
    }
    
    function getColorByOccupancy(free, total) {
        if (total === 0) return '#95a5a6';
        const percent = (free / total) * 100;
        if (percent > 40) return '#2ecc71';
        if (percent > 15) return '#f39c12';
        return '#e74c3c';
    }
    
    function updateStatus(message, isSuccess = true) {
        const badge = document.getElementById('statusBadge');
        if (badge) {
            badge.textContent = message;
            badge.classList.add('updated');
            if (!isSuccess) {
                badge.style.background = 'rgba(231, 76, 60, 0.9)';
            } else {
                badge.style.background = 'rgba(46, 204, 113, 0.9)';
            }
            setTimeout(() => {
                badge.classList.remove('updated');
                badge.style.background = 'rgba(0,0,0,0.7)';
            }, 2000);
        }
    }
    
    // Загрузка данных с сервера
    async function fetchParkings() {
        try {
            const response = await fetch('/api/parkings');
            const data = await response.json();
            if (data.parkings && Array.isArray(data.parkings)) {
                currentParkings = data.parkings;
                const time = new Date(data.timestamp).toLocaleTimeString();
                updateStatus(`✅ Updated ${time} · ${currentParkings.length} spots`);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Fetch error:', error);
            updateStatus('❌ Connection error', false);
            return false;
        }
    }
    
    // Обновление маркеров на карте - ПЕРЕСОЗДАЕМ КЛАСТЕРИЗАТОР
    async function refreshMarkers() {
        if (!map || !markerCreationFunctions) return;
        
        const success = await fetchParkings();
        if (!success) return;
        
        // Создаём новые features на основе актуальных данных
        const features = currentParkings.map((p) => ({
            type: 'Feature',
            id: p.id,
            geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
            properties: {
                id: p.id,
                name: p.name,
                free: p.free,
                total: p.total,
                address: p.address,
                lat: p.lat,
                lon: p.lon
            }
        }));
        
        // Удаляем старый кластеризатор
        if (clusterer) {
            map.removeChild(clusterer);
        }
        
        // Создаем новый кластеризатор с обновленными данными
        const { YMapClusterer, clusterByGrid } = markerCreationFunctions;
        clusterer = new YMapClusterer({
            features: features,
            method: clusterByGrid({ gridSize: 70 }),
            marker: createMarker,
            cluster: createCluster
        });
        map.addChild(clusterer);
        
        console.log('🔄 Markers refreshed at', new Date().toLocaleTimeString());
    }
    
    // Функции создания маркеров
    let createMarker, createCluster;
    
    // Инициализация карты
    async function initMap() {
        try {
            if (typeof ymaps3 === 'undefined') throw new Error('Yandex Maps API failed to load');
            await ymaps3.ready;
            
            const { YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer, YMapMarker, YMapListener } = ymaps3;
            const clustererModule = await ymaps3.import('@yandex/ymaps3-clusterer@0.0.1');
            const { YMapClusterer, clusterByGrid } = clustererModule;
            
            // Сохраняем функции для создания маркеров и кластеров
            markerCreationFunctions = { YMapClusterer, clusterByGrid };
            
            map = new YMap(document.getElementById('map'), {
                location: { center: [30.315868, 59.938732], zoom: 13 }
            });
            map.addChild(new YMapDefaultSchemeLayer());
            map.addChild(new YMapDefaultFeaturesLayer());
            
            // Определяем createMarker
            createMarker = (feature) => {
                const props = feature.properties;
                const color = getColorByOccupancy(props.free, props.total);
                const div = document.createElement('div');
                div.textContent = props.free;
                div.style.cssText = `
                    background-color: ${color};
                    width: 34px; height: 34px; border-radius: 50%;
                    display: flex; justify-content: center; align-items: center;
                    color: white; font-weight: bold; font-size: 13px;
                    font-family: Arial; border: 2px solid white;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
                    cursor: pointer;
                    transition: transform 0.2s;
                `;
                div.onmouseenter = () => div.style.transform = 'scale(1.08)';
                div.onmouseleave = () => div.style.transform = 'scale(1)';
                div.onclick = (e) => {
                    e.stopPropagation();
                    setSelectedPoint(props.lat, props.lon, props.name);
                };
                return new YMapMarker({ coordinates: feature.geometry.coordinates }, div);
            };
            
            // Определяем createCluster
            createCluster = (coordinates, featuresList) => {
                const count = featuresList.length;
                let totalFree = 0, totalSpots = 0;
                featuresList.forEach(f => {
                    totalFree += f.properties.free;
                    totalSpots += f.properties.total;
                });
                const avgPercent = totalSpots > 0 ? Math.round((totalFree / totalSpots) * 100) : 0;
                const clusterDiv = document.createElement('div');
                clusterDiv.style.cssText = `
                    background-color: #3498db; width: 44px; height: 44px; border-radius: 50%;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    color: white; font-weight: bold; border: 2px solid white;
                    box-shadow: 0 3px 8px rgba(0,0,0,0.3); cursor: pointer;
                    transition: transform 0.2s;
                `;
                const spanCount = document.createElement('span');
                spanCount.textContent = count;
                spanCount.style.fontSize = '16px';
                const spanPercent = document.createElement('span');
                spanPercent.textContent = `${avgPercent}%`;
                spanPercent.style.fontSize = '9px';
                clusterDiv.appendChild(spanCount);
                clusterDiv.appendChild(spanPercent);
                clusterDiv.onmouseenter = () => clusterDiv.style.transform = 'scale(1.05)';
                clusterDiv.onmouseleave = () => clusterDiv.style.transform = 'scale(1)';
                clusterDiv.onclick = (e) => {
                    e.stopPropagation();
                    setSelectedPoint(coordinates[1], coordinates[0], `Cluster (${count} parkings)`);
                    map.setLocation({ center: [coordinates[0], coordinates[1]], zoom: 15, duration: 400 });
                };
                return new YMapMarker({ coordinates: coordinates }, clusterDiv);
            };
            
            // Загружаем начальные данные
            await fetchParkings();
            
            const features = currentParkings.map((p) => ({
                type: 'Feature',
                id: p.id,
                geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
                properties: {
                    id: p.id,
                    name: p.name,
                    free: p.free,
                    total: p.total,
                    address: p.address,
                    lat: p.lat,
                    lon: p.lon
                }
            }));
            
            clusterer = new YMapClusterer({
                features: features,
                method: clusterByGrid({ gridSize: 70 }),
                marker: createMarker,
                cluster: createCluster
            });
            map.addChild(clusterer);
            
            // Функция для установки выбранной точки
            function setSelectedPoint(lat, lon, title) {
                removeClickMarker();
                const markerEl = document.createElement('div');
                markerEl.className = 'click-marker';
                markerEl.textContent = '📍';
                const newMarker = new YMapMarker({ coordinates: [lon, lat] }, markerEl);
                map.addChild(newMarker);
                currentClickMarker = newMarker;
                markerEl.classList.add('pulse');
                setTimeout(() => markerEl.classList.remove('pulse'), 400);
                updateRouteButton(lat, lon);
            }
            
            function removeClickMarker() {
                if (currentClickMarker) {
                    map.removeChild(currentClickMarker);
                    currentClickMarker = null;
                }
            }
            
            function updateRouteButton(lat, lon) {
                const routeBtn = document.getElementById('dynamicRouteBtn');
                if (routeBtn && lat && lon) {
                    routeBtn.href = `https://yandex.ru/maps/?rtext=${lat},${lon}&rtt=auto`;
                }
            }
            
            // Клик по карте
            map.addChild(new YMapListener({
                layer: 'any',
                onClick: (layer, coordinates, object) => {
                    if (coordinates && coordinates.length === 2) {
                        setSelectedPoint(coordinates[1], coordinates[0], "Point on map");
                    }
                }
            }));
            
            document.getElementById('dynamicRouteBtn').href = 'https://yandex.ru/maps/';
            
            // ЗАПУСКАЕМ ОБНОВЛЕНИЕ КАЖДЫЕ 10 СЕКУНД
            updateInterval = setInterval(async () => {
                await refreshMarkers();
            }, 10000);
            
            updateStatus('✅ Real-time: fetching every 10s');
            
            // ========== ПОИСК ==========
            const searchInput = document.getElementById('search-input');
            const resultsContainer = document.getElementById('search-results');
            
            function escapeHtml(str) {
                if (!str) return '';
                return str.replace(/[&<>]/g, function(m) {
                    if (m === '&') return '&amp;';
                    if (m === '<') return '&lt;';
                    if (m === '>') return '&gt;';
                    return m;
                });
            }
            
            async function performSearch(query) {
                if (!query || query.length < 2) {
                    resultsContainer.classList.remove('active');
                    return;
                }
                
                const results = await geocode(query);
                
                if (results.length) {
                    resultsContainer.innerHTML = '';
                    for (const result of results) {
                        const item = document.createElement('div');
                        item.className = 'result-item';
                        
                        let badgeClass = 'free-spots-badge';
                        let badgeEmoji = '🅿️';
                        if (result.freeSpots === 0) {
                            badgeClass += ' low';
                            badgeEmoji = '⚠️';
                        } else if (result.freeSpots < 10) {
                            badgeClass += ' medium';
                        }
                        
                        item.innerHTML = `
                            <div class="result-title">${escapeHtml(result.name)}</div>
                            <div class="result-address">${escapeHtml(result.address.substring(0, 80))}</div>
                            <div class="result-parking-stats">
                                <span class="${badgeClass}">
                                    ${badgeEmoji} ${result.freeSpots} free spots
                                </span>
                                <span class="nearby-info">📍 within 300m</span>
                            </div>
                        `;
                        item.onclick = () => {
                            map.setLocation({ center: [result.lon, result.lat], zoom: 16, duration: 400 });
                            setSelectedPoint(result.lat, result.lon, result.name);
                            resultsContainer.classList.remove('active');
                            searchInput.value = result.name;
                        };
                        resultsContainer.appendChild(item);
                    }
                    resultsContainer.classList.add('active');
                } else {
                    resultsContainer.innerHTML = '<div class="result-item">No results found</div>';
                    resultsContainer.classList.add('active');
                }
            }
            
            // Геокодирование
            async function geocode(query) {
                if (!query || query.length < 2) return [];
                try {
                    const url = `https://geocode-maps.yandex.ru/1.x/?apikey=8fc5e4ba-8ce3-4230-8529-4898346c54ab&geocode=${encodeURIComponent(query)}&format=json&results=8`;
                    const response = await fetch(url);
                    const data = await response.json();
                    const members = data.response?.GeoObjectCollection?.featureMember || [];
                    
                    const results = [];
                    for (const member of members) {
                        const geo = member.GeoObject;
                        const name = geo.name;
                        const address = geo.metaDataProperty?.GeocoderMetaData?.text || "";
                        const pointStr = geo.Point?.pos;
                        if (pointStr) {
                            const [lon, lat] = pointStr.split(' ').map(Number);
                            const freeSpots = countFreeSpotsInRadius(lat, lon, 300);
                            results.push({ name, address, lat, lon, freeSpots });
                        }
                    }
                    return results;
                } catch(e) {
                    console.warn(e);
                    return [];
                }
            }
            
            let debounce;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounce);
                debounce = setTimeout(() => performSearch(e.target.value), 400);
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    clearTimeout(debounce);
                    performSearch(searchInput.value);
                }
            });
            
            document.addEventListener('click', (e) => {
                if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                    resultsContainer.classList.remove('active');
                }
            });
            
            console.log('✅ Map ready, auto-refresh every 10 seconds');
            
        } catch (err) {
            console.error(err);
            document.getElementById('map').innerHTML = `<div style="padding:40px;background:white;margin:20px;border-radius:20px;">❌ Error: ${err.message}</div>`;
        }
    }
    
    // Запускаем карту
    initMap();
</script>
</body>
</html>'''
    
    return html

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)