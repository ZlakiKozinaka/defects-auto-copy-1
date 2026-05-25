(function () {
    const RU_TO_EN_MAP = {
        "Й": "Q", "Ц": "W", "У": "E", "К": "R", "Е": "T", "Н": "Y",
        "Г": "U", "Ш": "I", "Щ": "O", "З": "P",
        "Ф": "A", "Ы": "S", "В": "D", "А": "F", "П": "G",
        "Р": "H", "О": "J", "Л": "K", "Д": "L",
        "Я": "Z", "Ч": "X", "С": "C", "М": "V", "И": "B", "Т": "N", "Ь": "M",
        "Х": "[", "Ъ": "]", "Б": ",", "Ю": "."
    };

    function convertRussianLayoutToEnglish(value) {
        return (value || "")
            .toUpperCase()
            .split("")
            .map((char) => RU_TO_EN_MAP[char] || char)
            .join("");
    }

    function normalizeInputValue(input, forceUppercase) {
        const originalValue = input.value || "";
        const convertedValue = convertRussianLayoutToEnglish(originalValue);
        const normalizedValue = forceUppercase ? convertedValue.toUpperCase() : convertedValue;

        if (normalizedValue !== originalValue) {
            const cursorPos = input.selectionStart;
            input.value = normalizedValue;
            if (typeof cursorPos === "number") {
                input.setSelectionRange(cursorPos, cursorPos);
            }
        }
    }

    window.initScannerLayoutFix = function initScannerLayoutFix(selectors, options = {}) {
        const forceUppercase = options.forceUppercase !== false;

        (selectors || []).forEach((selector) => {
            const input = document.querySelector(selector);
            if (!input || input.disabled) return;

            input.addEventListener("input", function () {
                normalizeInputValue(input, forceUppercase);
            });

            input.addEventListener("paste", function () {
                setTimeout(function () {
                    normalizeInputValue(input, forceUppercase);
                }, 0);
            });
        });
    };
})();