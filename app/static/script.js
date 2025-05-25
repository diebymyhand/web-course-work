const readerWrapper = document.querySelector(".reader-wrapper"),
      form = document.querySelector("#upload-form"),
      fileInp = form.querySelector("input"),
      infoText = form.querySelector(".content p"),
      closeBtn = document.querySelector(".close"),
      copyBtn = document.querySelector(".copy"),
      textarea = document.querySelector(".details textarea");

const qrForm = document.getElementById("generate-form");
const qrInput = document.getElementById("qrData");
const qrPreview = document.getElementById("qrPreview");

const startBtn = document.getElementById("start-camera");
const cameraScan = document.getElementById("camera-scan");
const reader = document.getElementById("reader");
const scan_content = document.getElementById("scan-content");

let scanner;

// генерація QR-коду
document.getElementById("generate-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // блокуємо перезавантаження сторінки

    document.getElementById("qrImage").classList.remove("hidden");


    const qrData = document.getElementById("qrData").value;
    const formData = new FormData();
    formData.append("qr_data", qrData);

    try {
        const response = await fetch("/generate_qr", {
        method: "POST",
        body: formData
        });

        if (!response.ok) {
        alert("Помилка при генерації QR");
        return;
        }

        const blob = await response.blob(); // отримуємо зображення
        const imageURL = URL.createObjectURL(blob); // створюємо тимчасовий URL
        const qrPreview = document.getElementById("qrPreview");

        qrPreview.src = imageURL;
        
        document.getElementById("qrImage").style.display = "block"; // показуємо блок
    } catch (error) {
        console.error("Помилка:", error);
        alert("Щось пішло не так");
    }
});


// === Завантаження QR-коду ===
form.addEventListener("click", () => fileInp.click());

fileInp.addEventListener("change", async (e) => {

    document.getElementById("camera-scan").style.display = "none";
    document.getElementById("content").classList.add("hidden");

    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/scan_qr", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        const data = result.decoded_data;

        if (!data) {
            form.querySelector("img").src = "static/img/error.png";
            textarea.innerText = "Couldn't scan QR Code";
            return;
        }

        textarea.innerText = data;
        form.querySelector("img").src = URL.createObjectURL(file);

    } catch (error) {
        textarea.innerText = "Couldn't scan QR Code";
    }
});

// === Відкриття модального вікна ===
document.getElementById("camera-scan").addEventListener("click", () => startBtn.click());

startBtn.addEventListener("click", async () => {

    document.getElementById("upload-form").style.display = "none";
    
    scan_content.style.display = "none";
    reader.classList.remove("hidden");

    if (!scanner) {
        scanner = new Html5Qrcode("reader");
        
        scanner.start(
            { facingMode: "environment" },
            { fps: 20, qrbox: { width: 210, height: 250 } },
            (result) => {
                textarea.innerText = result;
                stopScanning();

                fetch("/scan_qr_camera", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ qr_data: result })
                })
                .then(response => response.json())
                .then(qr_data => console.log("✅ Відповідь від сервера:", qr_data))
            },
            (errorMessage) => {
                console.log(errorMessage);
            }
        ).catch(err => {
            console.error("Error starting scanner:", err);
        });
    } else {
        scanner.start(
            { facingMode: "environment" },
            { fps: 20, qrbox: { width: 210, height: 250 } },
            (result) => {
                textarea.innerText = result;
                stopScanning();

                fetch("/scan_qr_camera", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ qr_data: result })
                })
                .then(response => response.json())
                .then(qr_data => console.log("✅ Відповідь від сервера:", qr_data))
            },
            (errorMessage) => {
                console.log(errorMessage);
            }
        ).catch(err => {
            console.error("Error starting scanner:", err);
        });
    }
});

function stopScanning() {
  if (scanner) {
    scanner.stop().then(() => {
        document.getElementById("upload-form").removeAttribute("style");
        document.getElementById("scan-content").removeAttribute("style");
        reader.classList.add("hidden");
        cameraModal.classList.add("hidden");
    }).catch((err) => {
        console.error("Error stopping scanner:", err);
    });
  }
}

// === Копіювання тексту ===
copyBtn.addEventListener("click", () => {
    const text = textarea.textContent;
    navigator.clipboard.writeText(text).then(() => {
        copyBtn.innerText = "Copied!";
        setTimeout(() => copyBtn.innerText = "Copy", 1500);
    });
});

// === Закриття модального вікна ===
closeBtn.addEventListener("click", () => {
    form.querySelector("img").src = "static/img/upload.png";
    document.getElementById("camera-scan").removeAttribute("style");
    document.getElementById("content").classList.remove("hidden");    

    stopScanning();

    textarea.innerText = "";
    fileInp.value = "";
    infoText.innerText = "Upload QR Code";
});
