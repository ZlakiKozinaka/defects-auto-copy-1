let VIN_PREFIXES_CACHE = null;

async function loadVinPrefixes() {
    if (VIN_PREFIXES_CACHE) {
        return VIN_PREFIXES_CACHE;
    }

    const response = await fetch("/vin-prefixes-api/");
    VIN_PREFIXES_CACHE = await response.json();

    return VIN_PREFIXES_CACHE;
}

function fixRussianKeyboardVin(value) {
    const map = {
        "Й": "Q", "Ц": "W", "У": "E", "К": "R", "Е": "T", "Н": "Y",
        "Г": "U", "Ш": "I", "Щ": "O", "З": "P",
        "Ф": "A", "Ы": "S", "В": "D", "А": "F", "П": "G",
        "Р": "H", "О": "J", "Л": "K", "Д": "L",
        "Я": "Z", "Ч": "X", "С": "C", "М": "V",
        "И": "B", "Т": "N", "Ь": "M"
    };

    return (value || "")
        .toUpperCase()
        .split("")
        .map(char => map[char] || char)
        .join("");
}

function renderVinBoxes(vinBoxes, value) {
    vinBoxes.innerHTML = "";

    const vin = (value || "").padEnd(17, " ");

    for (let i = 0; i < 17; i++) {
        const cell = document.createElement("div");
        cell.className = "vin-cell";
        cell.textContent = vin[i] === " " ? "" : vin[i];
        vinBoxes.appendChild(cell);
    }
}

function setModelByText(modelSelect, modelName) {
    if (!modelSelect || !modelName) return;

    const normalizedModelName = modelName.trim().toUpperCase();

    for (let i = 0; i < modelSelect.options.length; i++) {
        const optionText = modelSelect.options[i].text.trim().toUpperCase();

        if (optionText === normalizedModelName) {
            modelSelect.selectedIndex = i;
            return;
        }
    }

    const newOption = document.createElement("option");
    newOption.value = "";
    newOption.text = modelName;
    newOption.selected = true;
    modelSelect.appendChild(newOption);
}

async function detectModelByFullVin(vin) {
    const cleanVin = (vin || "").trim().toUpperCase();

    if (cleanVin.length !== 17) {
        return null;
    }

    const response = await fetch(`/vin-model-api/?vin=${encodeURIComponent(cleanVin)}`);
    const data = await response.json();

    if (data.found && data.model) {
        return data.model;
    }

    return null;
}

async function detectModelByPrefix(vin) {
    const cleanVin = (vin || "").trim().toUpperCase();

    if (!cleanVin) {
        return null;
    }

    const prefixes = await loadVinPrefixes();

    for (const item of prefixes) {
        if (cleanVin.startsWith(item.prefix)) {
            return item.model;
        }
    }

    return null;
}

async function updateModelFromVin(vinInput, modelSelect, vinBoxes) {
    const currentVin = fixRussianKeyboardVin(vinInput.value).slice(0, 17);
    vinInput.value = currentVin;

    let detectedModel = null;

    if (currentVin.length === 17) {
        detectedModel = await detectModelByFullVin(currentVin);
    }

    if (!detectedModel) {
        detectedModel = await detectModelByPrefix(currentVin);
    }

    if (detectedModel) {
        setModelByText(modelSelect, detectedModel);
    }

    renderVinBoxes(vinBoxes, currentVin);
}

async function updateVinPrefixFromModel(vinInput, modelSelect, vinBoxes) {
    const selectedText = modelSelect.options[modelSelect.selectedIndex]?.text;

    if (!selectedText) {
        renderVinBoxes(vinBoxes, vinInput.value);
        return;
    }

    const prefixes = await loadVinPrefixes();

    const foundPrefix = prefixes.find(item =>
        item.model.trim().toUpperCase() === selectedText.trim().toUpperCase()
    );

    if (!foundPrefix) {
        renderVinBoxes(vinBoxes, vinInput.value);
        return;
    }

    vinInput.value = foundPrefix.prefix;
    renderVinBoxes(vinBoxes, vinInput.value);
}

function initVinLogic(vinInputId, modelSelectId, vinBoxesId, containerSelector = null) {
    const container = containerSelector
        ? document.querySelector(containerSelector)
        : document;

    if (!container) return;

    const vinInput = container.querySelector("#" + vinInputId);
    const modelSelect = container.querySelector("#" + modelSelectId);
    const vinBoxes = document.getElementById(vinBoxesId);

    if (!vinInput || !modelSelect || !vinBoxes) return;

    vinInput.addEventListener("input", function () {
        updateModelFromVin(vinInput, modelSelect, vinBoxes);
    });

    vinInput.addEventListener("paste", function () {
        setTimeout(() => {
            updateModelFromVin(vinInput, modelSelect, vinBoxes);
        }, 0);
    });

    modelSelect.addEventListener("change", function () {
        updateVinPrefixFromModel(vinInput, modelSelect, vinBoxes);
    });

    renderVinBoxes(vinBoxes, vinInput.value);
    updateModelFromVin(vinInput, modelSelect, vinBoxes);
}