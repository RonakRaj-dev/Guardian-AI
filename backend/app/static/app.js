/*
 * GuardianAI Dashboard Client Application
 * Real-time WebSockets, Multi-Agent UI Updates, Floor Plan Rendering & ESP32 Hardware Simulator
 */

let ws = null;
let currentIncident = null;
let currentTelemetry = null;

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;

    console.log(`Connecting to WebSocket: ${wsUrl}`);
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("WebSocket connected to GuardianAI backend.");
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "INITIAL_STATE" || data.type === "TELEMETRY_UPDATE") {
                if (data.telemetry) updateTelemetryUI(data.telemetry);
                if (data.incident) updateIncidentAndAgentsUI(data.incident);
            }
        } catch (e) {
            console.error("Error parsing WS message:", e);
        }
    };

    ws.onclose = () => {
        console.warn("WebSocket connection closed. Reconnecting in 3s...");
        setTimeout(initWebSocket, 3000);
    };
}

function updateTelemetryUI(t) {
    currentTelemetry = t;

    // 1. DHT22 Temp & Humidity
    const tempVal = document.getElementById("temp-value");
    const humidityText = document.getElementById("humidity-text");
    if (tempVal) tempVal.innerHTML = `${(t.temperature || 32.5).toFixed(1)} <span class="text-xs font-normal text-slate-400">°C</span>`;
    if (humidityText) humidityText.innerHTML = `<i data-lucide="droplet" class="w-3 h-3 text-cyan-400"></i> Humidity: <span class="text-slate-200 font-semibold">${(t.humidity || 67.5).toFixed(1)} %</span>`;

    // 2. MQ2 Smoke ADC (0 - 4095)
    const mq2Val = document.getElementById("mq2-value");
    const mq2Bar = document.getElementById("mq2-bar");
    const mq2Status = document.getElementById("mq2-status");
    const mq2Raw = t.mq2_raw || 180;
    if (mq2Val) mq2Val.innerHTML = `${mq2Raw} <span class="text-xs font-normal text-slate-400">/4095</span>`;
    if (mq2Bar) mq2Bar.style.width = `${Math.min(100, (mq2Raw / 4095) * 100)}%`;
    if (mq2Status) {
        if (mq2Raw > 1200) {
            mq2Bar.className = "bg-rose-500 h-full rounded-full transition-all duration-500";
            mq2Status.innerHTML = `<span class="text-rose-400 font-bold">Elevated Smoke (${mq2Raw})</span>`;
        } else {
            mq2Bar.className = "bg-amber-500 h-full rounded-full transition-all duration-500";
            mq2Status.textContent = "Nominal Air Level";
        }
    }

    // 3. MQ135 Air Quality ADC (0 - 4095)
    const mq135Val = document.getElementById("mq135-value");
    const mq135Bar = document.getElementById("mq135-bar");
    const mq135Status = document.getElementById("mq135-status");
    const mq135Raw = t.mq135_raw || 210;
    if (mq135Val) mq135Val.innerHTML = `${mq135Raw} <span class="text-xs font-normal text-slate-400">/4095</span>`;
    if (mq135Bar) mq135Bar.style.width = `${Math.min(100, (mq135Raw / 4095) * 100)}%`;
    if (mq135Status) {
        if (mq135Raw > 1500) {
            mq135Bar.className = "bg-purple-500 h-full rounded-full transition-all duration-500";
            mq135Status.innerHTML = `<span class="text-purple-400 font-bold">Toxic Air Warning (${mq135Raw})</span>`;
        } else {
            mq135Bar.className = "bg-emerald-500 h-full rounded-full transition-all duration-500";
            mq135Status.textContent = "Fresh Air Quality";
        }
    }

    // 4. Water Level Sensor ADC (0 - 4095)
    const waterVal = document.getElementById("water-value");
    const waterBar = document.getElementById("water-bar");
    const waterStatus = document.getElementById("water-status");
    const waterRaw = t.water_raw || 20;
    if (waterVal) waterVal.innerHTML = `${waterRaw} <span class="text-xs font-normal text-slate-400">/4095</span>`;
    if (waterBar) waterBar.style.width = `${Math.min(100, (waterRaw / 4095) * 100)}%`;
    if (waterStatus) {
        if (waterRaw > 1500) {
            waterBar.className = "bg-blue-500 h-full rounded-full transition-all duration-500";
            waterStatus.innerHTML = `<span class="text-blue-400 font-bold">Flood Warning (${waterRaw})</span>`;
        } else {
            waterBar.className = "bg-blue-500 h-full rounded-full transition-all duration-500";
            waterStatus.textContent = "No Flood Detected";
        }
    }

    // 5. MPU6050 3-Axis Accel
    const ax = (t.mpu_ax !== undefined) ? t.mpu_ax : 0.12;
    const ay = (t.mpu_ay !== undefined) ? t.mpu_ay : 0.05;
    const az = (t.mpu_az !== undefined) ? t.mpu_az : 0.98;
    const totalG = t.vibration_g || Math.sqrt(ax*ax + ay*ay + az*az);

    const mpuTotal = document.getElementById("mpu-total-g");
    const mpuAxes = document.getElementById("mpu-axes");
    if (mpuTotal) mpuTotal.innerHTML = `${totalG.toFixed(2)} <span class="text-xs font-normal text-slate-400">G</span>`;
    if (mpuAxes) mpuAxes.textContent = `AX: ${ax.toFixed(2)} | AY: ${ay.toFixed(2)} | AZ: ${az.toFixed(2)}`;

    // 6. GPS NEO-6M & SIM800L Headers
    const gpsLat = t.gps_lat || 20.2961;
    const gpsLon = t.gps_lon || 85.8245;
    const headerGps = document.getElementById("header-gps-text");
    if (headerGps) headerGps.textContent = `NEO-6M GPS: ${gpsLat.toFixed(4)}, ${gpsLon.toFixed(4)}`;

    const sim800lStatus = t.sim800l_status || "NETWORK_FOUND";
    const sim800lText = document.getElementById("sim800l-text");
    if (sim800lText) sim800lText.textContent = `SIM800L: ${sim800lStatus}`;

    // Actuator Badges
    const buzzerBadge = document.getElementById("buzzer-badge");
    const ledBadge = document.getElementById("led-badge");
    const actuatorStatus = document.getElementById("actuator-status");

    const buzzerOn = (t.buzzer_state === "ON");
    const ledColor = t.led_state || "GREEN";

    if (buzzerBadge) {
        buzzerBadge.textContent = `Buzzer: ${buzzerOn ? 'ACTIVE ON' : 'OFF'}`;
        buzzerBadge.className = buzzerOn ? "px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 animate-pulse" : "px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700";
    }

    if (ledBadge) {
        ledBadge.textContent = `LED: ${ledColor}`;
        ledBadge.className = (ledColor === 'RED') ? "px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800" : "px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800";
    }

    if (actuatorStatus) {
        if (buzzerOn || ledColor === 'RED') {
            actuatorStatus.textContent = "ALARM ACTIVE";
            actuatorStatus.className = "text-lg font-bold font-outfit text-rose-500 mt-0.5 animate-pulse";
        } else {
            actuatorStatus.textContent = "NOMINAL";
            actuatorStatus.className = "text-lg font-bold font-outfit text-emerald-400 mt-0.5";
        }
    }

    if (window.lucide) lucide.createIcons();
}

function updateIncidentAndAgentsUI(incident) {
    currentIncident = incident;

    const statusBadge = document.getElementById("system-status-badge");
    const statusText = document.getElementById("system-status-text");
    const floorplanAlert = document.getElementById("floorplan-alert-overlay");
    const overlayTitle = document.getElementById("overlay-title");
    const overlaySub = document.getElementById("overlay-sub");
    const svgRoom = document.getElementById("svg-room-204");
    const svgSensorPin = document.getElementById("svg-sensor-pin");
    const svgEvacPath = document.getElementById("svg-evac-path");

    const status = incident.status;
    const isEmergency = (status === "VERIFIED_EMERGENCY");
    const isFalseAlarm = (status === "FALSE_ALARM");

    if (isEmergency) {
        statusBadge.className = "px-3 py-1.5 rounded-full text-xs font-semibold bg-rose-950/80 border border-rose-500/50 text-rose-400 flex items-center space-x-2 animate-pulse";
        statusText.textContent = `🚨 CONFIRMED DISASTER (${incident.confidence.toFixed(0)}% CONFIDENCE)`;

        svgRoom.setAttribute("fill", "#450a0a");
        svgRoom.setAttribute("stroke", "#f43f5e");
        svgSensorPin.setAttribute("fill", "#f43f5e");
        svgEvacPath.setAttribute("stroke", "#10b981");
        svgEvacPath.setAttribute("class", "animate-evac-flow opacity-100");

        overlayTitle.textContent = `ACTIVE DISASTER (${incident.disaster_type || 'FIRE'}) IN ROOM 204`;
        overlayTitle.className = "text-xs font-bold text-rose-400";
        overlaySub.textContent = `EVACUATE via ${incident.evacuation_route} immediately!`;

    } else if (isFalseAlarm) {
        statusBadge.className = "px-3 py-1.5 rounded-full text-xs font-semibold bg-amber-950/80 border border-amber-500/50 text-amber-400 flex items-center space-x-2";
        statusText.textContent = "⚠️ FALSE ALARM PREVENTED";

        svgRoom.setAttribute("fill", "#17120a");
        svgRoom.setAttribute("stroke", "#f59e0b");
        svgSensorPin.setAttribute("fill", "#f59e0b");
        svgEvacPath.setAttribute("stroke", "#64748b");
        svgEvacPath.setAttribute("class", "opacity-30");

        overlayTitle.textContent = "False Alarm Detected (Smoke only)";
        overlayTitle.className = "text-xs font-bold text-amber-400";
        overlaySub.textContent = "No thermal jump or flame; alarm suppressed.";

    } else {
        statusBadge.className = "px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 flex items-center space-x-2";
        statusText.textContent = "SYSTEM NORMAL";

        svgRoom.setAttribute("fill", "#0f172a");
        svgRoom.setAttribute("stroke", "#334155");
        svgSensorPin.setAttribute("fill", "#10b981");
        svgEvacPath.setAttribute("stroke", "#10b981");
        svgEvacPath.setAttribute("class", "animate-evac-flow opacity-40");

        overlayTitle.textContent = "All Corridors Clear";
        overlayTitle.className = "text-xs font-semibold text-slate-200";
        overlaySub.textContent = "Proceed with normal building occupancy";
    }

    // Update Agent Cards
    const logs = incident.agents_log || [];
    logs.forEach((log, index) => {
        const card = document.getElementById(`agent-card-${index}`);
        const badge = document.getElementById(`agent-badge-${index}`);
        const desc = document.getElementById(`agent-desc-${index}`);

        if (card && badge && desc) {
            badge.textContent = log.status || "OK";
            
            if (isEmergency) {
                card.className = "agent-card p-3 rounded-xl active-alert border flex items-start space-x-3";
                badge.className = "text-[10px] px-2 py-0.5 rounded font-mono bg-rose-950 text-rose-400 border border-rose-800";
            } else if (isFalseAlarm && index === 1) {
                card.className = "agent-card p-3 rounded-xl border border-amber-500/50 bg-amber-950/30 flex items-start space-x-3";
                badge.className = "text-[10px] px-2 py-0.5 rounded font-mono bg-amber-950 text-amber-400 border border-amber-800";
            } else {
                card.className = "agent-card p-3 rounded-xl bg-slate-900/70 border border-slate-800 flex items-start space-x-3";
                badge.className = "text-[10px] px-2 py-0.5 rounded font-mono bg-slate-800 text-slate-400";
            }

            desc.textContent = log.summary || log.rationale || log.guidance || log.assessment || "Completed execution.";
        }
    });

    const timer = document.getElementById("pipeline-timer");
    if (timer && incident.pipeline_duration_ms) {
        timer.textContent = `Latency: ${incident.pipeline_duration_ms} ms`;
    }
}

// Modal Controllers
function openHardwareSimModal() {
    document.getElementById("modal-hardware-sim").classList.remove("hidden");
    document.getElementById("modal-hardware-sim").classList.add("flex");
}

function closeHardwareSimModal() {
    document.getElementById("modal-hardware-sim").classList.remove("flex");
    document.getElementById("modal-hardware-sim").classList.add("hidden");
}

function openReportModal() {
    document.getElementById("modal-report").classList.remove("hidden");
    document.getElementById("modal-report").classList.add("flex");
    const reportContent = document.getElementById("report-content");
    if (currentIncident && currentIncident.report_markdown) {
        reportContent.textContent = currentIncident.report_markdown;
    } else {
        reportContent.textContent = "No active incident report available. Trigger a hardware scenario to synthesize a report!";
    }
}

function closeReportModal() {
    document.getElementById("modal-report").classList.remove("flex");
    document.getElementById("modal-report").classList.add("hidden");
}

function copyReportText() {
    const reportContent = document.getElementById("report-content").textContent;
    navigator.clipboard.writeText(reportContent).then(() => {
        alert("Incident Report copied to clipboard!");
    });
}

function triggerSimPreset(scenario) {
    let payload = {};
    const now = Date.now() / 1000;

    if (scenario === 'SAFE') {
        payload = {
            device_id: 'esp32-guardian-01',
            timestamp: now,
            temperature: 32.5,
            humidity: 67.5,
            mq2_raw: 180,
            mq135_raw: 210,
            water_raw: 20,
            mpu_ax: 0.12,
            mpu_ay: 0.05,
            mpu_az: 0.98,
            gps_lat: 20.2961,
            gps_lon: 85.8245,
            sim800l_status: 'NETWORK_FOUND',
            led_state: 'GREEN',
            buzzer_state: 'OFF',
            flame_detected: false,
            scream_detected: false
        };
    } else if (scenario === 'FALSE_ALARM') {
        payload = {
            device_id: 'esp32-guardian-01',
            timestamp: now,
            temperature: 32.5,
            humidity: 67.5,
            mq2_raw: 1850,
            mq135_raw: 320,
            water_raw: 15,
            mpu_ax: 0.12,
            mpu_ay: 0.05,
            mpu_az: 0.98,
            gps_lat: 20.2961,
            gps_lon: 85.8245,
            sim800l_status: 'NETWORK_FOUND',
            led_state: 'GREEN',
            buzzer_state: 'OFF',
            flame_detected: false,
            scream_detected: false
        };
    } else if (scenario === 'FIRE_EMERGENCY') {
        payload = {
            device_id: 'esp32-guardian-01',
            timestamp: now,
            temperature: 68.5,
            humidity: 22.0,
            mq2_raw: 3450,
            mq135_raw: 1950,
            water_raw: 10,
            mpu_ax: 0.35,
            mpu_ay: 0.28,
            mpu_az: 1.25,
            gps_lat: 20.2961,
            gps_lon: 85.8245,
            sim800l_status: 'SMS_SENT_NETWORK_FOUND',
            led_state: 'RED',
            buzzer_state: 'ON',
            flame_detected: true,
            scream_detected: true
        };
    } else if (scenario === 'FLOOD_EMERGENCY') {
        payload = {
            device_id: 'esp32-guardian-01',
            timestamp: now,
            temperature: 31.0,
            humidity: 92.0,
            mq2_raw: 150,
            mq135_raw: 180,
            water_raw: 3120,
            mpu_ax: 0.10,
            mpu_ay: 0.04,
            mpu_az: 0.99,
            gps_lat: 20.2961,
            gps_lon: 85.8245,
            sim800l_status: 'SMS_SENT_NETWORK_FOUND',
            led_state: 'RED',
            buzzer_state: 'ON',
            flame_detected: false,
            scream_detected: false
        };
    }

    fetch('/api/v1/telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        closeHardwareSimModal();
    })
    .catch(err => console.error("Error triggering sim preset:", err));
}

function triggerManualHardwareAlarm() {
    fetch('/api/v1/hardware/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ buzzer: true, led: 'RED' })
    })
    .then(res => res.json())
    .then(data => alert("Hardware Siren Command Sent: Active Buzzer ON, RED LED"))
    .catch(err => console.error("Error sending hardware command:", err));
}

// Start WebSocket on page load
window.addEventListener("DOMContentLoaded", () => {
    initWebSocket();
});
