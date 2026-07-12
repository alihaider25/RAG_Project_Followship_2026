document.getElementById("upload-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const fileInput = document.getElementById("file-input");
    const statusDiv = document.getElementById("upload-status");

    if (!fileInput.files.length) return;

    const files = Array.from(fileInput.files);
    statusDiv.innerHTML = "";

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append("file", file);

        const lineId = `upload-line-${i}`;
        statusDiv.innerHTML += `<div id="${lineId}" class="text-muted"><span class="spinner-border spinner-border-sm"></span> Uploading ${file.name}...</div>`;

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                document.getElementById(lineId).innerHTML =
                    `<span class="text-success">✓ ${data.filename} (${data.chunk_count} chunks)</span>`;
            } else {
                document.getElementById(lineId).innerHTML =
                    `<span class="text-danger">✗ ${file.name}: ${data.error}</span>`;
            }
        } catch (err) {
            document.getElementById(lineId).innerHTML =
                `<span class="text-danger">✗ ${file.name}: ${err}</span>`;
        }
    }

    setTimeout(() => location.reload(), 1200);
});

// Delete document
document.addEventListener("click", async function (e) {
    if (e.target.closest(".delete-btn")) {
        const btn = e.target.closest(".delete-btn");
        const docId = btn.dataset.id;

        if (!confirm("Delete this document?")) return;

        const response = await fetch(`/documents/${docId}/delete`, { method: "DELETE" });
        if (response.ok) {
            document.getElementById(`doc-row-${docId}`).remove();
        }
    }
});