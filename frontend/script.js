/* =========================================================
   DISASTERLENS AI
   COMPLETE DYNAMIC FRONTEND
========================================================= */


/* =========================================================
   MOCK DISASTER DATA
========================================================= */

const disasterEvents = [

    {
        id: "FLOOD-VJA-001",
        type: "FLOOD",
        location: "Vijayawada",
        severity: "HIGH",
        confidence: 0.93,
        reportCount: 18,
        status: "ACTIVE",
        detected: "10:42 AM",
        lat: 16.5062,
        lng: 80.6480
    },

    {
        id: "FIRE-GNT-001",
        type: "FIRE",
        location: "Guntur",
        severity: "MEDIUM",
        confidence: 0.81,
        reportCount: 7,
        status: "ACTIVE",
        detected: "10:38 AM",
        lat: 16.3067,
        lng: 80.4365
    },

    {
        id: "EQ-VSK-001",
        type: "EARTHQUAKE",
        location: "Visakhapatnam",
        severity: "HIGH",
        confidence: 0.89,
        reportCount: 12,
        status: "ACTIVE",
        detected: "10:35 AM",
        lat: 17.6868,
        lng: 83.2185
    },

    {
        id: "CYCLONE-KKD-001",
        type: "CYCLONE",
        location: "Kakinada",
        severity: "HIGH",
        confidence: 0.91,
        reportCount: 24,
        status: "ACTIVE",
        detected: "10:29 AM",
        lat: 16.9891,
        lng: 82.2475
    },

    {
        id: "LANDSLIDE-ANP-001",
        type: "LANDSLIDE",
        location: "Anantapur",
        severity: "MEDIUM",
        confidence: 0.76,
        reportCount: 9,
        status: "ACTIVE",
        detected: "10:21 AM",
        lat: 14.6819,
        lng: 77.6006
    },

    {
        id: "DROUGHT-KDP-001",
        type: "DROUGHT",
        location: "Kadapa",
        severity: "LOW",
        confidence: 0.72,
        reportCount: 5,
        status: "RESOLVED",
        detected: "09:58 AM",
        lat: 14.4674,
        lng: 78.8241
    }

];


/* =========================================================
   LIVE FEED DATA
========================================================= */

const liveFeedEvents = [

    {
        type: "FLOOD",
        location: "Vijayawada",
        message: "AI detected multiple flood-related reports.",
        icon: "🌊"
    },

    {
        type: "FIRE",
        location: "Guntur",
        message: "AI detected a possible fire incident.",
        icon: "🔥"
    },

    {
        type: "EARTHQUAKE",
        location: "Visakhapatnam",
        message: "Seismic activity reports detected.",
        icon: "🌍"
    },

    {
        type: "CYCLONE",
        location: "Kakinada",
        message: "Strong weather activity detected.",
        icon: "🌀"
    },

    {
        type: "LANDSLIDE",
        location: "Anantapur",
        message: "Possible landslide activity detected.",
        icon: "⛰️"
    },

    {
        type: "DROUGHT",
        location: "Kadapa",
        message: "Low rainfall conditions detected.",
        icon: "🌾"
    }

];


/* =========================================================
   GET ELEMENTS
========================================================= */

const disasterContainer =
    document.getElementById("disasterContainer");

const activeIncidents =
    document.getElementById("activeIncidents");

const highSeverity =
    document.getElementById("highSeverity");

const totalReports =
    document.getElementById("totalReports");

const aiConfidence =
    document.getElementById("aiConfidence");

const lastUpdated =
    document.getElementById("lastUpdated");

const refreshBtn =
    document.getElementById("refreshBtn");

const searchInput =
    document.getElementById("searchInput");

const severityFilter =
    document.getElementById("severityFilter");

const statusFilter =
    document.getElementById("statusFilter");

const resetFilters =
    document.getElementById("resetFilters");

const resultsCount =
    document.getElementById("resultsCount");

const liveFeed =
    document.getElementById("liveFeed");

const mapRefreshBtn =
    document.getElementById("mapRefreshBtn");

const modeToggle =
    document.getElementById("modeToggle");

const monitorStatus =
    document.getElementById("monitorStatus");

const statusDot =
    document.getElementById("statusDot");


/* =========================================================
   MODAL ELEMENTS
========================================================= */

const incidentModal =
    document.getElementById("incidentModal");

const closeModal =
    document.getElementById("closeModal");

const closeModalBtn =
    document.getElementById("closeModalBtn");

const modalDisasterType =
    document.getElementById("modalDisasterType");

const modalLocation =
    document.getElementById("modalLocation");

const modalStatus =
    document.getElementById("modalStatus");

const modalEventId =
    document.getElementById("modalEventId");

const modalSeverity =
    document.getElementById("modalSeverity");

const modalConfidence =
    document.getElementById("modalConfidence");

const modalReports =
    document.getElementById("modalReports");

const modalDetected =
    document.getElementById("modalDetected");

const modalAnalysis =
    document.getElementById("modalAnalysis");


/* =========================================================
   GLOBAL STATE
========================================================= */

let monitoringMode = "LIVE";

let disasterMap = null;

let mapMarkers = [];

let liveFeedTimer = null;

let clockTimer = null;


/* =========================================================
   FILTER EVENTS
========================================================= */

function getFilteredEvents() {

    const searchValue =
        searchInput.value
            .trim()
            .toLowerCase();

    const selectedSeverity =
        severityFilter.value;

    const selectedStatus =
        statusFilter.value;


    return disasterEvents.filter(event => {

        const matchesSearch =

            event.type
                .toLowerCase()
                .includes(searchValue)

            ||

            event.location
                .toLowerCase()
                .includes(searchValue)

            ||

            event.id
                .toLowerCase()
                .includes(searchValue);


        const matchesSeverity =

            selectedSeverity === "ALL"

            ||

            event.severity === selectedSeverity;


        const matchesStatus =

            selectedStatus === "ALL"

            ||

            event.status === selectedStatus;


        return (
            matchesSearch &&
            matchesSeverity &&
            matchesStatus
        );

    });

}


/* =========================================================
   RENDER DISASTER CARDS
========================================================= */

function renderDisasterEvents() {

    const filteredEvents =
        getFilteredEvents();


    disasterContainer.innerHTML = "";

    resultsCount.textContent =
        filteredEvents.length;


    if (filteredEvents.length === 0) {

        disasterContainer.innerHTML = `

            <div class="no-results">

                <div class="no-results-icon">
                    🔍
                </div>

                <h3>
                    No disaster events found
                </h3>

                <p>
                    Try changing your search or filters.
                </p>

            </div>

        `;

        return;
    }


    filteredEvents.forEach(event => {

        const card =
            document.createElement("div");

        card.className =
            "disaster-card";


        card.setAttribute(
            "data-event-id",
            event.id
        );


        card.innerHTML = `

            <div class="card-top">

                <div class="disaster-type">
                    ${event.type}
                </div>

                <span class="status-badge">
                    ${event.status}
                </span>

            </div>


            <div class="location">
                📍 ${event.location}
            </div>


            <div class="disaster-details">


                <div class="detail-item">

                    <span>
                        Severity
                    </span>

                    <strong
                        class="severity-${event.severity.toLowerCase()}"
                    >
                        ${event.severity}
                    </strong>

                </div>


                <div class="detail-item">

                    <span>
                        AI Confidence
                    </span>

                    <strong>
                        ${Math.round(
                            event.confidence * 100
                        )}%
                    </strong>

                </div>


                <div class="detail-item">

                    <span>
                        Reports
                    </span>

                    <strong>
                        ${event.reportCount}
                    </strong>

                </div>


                <div class="detail-item">

                    <span>
                        Event ID
                    </span>

                    <strong>
                        ${event.id}
                    </strong>

                </div>


            </div>


            <div class="card-footer">

                <span>
                    Detected
                </span>

                <strong>
                    ${event.detected}
                </strong>

            </div>

        `;


        card.addEventListener(
            "click",
            () => openIncidentModal(event)
        );


        disasterContainer.appendChild(card);

    });

}


/* =========================================================
   UPDATE STATISTICS
========================================================= */

function updateStatistics() {

    const activeCount =
        disasterEvents.filter(
            event =>
                event.status === "ACTIVE"
        ).length;


    const highCount =
        disasterEvents.filter(
            event =>
                event.severity === "HIGH"
        ).length;


    const reports =
        disasterEvents.reduce(
            (total, event) =>
                total + event.reportCount,
            0
        );


    const confidence =
        disasterEvents.reduce(
            (total, event) =>
                total + event.confidence,
            0
        ) / disasterEvents.length;


    activeIncidents.textContent =
        activeCount;


    highSeverity.textContent =
        highCount;


    totalReports.textContent =
        reports;


    aiConfidence.textContent =
        Math.round(
            confidence * 100
        ) + "%";

}


/* =========================================================
   UPDATE CLOCK
========================================================= */

function updateTime() {

    const now =
        new Date();


    lastUpdated.textContent =
        now.toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            }
        );

}


/* =========================================================
   MAP INITIALIZATION
========================================================= */

function initializeMap() {

    if (
        typeof L === "undefined"
    ) {

        console.error(
            "Leaflet library failed to load."
        );

        return;

    }


    const mapElement =
        document.getElementById(
            "disasterMap"
        );


    if (!mapElement) {

        console.error(
            "Map element not found."
        );

        return;

    }


    disasterMap =
        L.map(
            "disasterMap"
        ).setView(
            [16.50, 80.64],
            7
        );


    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,

            attribution:
                '&copy; OpenStreetMap contributors'
        }
    ).addTo(
        disasterMap
    );


    updateMapMarkers();


    console.log(
        "Disaster map initialized successfully."
    );

}


/* =========================================================
   GET MARKER COLOR
========================================================= */

function getMarkerColor(severity) {

    if (severity === "HIGH") {
        return "#dc2626";
    }

    if (severity === "MEDIUM") {
        return "#f59e0b";
    }

    return "#16a34a";

}


/* =========================================================
   CREATE CUSTOM MARKER
========================================================= */

function createMarkerIcon(severity) {

    const color =
        getMarkerColor(severity);


    return L.divIcon({

        className: "",

        html: `

            <div
                style="
                    width:22px;
                    height:22px;
                    background:${color};
                    border:3px solid white;
                    border-radius:50%;
                    box-shadow:0 2px 8px rgba(0,0,0,.35);
                "
            ></div>

        `,

        iconSize: [22, 22],

        iconAnchor: [11, 11],

        popupAnchor: [0, -11]

    });

}


/* =========================================================
   UPDATE MAP MARKERS
========================================================= */

function updateMapMarkers() {

    if (!disasterMap) {
        return;
    }


    /* Remove old markers */

    mapMarkers.forEach(marker => {

        disasterMap.removeLayer(marker);

    });


    mapMarkers = [];


    /* Use currently filtered incidents */

    const events =
        getFilteredEvents();


    events.forEach(event => {

        const marker =
            L.marker(
                [event.lat, event.lng],
                {
                    icon:
                        createMarkerIcon(
                            event.severity
                        )
                }
            );


        marker.bindPopup(`

            <div class="map-popup">

                <h3>
                    ${event.type}
                </h3>

                <p>
                    📍 ${event.location}
                </p>

                <p>
                    <strong>Severity:</strong>
                    ${event.severity}
                </p>

                <p>
                    <strong>AI Confidence:</strong>
                    ${Math.round(
                        event.confidence * 100
                    )}%
                </p>

                <p>
                    <strong>Status:</strong>
                    ${event.status}
                </p>

                <p>
                    <strong>Reports:</strong>
                    ${event.reportCount}
                </p>

                <p>
                    <strong>ID:</strong>
                    ${event.id}
                </p>

            </div>

        `);


        marker.on(
            "click",
            () => openIncidentModal(event)
        );


        marker.addTo(
            disasterMap
        );


        mapMarkers.push(marker);

    });

}


/* =========================================================
   REFRESH MAP
========================================================= */

function refreshMap() {

    updateMapMarkers();


    if (disasterMap) {

        setTimeout(
            () => disasterMap.invalidateSize(),
            100
        );

    }

}


/* =========================================================
   OPEN INCIDENT MODAL
========================================================= */

function openIncidentModal(event) {

    modalDisasterType.textContent =
        event.type;

    modalLocation.textContent =
        event.location;

    modalStatus.textContent =
        event.status;

    modalEventId.textContent =
        event.id;

    modalSeverity.textContent =
        event.severity;


    modalSeverity.className =
        "severity-" +
        event.severity.toLowerCase();


    modalConfidence.textContent =
        Math.round(
            event.confidence * 100
        ) + "%";


    modalReports.textContent =
        event.reportCount;


    modalDetected.textContent =
        event.detected;


    modalAnalysis.textContent =

        `AI model detected a ${event.severity.toLowerCase()}-severity ` +
        `${event.type.toLowerCase()} event in ${event.location} ` +
        `with ${Math.round(event.confidence * 100)}% confidence ` +
        `from ${event.reportCount} incoming reports.`;


    incidentModal.classList.add(
        "show"
    );


    document.body.style.overflow =
        "hidden";

}


/* =========================================================
   CLOSE MODAL
========================================================= */

function closeIncidentModal() {

    incidentModal.classList.remove(
        "show"
    );


    document.body.style.overflow =
        "";

}


/* =========================================================
   CREATE LIVE FEED ITEM
========================================================= */

function createFeedItem(event) {

    const item =
        document.createElement("div");


    item.className =
        "feed-item";


    const currentTime =
        new Date().toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            }
        );


    item.innerHTML = `

        <div class="feed-icon">
            ${event.icon}
        </div>


        <div class="feed-content">

            <strong>
                ${event.type} detected
            </strong>

            <p>
                📍 ${event.location}
                — ${event.message}
            </p>

        </div>


        <div class="feed-time">
            ${currentTime}
        </div>

    `;


    return item;

}


/* =========================================================
   INITIALIZE LIVE FEED
========================================================= */

function initializeLiveFeed() {

    liveFeed.innerHTML = "";


    liveFeedEvents
        .slice(0, 5)
        .forEach(event => {

            liveFeed.appendChild(
                createFeedItem(event)
            );

        });

}


/* =========================================================
   SIMULATE LIVE INCIDENT
========================================================= */

function simulateLiveIncident() {

    if (
        monitoringMode !== "LIVE"
    ) {

        return;

    }


    const randomIndex =
        Math.floor(
            Math.random() *
            liveFeedEvents.length
        );


    const event =
        liveFeedEvents[randomIndex];


    const item =
        createFeedItem(event);


    liveFeed.prepend(item);


    while (
        liveFeed.children.length > 5
    ) {

        liveFeed.removeChild(
            liveFeed.lastElementChild
        );

    }


    console.log(
        "New live incident:",
        event.type,
        event.location
    );

}


/* =========================================================
   MONITORING MODE
========================================================= */

function toggleMonitoringMode() {

    if (
        monitoringMode === "LIVE"
    ) {

        monitoringMode = "DEMO";

        monitorStatus.textContent =
            "DEMO MONITORING";

        modeToggle.textContent =
            "LIVE MODE";

        statusDot.classList.add(
            "demo"
        );

    } else {

        monitoringMode = "LIVE";

        monitorStatus.textContent =
            "LIVE MONITORING";

        modeToggle.textContent =
            "DEMO MODE";

        statusDot.classList.remove(
            "demo"
        );

    }


    console.log(
        "Monitoring mode:",
        monitoringMode
    );

}


/* =========================================================
   REFRESH DASHBOARD
========================================================= */

function refreshDashboard() {

    renderDisasterEvents();

    updateStatistics();

    updateTime();

    updateMapMarkers();

}


/* =========================================================
   SEARCH
========================================================= */

searchInput.addEventListener(
    "input",
    () => {

        renderDisasterEvents();

        updateMapMarkers();

    }
);


/* =========================================================
   SEVERITY FILTER
========================================================= */

severityFilter.addEventListener(
    "change",
    () => {

        renderDisasterEvents();

        updateMapMarkers();

    }
);


/* =========================================================
   STATUS FILTER
========================================================= */

statusFilter.addEventListener(
    "change",
    () => {

        renderDisasterEvents();

        updateMapMarkers();

    }
);


/* =========================================================
   RESET FILTERS
========================================================= */

resetFilters.addEventListener(
    "click",
    () => {

        searchInput.value =
            "";

        severityFilter.value =
            "ALL";

        statusFilter.value =
            "ALL";


        renderDisasterEvents();

        updateMapMarkers();

    }
);


/* =========================================================
   REFRESH DASHBOARD BUTTON
========================================================= */

refreshBtn.addEventListener(
    "click",
    () => {

        refreshDashboard();

        console.log(
            "Dashboard refreshed."
        );

    }
);


/* =========================================================
   MAP REFRESH BUTTON
========================================================= */

mapRefreshBtn.addEventListener(
    "click",
    refreshMap
);


/* =========================================================
   MODE BUTTON
========================================================= */

modeToggle.addEventListener(
    "click",
    toggleMonitoringMode
);


/* =========================================================
   MODAL BUTTONS
========================================================= */

closeModal.addEventListener(
    "click",
    closeIncidentModal
);


closeModalBtn.addEventListener(
    "click",
    closeIncidentModal
);


/* =========================================================
   CLOSE MODAL WHEN CLICKING OUTSIDE
========================================================= */

incidentModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            incidentModal
        ) {

            closeIncidentModal();

        }

    }
);


/* =========================================================
   ESC KEY CLOSES MODAL
========================================================= */

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape"
        ) {

            closeIncidentModal();

        }

    }
);


/* =========================================================
   START CLOCK
========================================================= */

clockTimer =
    setInterval(
        updateTime,
        1000
    );


/* =========================================================
   START LIVE FEED
========================================================= */

liveFeedTimer =
    setInterval(
        simulateLiveIncident,
        8000
    );


/* =========================================================
   INITIALIZE APPLICATION
========================================================= */

function initializeApplication() {

    console.log(
        "================================="
    );

    console.log(
        "Starting DisasterLens AI..."
    );


    renderDisasterEvents();

    updateStatistics();

    updateTime();

    initializeLiveFeed();


    /* Initialize map after page rendering */

    initializeMap();


    console.log(
        "DisasterLens AI frontend loaded"
    );


    console.log(
        "Mock disaster events:",
        disasterEvents
    );


    console.log(
        "================================="
    );

}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);

const socket = new WebSocket("ws://172.16.7.53:8000/api/ws");

socket.onopen = function () {
    console.log("Connected to DisasterLens WebSocket");
};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    console.log("New disaster event:", data);

    if (data.type === "DISASTER_EVENT") {
        console.log("Disaster:", data.event.disaster_type);
        console.log("Location:", data.event.location);
        console.log("Severity:", data.event.severity);
        console.log("Confidence:", data.event.confidence);
    }
};

socket.onerror = function (error) {
    console.error("WebSocket error:", error);
};

socket.onclose = function () {
    console.log("WebSocket connection closed");
};