const fileInput = document.getElementById("file");
const fileName = document.getElementById("fileName");
const form = document.getElementById("uploadForm");

// Show file name
fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
    } else {
        fileName.textContent = "No file selected";
    }
});

// Handle submit
form.addEventListener("submit", function (e) {
    e.preventDefault(); // 🚨 VERY IMPORTANT

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("resume", file); // must match backend

    fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
            document.getElementById("result").innerHTML = `
        <h3>Score: ${data.score}</h3>

        <p><b>Found Skills:</b> ${data.found_keywords.join(", ")}</p>
        <p><b>Missing Skills:</b> ${data.missing_keywords.join(", ")}</p>

        <p><b>Missing Sections:</b> ${data.missing_sections.join(", ")}</p>

        <p><b>Suggestions:</b><br>${data.suggestions.join("<br>")}</p>
    `;

    })
    .catch(err => {
        console.error(err);
        alert("Error occurred");
    });
});