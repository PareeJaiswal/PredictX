
const API_BASE_URL = "http://127.0.0.1:5000";

const predictionForm = document.getElementById("predictionForm");
const predictionResult = document.getElementById("predictionResult");

const machineIdField = document.getElementById("machineId");
const machineTypeField = document.getElementById("machineType");

// Machine names used for display in the dropdown.
const machineNames = {
    "MCH-001": "Electric Motor",
    "MCH-002": "Centrifugal Pump",
    "MCH-003": "Industrial Gearbox",
    "MCH-004": "Air Compressor",
    "MCH-005": "Conveyor System",
    "MCH-006": "Hydraulic Press"
};

// Load machines from the database through Flask.
async function loadMachines() {
    if (!machineIdField || !machineTypeField) return;

    try {
        machineIdField.innerHTML =
            '<option value="">Loading machines...</option>';

        const response = await fetch(`${API_BASE_URL}/api/machines`);

        if (!response.ok) {
            throw new Error(`Could not load machines (${response.status})`);
        }

        const data = await response.json();

        // Support different possible Flask response formats.
        const machines = Array.isArray(data)
            ? data
            : data.machines || data.data || [];

        if (!machines.length) {
            throw new Error("No machines were found in the database.");
        }

        machineIdField.innerHTML =
            '<option value="">Select a machine</option>';

        machines.forEach(machine => {
            const machineId = machine.machine_id;
            const machineType = machine.machine_type;

            if (!machineId || !["L", "M", "H"].includes(machineType)) {
                return;
            }

            const machineName =
                machine.name ||
                machine.machine_name ||
                machineNames[machineId] ||
                "Industrial Machine";

            const typeLabel = {
                L: "Low",
                M: "Medium",
                H: "High"
            }[machineType];

            const option = document.createElement("option");

            option.value = machineId;
            option.textContent =
                `${machineId} - ${machineName} (${machineType} - ${typeLabel})`;

            option.dataset.machineType = machineType;

            machineIdField.appendChild(option);
        });

        if (machineIdField.options.length <= 1) {
            throw new Error("No valid machine profiles were returned.");
        }

        machineIdField.disabled = false;

    } catch (error) {
        console.error("Machine loading error:", error);

        machineIdField.innerHTML =
            '<option value="">Unable to load machines</option>';

        machineIdField.disabled = true;

        showResult(
            `Could not load machines: ${error.message}. Make sure Flask is running.`,
            "error"
        );
    }
}

// Automatically set machine type when a machine is selected.
if (machineIdField && machineTypeField) {
    machineIdField.addEventListener("change", function () {
        const selectedOption =
            machineIdField.options[machineIdField.selectedIndex];

        const selectedType =
            selectedOption?.dataset.machineType || "";

        machineTypeField.value = selectedType;
    });
}

// Display messages.
function showResult(message, type) {
    if (!predictionResult) return;

    predictionResult.textContent = message;
    styleResult(type);
}

// Style prediction results.
function styleResult(type) {
    if (!predictionResult) return;

    predictionResult.style.display = "block";
    predictionResult.style.padding = "20px";
    predictionResult.style.marginTop = "20px";
    predictionResult.style.borderRadius = "10px";
    predictionResult.style.border = "1px solid";
    predictionResult.style.lineHeight = "1.6";

    if (type === "success") {
        predictionResult.style.color = "#166534";
        predictionResult.style.backgroundColor = "#f0fdf4";
        predictionResult.style.borderColor = "#bbf7d0";

    } else if (type === "failure" || type === "error") {
        predictionResult.style.color = "#b91c1c";
        predictionResult.style.backgroundColor = "#fef2f2";
        predictionResult.style.borderColor = "#fecaca";

    } else {
        predictionResult.style.color = "#1d4ed8";
        predictionResult.style.backgroundColor = "#eff6ff";
        predictionResult.style.borderColor = "#bfdbfe";
    }
}

// Submit prediction form.
if (predictionForm && predictionResult) {
    predictionForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const machineId = machineIdField.value;
        const machineType = machineTypeField.value;

        const airTemperatureField =
            document.getElementById("airTemperature");

        const processTemperatureField =
            document.getElementById("processTemperature");

        const rotationalSpeedField =
            document.getElementById("rotationalSpeed");

        const torqueField =
            document.getElementById("torque");

        const toolWearField =
            document.getElementById("toolWear");

        if (!machineId) {
            showResult("Please select a machine first.", "error");
            return;
        }

        if (!["L", "M", "H"].includes(machineType)) {
            showResult("Please select a valid machine.", "error");
            return;
        }

        const fields = [
            airTemperatureField,
            processTemperatureField,
            rotationalSpeedField,
            torqueField,
            toolWearField
        ];

        if (fields.some(field => !field)) {
            showResult("One or more sensor input fields are missing.", "error");
            return;
        }

        if (fields.some(field => field.value.trim() === "")) {
            showResult("Please fill in all five sensor readings.", "error");
            return;
        }

        const airTemperature = Number(airTemperatureField.value);
        const processTemperature = Number(processTemperatureField.value);
        const rotationalSpeed = Number(rotationalSpeedField.value);
        const torque = Number(torqueField.value);
        const toolWear = Number(toolWearField.value);

        if (
            !Number.isFinite(airTemperature) ||
            !Number.isFinite(processTemperature) ||
            !Number.isFinite(rotationalSpeed) ||
            !Number.isFinite(torque) ||
            !Number.isFinite(toolWear) ||
            airTemperature <= 0 ||
            processTemperature <= 0 ||
            rotationalSpeed <= 0 ||
            torque < 0 ||
            toolWear < 0
        ) {
            showResult(
                "Enter valid readings. Temperatures and speed must be positive; torque and tool wear cannot be negative.",
                "error"
            );
            return;
        }

        const submitButton =
            predictionForm.querySelector('button[type="submit"]');

        showResult("Analyzing machine condition. Please wait...", "loading");

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Analyzing...";
        }

        try {
            // IMPORTANT: machine_id is now included in the request.
            const response = await fetch(`${API_BASE_URL}/predict`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    machine_id: machineId,
                    machine_type: machineType,
                    air_temperature: airTemperature,
                    process_temperature: processTemperature,
                    rotational_speed: rotationalSpeed,
                    torque: torque,
                    tool_wear: toolWear
                })
            });

            const result = await response.json().catch(() => ({}));

            console.log("Backend response:", result);

            if (!response.ok) {
                throw new Error(
                    result.error || `Server error: ${response.status}`
                );
            }

            const failureDetected =
                Number(result.predicted_failure) === 1;

            predictionResult.replaceChildren();

            const heading = document.createElement("h3");

            heading.textContent = failureDetected
                ? "⚠️ Potential Machine Failure"
                : "✅ No Failure Predicted";

            predictionResult.appendChild(heading);

            const details = [
                ["Machine ID", result.machine_id || machineId],
                ["Machine Type", machineType],
                ["Prediction ID", result.prediction_id],
                [
                    "Status",
                    result.status ||
                    result.prediction_status ||
                    (failureDetected ? "Failure Predicted" : "Healthy")
                ],
                ["Air Temperature", `${airTemperature} K`],
                ["Process Temperature", `${processTemperature} K`],
                ["Rotational Speed", `${rotationalSpeed} RPM`],
                ["Torque", `${torque} Nm`],
                ["Tool Wear", `${toolWear} minutes`]
            ];

            details.forEach(([label, value]) => {
                const paragraph = document.createElement("p");
                const strong = document.createElement("strong");

                strong.textContent = `${label}: `;

                paragraph.appendChild(strong);
                paragraph.appendChild(
                    document.createTextNode(String(value ?? "N/A"))
                );

                predictionResult.appendChild(paragraph);
            });

            styleResult(failureDetected ? "failure" : "success");

            predictionResult.scrollIntoView({
                behavior: "smooth",
                block: "nearest"
            });

        } catch (error) {
            console.error("Prediction error:", error);

            showResult(
                `Prediction failed: ${error.message}. Check that Flask is running.`,
                "error"
            );

        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML =
                    'Analyze Machine Health <span>→</span>';
            }
        }
    });
}


// Display machines in the Dashboard inventory table
function renderDashboardMachines(machines) {

    const tableBody = document.getElementById(
        "dashboardMachineTableBody"
    );

    const machineCount = document.getElementById(
        "dashboardMachineCount"
    );

    if (!tableBody || !machineCount) return;

    tableBody.replaceChildren();

    machineCount.textContent = `${machines.length} Machines`;

    if (machines.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.textContent = "No machines found.";

        row.appendChild(cell);
        tableBody.appendChild(row);

        return;
    }

    machines.forEach(machine => {

        const row = document.createElement("tr");

        const machineCell = document.createElement("td");
        const machineName = document.createElement("strong");
        const machineId = document.createElement("small");

        machineName.textContent = machine.name || "Industrial Machine";
        machineId.textContent = machine.machine_id;

        machineCell.appendChild(machineName);
        machineCell.appendChild(document.createElement("br"));
        machineCell.appendChild(machineId);

        const typeCell = document.createElement("td");
        const typePill = document.createElement("span");

        typePill.className = "type-pill";
        typePill.textContent = machine.machine_type;

        typeCell.appendChild(typePill);

        const airTempCell = document.createElement("td");
        airTempCell.textContent = `${machine.air_temperature} K`;

        const processTempCell = document.createElement("td");
        processTempCell.textContent = `${machine.process_temperature} K`;

        const speedCell = document.createElement("td");
        speedCell.textContent = `${machine.rotational_speed} RPM`;

        const statusCell = document.createElement("td");
        const statusBadge = document.createElement("span");

        const status = machine.status || "Unknown";
        const statusClass = status.toLowerCase().replace(/\s+/g, "-");

        statusBadge.className = `machine-status ${statusClass}`;
        statusBadge.textContent = status;

        statusCell.appendChild(statusBadge);

        row.append(
            machineCell,
            typeCell,
            airTempCell,
            processTempCell,
            speedCell,
            statusCell
        );

        tableBody.appendChild(row);

    });
}

// Load and update dashboard statistics
async function loadDashboardStats() {
    try {
        // Fetch machine data from Flask
        const machineResponse = await fetch(`${API_BASE_URL}/api/machines`);

        if (!machineResponse.ok) {
            throw new Error("Unable to fetch machines");
        }

        const machineData = await machineResponse.json();

        // Extract the machines array
        const machines = Array.isArray(machineData)
            ? machineData
            : machineData.machines || [];
            // Display machines in the inventory table
renderDashboardMachines(machines);

        // Update total machines count
        document.getElementById("totalMachines").textContent =
            machines.length;

            // Count machines based on their current status
const healthyCount = machines.filter(
    machine => machine.status === "Healthy"
).length;

const atRiskCount = machines.filter(
    machine => machine.status === "At Risk"
).length;

// Update dashboard statistics
document.getElementById("healthyMachines").textContent =
    healthyCount;

document.getElementById("machinesAtRisk").textContent =
    atRiskCount;

// Fetch failure alerts
const alertResponse = await fetch(`${API_BASE_URL}/api/alerts`);

if (!alertResponse.ok) {
    throw new Error("Unable to fetch alerts");
}

const alertData = await alertResponse.json();
const alerts = alertData.alerts || [];

// Count unresolved alerts
const activeAlerts = alerts.filter(
    alert => Number(alert.is_resolved) === 0
).length;

// Update failure alerts statistic
document.getElementById("failureAlerts").textContent =
    activeAlerts;

    } catch (error) {
        console.error("Dashboard loading error:", error);
    }
}

// Load machine profiles when the dashboard opens.
loadMachines();
loadDashboardStats();
