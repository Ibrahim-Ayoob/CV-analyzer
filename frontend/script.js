async function analyze() {

    const file = document.getElementById("file").files[0];

    if (!file) {
        alert("Upload file first");
        return;
    }

    const reader = new FileReader();

    reader.onload = async function () {

        const typedarray = new Uint8Array(reader.result);
        const pdf = await pdfjsLib.getDocument(typedarray).promise;

        let text = "";

        for (let i = 1; i <= pdf.numPages; i++) {
            let page = await pdf.getPage(i);
            let content = await page.getTextContent();

            content.items.forEach(item => {
                text += item.str + " ";
            });
        }

        process(text);
    };

    reader.readAsArrayBuffer(file);
}

function process(text) {

    text = text.toLowerCase();

    const skills = ["python", "java", "sql", "cyber security"];
    let score = 0;
    let found = [];

    skills.forEach(skill => {
        if (text.includes(skill)) {
            score += 25;
            found.push(skill);
        }
    });

    document.getElementById("output").innerHTML = `
        <h3>Score: ${score}/100</h3>
        <p>Skills: ${found.join(", ")}</p>
    `;
}
#amro