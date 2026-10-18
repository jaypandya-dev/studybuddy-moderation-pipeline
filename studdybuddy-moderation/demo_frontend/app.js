const API_BASE = "http://127.0.0.1:8000";

const resourceType = document.getElementById("resourceType");
const fileInput = document.getElementById("fileInput");
const moderateButton = document.getElementById("moderateButton");

const progressCard = document.getElementById("progressCard");
const resultCard = document.getElementById("resultCard");

const progressBar = document.getElementById("progressBar");
const progressPercent = document.getElementById("progressPercent");
const progressStatus = document.getElementById("progressStatus");
const progressDetails = document.getElementById("progressDetails");

const decision = document.getElementById("decision");
const educationalValue = document.getElementById("educationalValue");
const harmfulValue = document.getElementById("harmfulValue");
const categoryValue = document.getElementById("categoryValue");
const reasonValue = document.getElementById("reasonValue");
const descriptionValue = document.getElementById("descriptionValue");

const ocrSection = document.getElementById("ocrSection");
const ocrValue = document.getElementById("ocrValue");

const errorMessage = document.getElementById("errorMessage");

const apiStatus = document.getElementById("apiStatus");
const qwenStatus = document.getElementById("qwenStatus");
const vlmStatus = document.getElementById("vlmStatus");


/* -------------------------------------------------------
   Resource type
------------------------------------------------------- */

resourceType.addEventListener("change", () => {
    if (resourceType.value === "pdf") {
        fileInput.accept = ".pdf";
    } else {
        fileInput.accept = "image/png,image/jpeg,image/webp";
    }

    fileInput.value = "";
});


/* -------------------------------------------------------
   Main moderation button
------------------------------------------------------- */

moderateButton.addEventListener("click", async () => {
    clearError();
    hideResult();

    const file = fileInput.files[0];

    if (!file) {
        showError("Please select a file first.");
        return;
    }

    moderateButton.disabled = true;

    try {
        if (resourceType.value === "pdf") {
            await moderatePdf(file);
        } else {
            await moderateImage(file);
        }
    } catch (error) {
        console.error(error);
        showError(error.message || "Moderation failed.");
    } finally {
        moderateButton.disabled = false;
    }
});


/* -------------------------------------------------------
   PDF moderation
------------------------------------------------------- */

async function moderatePdf(file) {
    showProgress();

    updateProgress(
        0,
        "Uploading...",
        ""
    );

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
        `${API_BASE}/moderate`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("Failed to upload PDF.");
    }

    const data = await response.json();

    if (!data.success) {
        const reason =
            data.validation?.reason ||
            "PDF validation failed.";

        throw new Error(reason);
    }

    const jobId = data.job_id;

    updateProgress(
        0,
        "Queued",
        `Job ID: ${jobId}`
    );

    await pollPdfJob(jobId);
}


async function pollPdfJob(jobId) {
    while (true) {
        const response = await fetch(
            `${API_BASE}/moderate/${jobId}`
        );

        if (!response.ok) {
            throw new Error(
                "Failed to fetch PDF moderation status."
            );
        }

        const job = await response.json();

        if (!job.success) {
            throw new Error(
                "Moderation job not found."
            );
        }

        const progress = job.progress || {};

        updateProgress(
            progress.percentage ?? 0,
            formatPdfStatus(job.status),
            buildPdfDetails(job)
        );

        if (job.status === "FAILED") {
            throw new Error(
                job.error || "PDF moderation failed."
            );
        }

        if (job.status === "COMPLETED") {
            updateProgress(
                100,
                "Completed",
                buildPdfDetails(job)
            );

            showPdfResult(job);
            return;
        }

        await sleep(1500);
    }
}


function formatPdfStatus(status) {
    switch (status) {
        case "QUEUED":
            return "Queued";
        case "RUNNING":
            return "Moderating";
        case "COMPLETED":
            return "Completed";
        case "FAILED":
            return "Failed";
        default:
            return status || "Processing";
    }
}


function buildPdfDetails(job) {
    const details = [];
    const progress = job.progress || {};
    const result = job.result || {};

    if (
        progress.processed_chunks !== undefined &&
        progress.total_chunks !== undefined
    ) {
        details.push(
            `Chunks: ${progress.processed_chunks} / ${progress.total_chunks}`
        );
    }

    if (result.page_count !== undefined) {
        details.push(
            `Pages: ${result.page_count}`
        );
    }

    if (result.pages_with_text !== undefined) {
        details.push(
            `Text pages: ${result.pages_with_text}`
        );
    }

    if (result.pages_ocr !== undefined) {
        details.push(
            `OCR pages: ${result.pages_ocr}`
        );
    }

    return details.join("<br>");
}


/* -------------------------------------------------------
   PDF result
------------------------------------------------------- */

function showPdfResult(job) {
    hideProgress();

    const result = job.result;

    if (!result) {
        throw new Error(
            "PDF moderation result is missing."
        );
    }

    const chunks = result.chunks || [];

    /*
     * Use the same page-role logic as the backend resource
     * decision so the frontend reflects the actual PDF policy.
     */

    const nonContentRoles = new Set([
        "front_matter",
        "metadata",
        "references",
        "index",
        "glossary"
    ]);

    const substantiveChunks = chunks.filter(
        chunk =>
            !nonContentRoles.has(
                chunk.page_role || "content"
            )
    );

    const educationalChunks = substantiveChunks.filter(
        chunk =>
            chunk.moderation?.educational === true
    );

    const harmfulChunks = chunks.filter(
        chunk =>
            chunk.moderation?.harmful === true
    );

    const educationalCount =
        educationalChunks.length;

    const substantiveCount =
        substantiveChunks.length;

    const educationalCoverage =
        substantiveCount > 0
            ? educationalCount / substantiveCount
            : 0;

    const harmful =
        harmfulChunks.length > 0;

    const educational =
        educationalCount > 0 &&
        educationalCoverage >= 0.75;

    const harmfulCategories = [
        ...new Set(
            harmfulChunks
                .map(
                    chunk =>
                        chunk.moderation?.category
                )
                .filter(Boolean)
        )
    ];

    let category = "none";

    if (harmfulCategories.length > 0) {
        category = harmfulCategories.join(", ");
    } else if (!educational) {
        category = "non_educational";
    }

    let reason;

    if (result.reason) {
        reason = formatResourceReason(result.reason);
    } else if (harmful) {
        reason = "Harmful content was detected in the PDF.";
    } else if (educationalCount === 0) {
        reason = "The PDF contains no substantive educational content.";
    } else {
        reason =
            "The PDF does not meet the required educational coverage threshold.";
    }

    showBasicResult(
        result.decision,
        educational,
        harmful,
        category,
        reason
    );

    descriptionValue.textContent =
        `PDF processed: ${result.page_count ?? "-"} pages, ` +
        `${chunks.length} chunks. ` +
        `Educational coverage: ` +
        `${Math.round(educationalCoverage * 100)}%.`;

    ocrSection.classList.add("hidden");

    showResult();
}


function formatResourceReason(reason) {
    const reasons = {
        "harmful_content_detected":
            "Harmful content was detected in the PDF.",

        "no_educational_content":
            "The PDF contains no substantive educational content.",

        "insufficient_educational_coverage":
            "The PDF does not meet the required educational coverage threshold.",

        "sufficient_educational_coverage":
            "The PDF contains sufficient educational content."
    };

    return reasons[reason] || reason;
}


/* -------------------------------------------------------
   Image moderation
------------------------------------------------------- */

async function moderateImage(file) {
    showProgress();

    updateProgress(
        0,
        "Analyzing image...",
        "SmolVLM2 → OCR → Qwen3"
    );

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
        `${API_BASE}/moderate-image`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error(
            "Image moderation request failed."
        );
    }

    const data = await response.json();

    if (!data.success) {
        const reason =
            data.validation?.reason ||
            "Image validation failed.";

        throw new Error(reason);
    }

    updateProgress(
        100,
        "Completed",
        "Image moderation finished."
    );

    showImageResult(data.result);
}


/* -------------------------------------------------------
   Image result
------------------------------------------------------- */

function showImageResult(result) {
    hideProgress();

    const moderation =
        result.moderation || {};

    showBasicResult(
        result.decision,
        moderation.educational,
        moderation.harmful,
        moderation.category,
        moderation.reason
    );

    descriptionValue.textContent =
        result.description ||
        "No description available.";

    if (result.ocr_text) {
        ocrValue.textContent = result.ocr_text;
        ocrSection.classList.remove("hidden");
    } else {
        ocrSection.classList.add("hidden");
    }

    showResult();
}


/* -------------------------------------------------------
   Common result rendering
------------------------------------------------------- */

function showBasicResult(
    finalDecision,
    educational,
    harmful,
    category,
    reason
) {
    decision.textContent =
        finalDecision || "UNKNOWN";

    educationalValue.textContent =
        formatBoolean(educational);

    harmfulValue.textContent =
        formatBoolean(harmful);

    categoryValue.textContent =
        category || "-";

    reasonValue.textContent =
        reason || "No reason provided.";
}


function formatBoolean(value) {
    if (value === true) {
        return "YES";
    }

    if (value === false) {
        return "NO";
    }

    return "-";
}


/* -------------------------------------------------------
   Progress UI
------------------------------------------------------- */

function showProgress() {
    progressCard.classList.remove("hidden");
}


function hideProgress() {
    progressCard.classList.add("hidden");
}


function updateProgress(
    percent,
    status,
    details
) {
    const safePercent = Math.max(
        0,
        Math.min(100, Number(percent) || 0)
    );

    progressBar.style.width =
        `${safePercent}%`;

    progressPercent.textContent =
        `${Math.round(safePercent)}%`;

    progressStatus.textContent =
        status || "Processing";

    progressDetails.innerHTML =
        details || "";
}


/* -------------------------------------------------------
   Result UI
------------------------------------------------------- */

function showResult() {
    resultCard.classList.remove("hidden");
}


function hideResult() {
    resultCard.classList.add("hidden");
}


/* -------------------------------------------------------
   Error UI
------------------------------------------------------- */

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}


function clearError() {
    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
}


/* -------------------------------------------------------
   Utility
------------------------------------------------------- */

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


/* -------------------------------------------------------
   Health status
------------------------------------------------------- */

async function checkHealth() {

    /* FastAPI */

    try {
        const response = await fetch(
            `${API_BASE}/`
        );

        setStatus(
            apiStatus,
            response.ok ? "Online" : "Offline",
            response.ok
        );
    } catch {
        setStatus(
            apiStatus,
            "Offline",
            false
        );
    }


    /* Qwen3 */

    try {
        const response = await fetch(
            "http://127.0.0.1:8080/health"
        );

        setStatus(
            qwenStatus,
            response.ok ? "Online" : "Offline",
            response.ok
        );
    } catch {
        setStatus(
            qwenStatus,
            "Offline",
            false
        );
    }


    /* SmolVLM2 */

    try {
        const response = await fetch(
            "http://127.0.0.1:8081/health"
        );

        setStatus(
            vlmStatus,
            response.ok ? "Online" : "Offline",
            response.ok
        );
    } catch {
        setStatus(
            vlmStatus,
            "Offline",
            false
        );
    }
}


function setStatus(
    element,
    text,
    online = false
) {
    element.textContent = text;

    element.classList.toggle(
        "online",
        online
    );

    element.classList.toggle(
        "offline",
        !online
    );
}


/* -------------------------------------------------------
   Initial status check
------------------------------------------------------- */

checkHealth();