const ring = document.getElementById("ring");
const stopList = document.getElementById("stop-list");
const message = document.getElementById("message");
const searchResult = document.getElementById("search-result");
const autoButton = document.getElementById("btn-auto");
const positionSelect = document.getElementById("stop-position");
const referenceSelect = document.getElementById("stop-reference");
const referenceLabel = document.getElementById("reference-label");

let autoTimer = null;

async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Ocurrió un error");
    }
    return data;
}

function showMessage(element, text, type) {
    element.textContent = text;
    element.className = `message ${type}`;
}

function renderRing(state) {
    ring.innerHTML = "";
    const radius = ring.clientWidth / 2;
    const busName = state.bus_at ? state.bus_at.name : null;

    state.stops.forEach((stop, index) => {
        const angle = (2 * Math.PI * index) / state.stops.length - Math.PI / 2;
        const element = document.createElement("div");
        element.className = "stop";
        if (stop.name === busName) element.classList.add("active");
        if (stop.name === state.terminal) element.classList.add("terminal");
        element.style.left = `${radius + radius * Math.cos(angle)}px`;
        element.style.top = `${radius + radius * Math.sin(angle)}px`;
        element.innerHTML = `${stop.name === busName ? "🚌 " : ""}${stop.name}<small>${stop.minutes} min</small>`;
        ring.appendChild(element);
    });
}

function renderList(state) {
    stopList.innerHTML = "";
    const busName = state.bus_at ? state.bus_at.name : null;
    state.stops.forEach((stop) => {
        const item = document.createElement("li");
        if (stop.name === busName) item.classList.add("active");
        const label = document.createElement("span");
        label.textContent = `${stop.name} · ${stop.minutes} min${stop.name === state.terminal ? " · terminal" : ""}`;
        const button = document.createElement("button");
        button.textContent = "Eliminar";
        button.addEventListener("click", () => removeStop(stop.name));
        item.append(label, button);
        stopList.appendChild(item);
    });
}

function renderReferences(state) {
    const selected = referenceSelect.value;
    referenceSelect.innerHTML = "";
    state.stops.forEach((stop) => {
        const option = document.createElement("option");
        option.value = stop.name;
        option.textContent = stop.name;
        referenceSelect.appendChild(option);
    });
    if (state.stops.some((stop) => stop.name === selected)) {
        referenceSelect.value = selected;
    }
}

function renderTraverse(container, stopNames) {
    container.innerHTML = "";
    if (stopNames.length === 0) {
        container.textContent = "No hay paradas";
        return;
    }
    stopNames.concat(stopNames[0]).forEach((name, index) => {
        if (index > 0) {
            const arrow = document.createElement("span");
            arrow.className = "arrow";
            arrow.textContent = "→";
            container.appendChild(arrow);
        }
        const chip = document.createElement("span");
        chip.className = "chip";
        if (index === 0 || index === stopNames.length) chip.classList.add("first");
        chip.textContent = name;
        container.appendChild(chip);
    });
}

function render(state) {
    const bus = state.bus_at;
    document.getElementById("route-name").textContent = state.name;
    document.getElementById("stat-size").textContent = state.size;
    document.getElementById("stat-total").textContent = `${state.total_minutes} min`;
    document.getElementById("stat-laps").textContent = state.laps;
    document.getElementById("stat-elapsed").textContent = `${state.elapsed_minutes} min`;
    document.getElementById("current-stop").textContent = bus ? bus.name : "-";
    document.getElementById("ahead-stop").textContent = bus ? bus.stop_ahead : "-";
    document.getElementById("behind-stop").textContent = bus ? bus.stop_behind : "-";
    renderRing(state);
    renderList(state);
    renderReferences(state);
    renderTraverse(document.getElementById("ahead-route"), state.ahead);
    renderTraverse(document.getElementById("behind-route"), state.behind);
}

async function loadRoute() {
    render(await request("/api/route"));
}

async function drive(direction) {
    try {
        render(await request(`/api/bus/${direction}`, { method: "POST" }));
    } catch (error) {
        showMessage(message, error.message, "error");
        stopAuto();
    }
}

async function removeStop(name) {
    try {
        render(await request(`/api/stops/${encodeURIComponent(name)}`, { method: "DELETE" }));
        showMessage(message, `Parada '${name}' eliminada`, "ok");
    } catch (error) {
        showMessage(message, error.message, "error");
    }
}

function stopAuto() {
    clearInterval(autoTimer);
    autoTimer = null;
    autoButton.textContent = "▶ Recorrido automático";
    autoButton.classList.remove("running");
}

autoButton.addEventListener("click", () => {
    if (autoTimer) {
        stopAuto();
        return;
    }
    autoTimer = setInterval(() => drive("ahead"), 1200);
    autoButton.textContent = "■ Detener recorrido";
    autoButton.classList.add("running");
});

document.getElementById("btn-ahead").addEventListener("click", () => drive("ahead"));
document.getElementById("btn-behind").addEventListener("click", () => drive("behind"));

positionSelect.addEventListener("change", () => {
    referenceLabel.classList.toggle("hidden", positionSelect.value !== "after");
});

document.getElementById("stop-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const nameInput = document.getElementById("stop-name");
    try {
        const state = await request("/api/stops", {
            method: "POST",
            body: JSON.stringify({
                name: nameInput.value,
                minutes: document.getElementById("stop-minutes").value,
                position: positionSelect.value,
                reference: referenceSelect.value,
            }),
        });
        render(state);
        showMessage(message, "Parada agregada correctamente", "ok");
        nameInput.value = "";
    } catch (error) {
        showMessage(message, error.message, "error");
    }
});

document.getElementById("search-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("search-name").value.trim();
    try {
        const stop = await request(`/api/stops/${encodeURIComponent(name)}`);
        showMessage(searchResult, `${stop.name} (${stop.minutes} min) · atrás: ${stop.stop_behind} · adelante: ${stop.stop_ahead}`, "ok");
    } catch (error) {
        showMessage(searchResult, error.message, "error");
    }
});

window.addEventListener("resize", loadRoute);

loadRoute();
