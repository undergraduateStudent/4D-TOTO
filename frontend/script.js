/**
 * script.js
 *
 * Frontend logic for:
 * - Uploading a ticket image to the FastAPI backend
 * - Displaying results on the UI
 * - Handling language switching (English/Chinese/Malay/Tamil)
 *
 * Backend endpoint used:
 * POST http://127.0.0.1:8001/upload-image-ticket
 */

let currentLanguage = "en";
let lastResultData = null;

/**
 * Translation dictionary for UI text in multiple languages.
 * Elements are linked using the `data-i18n` attribute in index.html.
 */
const translations = {
  // ... (same as your file; unchanged)
};

/**
 * Updates the UI language based on the language dropdown selection.
 * Also re-renders the last result so output matches the selected language.
 */
function changeLanguage() {
  currentLanguage = document.getElementById("languageSelect").value;
  const t = translations[currentLanguage];

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (t[key]) el.innerText = t[key];
  });

  if (lastResultData) {
    displayResult(lastResultData);
  }
}

/**
 * Upload the selected ticket image file to the backend OCR endpoint.
 *
 * Steps:
 * 1) Validate user has selected a file
 * 2) Send file in multipart/form-data request
 * 3) Receive JSON response with extracted numbers and results
 * 4) Display ticket results in UI
 */
async function uploadTicket() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select a ticket image.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  document.getElementById("loading").style.display = "block";
  document.getElementById("resultCard").style.display = "none";

  try {
    const response = await fetch("http://127.0.0.1:8001/upload-image-ticket", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    document.getElementById("loading").style.display = "none";

    if (!response.ok) {
      alert(data.detail || "Failed to process ticket.");
      return;
    }

    lastResultData = data;
    displayResult(data);

  } catch (err) {
    document.getElementById("loading").style.display = "none";
    alert("Unable to connect to backend.");
  }
}

/**
 * Render the prize results on the webpage.
 *
 * @param {Object} data - Backend response JSON from /upload-image-ticket
 */
function displayResult(data) {
  const t = translations[currentLanguage];
  document.getElementById("resultCard").style.display = "block";

  document.getElementById("gameType").innerText = data.game_type;

  document.getElementById("ticketNumbers").innerText =
    Array.isArray(data.extracted_numbers)
      ? data.extracted_numbers.join(" ")
      : data.extracted_numbers;

  const box = document.getElementById("winningNumbers");
  box.innerHTML = "";

  if (data.game_type === "4D") {
    box.innerHTML += `🎯 ${t.prize_first}: ${data.winning_numbers.first}<br>`;
    box.innerHTML += `🥈 ${t.prize_second}: ${data.winning_numbers.second}<br>`;
    box.innerHTML += `🥉 ${t.prize_third}: ${data.winning_numbers.third}<br>`;
    box.innerHTML += `⭐ ${t.prize_starter}: ${data.winning_numbers.starter.join(", ")}<br>`;
    box.innerHTML += `🔹 ${t.prize_consolation}: ${data.winning_numbers.consolation.join(", ")}`;
  } else {
    box.innerText = data.winning_numbers.join(", ");
  }

  const msg = document.getElementById("finalMessage");
  if (data.is_winner) {
    msg.innerText =
      data.game_type === "4D" && data.winning_numbers.first === data.extracted_numbers[0]
        ? t.win_first
        : t.win_generic;
    msg.className = "final-message success";
  } else {
    msg.innerText = t.lose_generic;
    msg.className = "final-message fail";
  }
}

/**
 * Reset the page state so user can upload another ticket.
 */
function reset() {
  document.getElementById("fileInput").value = "";
  document.getElementById("resultCard").style.display = "none";
  lastResultData = null;
}

document.addEventListener("DOMContentLoaded", changeLanguage);
