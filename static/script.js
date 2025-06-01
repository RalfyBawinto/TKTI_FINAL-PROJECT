const toggleBtn = document.getElementById("toggleModeBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const loadingSpinner = document.getElementById("loadingSpinner");
const resultSection = document.getElementById("resultSection");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const uploadBox = document.getElementById("uploadBox");
const summaryText = document.getElementById("summaryText");
const highlightList = document.getElementById("highlightList");
const copyBtn = document.getElementById("copyBtn");
const body = document.body;

// Toggle light/dark mode
toggleBtn.addEventListener("click", () => {
  body.classList.toggle("light-mode");
  body.classList.toggle("dark-mode");
  toggleBtn.textContent = body.classList.contains("light-mode")
    ? "Ganti ke Dark Mode"
    : "Ganti ke Light Mode";
});

// File input listener
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) {
    if (file.type !== "application/pdf") {
      alert("Hanya file PDF yang diperbolehkan.");
      fileInput.value = "";
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert("Ukuran file melebihi 5 MB.");
      fileInput.value = "";
      return;
    }
    fileInfo.textContent = `File terpilih: ${file.name} (${(
      file.size /
      1024 /
      1024
    ).toFixed(2)} MB)`;
    fileInfo.classList.remove("hidden");
    analyzeBtn.classList.remove("hidden");
    uploadBox.classList.add("hidden");
  }
});

// Drag & Drop event
uploadBox.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadBox.classList.add("drag-over");
});

uploadBox.addEventListener("dragleave", () => {
  uploadBox.classList.remove("drag-over");
});

uploadBox.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadBox.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event("change"));
  }
});

const resetBtn = document.getElementById("resetBtn");

resetBtn.addEventListener("click", () => {
  fileInput.value = "";
  fileInfo.classList.add("hidden");
  analyzeBtn.classList.add("hidden");
  resetBtn.classList.add("hidden");
  resultSection.classList.add("hidden");
  uploadBox.classList.remove("hidden");
});

// Analyze PDF
analyzeBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return alert("Harap unggah file PDF terlebih dahulu.");

  analyzeBtn.disabled = true;
  loadingSpinner.classList.remove("hidden");
  resultSection.classList.add("hidden");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(
      "https://tkti_final-project.railway.app/analyze",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    let data;
    try {
      data = await response.json();
    } catch (jsonError) {
      throw new Error("Gagal memparsing respon JSON dari server.");
    }

    loadingSpinner.classList.add("hidden");
    analyzeBtn.disabled = false;
    resultSection.classList.remove("hidden");

    // Sembunyikan tombol analisa setelah selesai
    analyzeBtn.classList.add("hidden");
    resetBtn.classList.remove("hidden");

    // Pastikan elemen ada sebelum mengubahnya
    if (summaryText) {
      summaryText.textContent = data.summary || "Ringkasan tidak tersedia.";
    }

    if (highlightList) {
      highlightList.innerHTML = "";
      if (data.highlights && data.highlights.length > 0) {
        data.highlights.forEach((kw) => {
          const li = document.createElement("li");
          li.textContent = kw;
          highlightList.appendChild(li);
        });
      } else {
        highlightList.innerHTML = "<li>Tidak ada highlight tersedia.</li>";
      }
    }
  } catch (err) {
    console.error("Gagal memproses:", err);
    loadingSpinner.classList.add("hidden");
    analyzeBtn.disabled = false;
    alert("Terjadi kesalahan saat menghubungi server. Silakan coba lagi.");
  }
});

// Copy summary
copyBtn.addEventListener("click", () => {
  navigator.clipboard
    .writeText(summaryText.textContent)
    .then(() => alert("Ringkasan berhasil disalin ke clipboard!"))
    .catch((err) => console.error("Gagal menyalin ringkasan:", err));
});

// Ekspor ke TXT
document.getElementById("exportTxtBtn").addEventListener("click", () => {
  const text = summaryText.textContent;
  const blob = new Blob([text], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "Ringkasan dari Smart Document Analyzer.txt";
  link.click();
});

// Ekspor ke PDF (menggunakan jsPDF)
document.getElementById("exportPdfBtn").addEventListener("click", () => {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const lines = doc.splitTextToSize(summaryText.textContent, 180);
  doc.text(lines, 10, 10);
  doc.save("Ringkasan dari Smart Document Analyzer.pdf");
});
