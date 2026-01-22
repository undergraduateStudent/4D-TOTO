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

/* ======================
   Global State
====================== */
let currentLanguage = "en";
let lastResultData = null;

/* ======================
   Translations
====================== */
const translations = {
  en: {
    title: "Lottery Ticket Checker",
    subtitle: "Upload a photo of your TOTO or 4D ticket",
    step1: "Step 1: Upload Ticket",
    check_ticket: "Check Ticket",
    hint: "Take a clear photo in good lighting. Make sure all numbers are visible.",
    result: "Result",
    check_another: "Check Another Ticket",
    loading: "Checking your ticket, please wait...",

    game: "Game",
    your_numbers: "Your Numbers",
    winning_numbers: "Winning Numbers",

    prize_first: "1st Prize",
    prize_second: "2nd Prize",
    prize_third: "3rd Prize",
    prize_starter: "Starter",
    prize_consolation: "Consolation",

    win_generic: "Congratulations! You won.",
    lose_generic: "Your ticket did not win this time.",
    win_first: "Congratulations! You won the First Prize."
  },

  zh: {
    title: "彩票号码查询",
    subtitle: "上传您的 TOTO 或 4D 彩票照片",
    step1: "步骤 1：上传彩票",
    check_ticket: "检查彩票",
    hint: "请在光线充足的情况下拍摄清晰的照片。",
    result: "结果",
    check_another: "检查另一张彩票",
    loading: "正在检查您的彩票，请稍候...",

    game: "游戏",
    your_numbers: "您的号码",
    winning_numbers: "中奖号码",

    prize_first: "一等奖",
    prize_second: "二等奖",
    prize_third: "三等奖",
    prize_starter: "入围奖",
    prize_consolation: "安慰奖",

    win_generic: "恭喜！您中奖了。",
    lose_generic: "很遗憾，您的彩票未中奖。",
    win_first: "恭喜！您获得了一等奖。"
  },

  ms: {
    title: "Semakan Tiket Loteri",
    subtitle: "Muat naik gambar tiket TOTO atau 4D anda",
    step1: "Langkah 1: Muat Naik Tiket",
    check_ticket: "Semak Tiket",
    hint: "Ambil gambar yang jelas dalam pencahayaan yang baik.",
    result: "Keputusan",
    check_another: "Semak Tiket Lain",
    loading: "Sedang menyemak tiket anda, sila tunggu...",

    game: "Permainan",
    your_numbers: "Nombor Anda",
    winning_numbers: "Nombor Menang",

    prize_first: "Hadiah Pertama",
    prize_second: "Hadiah Kedua",
    prize_third: "Hadiah Ketiga",
    prize_starter: "Hadiah Permulaan",
    prize_consolation: "Hadiah Saguhati",

    win_generic: "Tahniah! Anda menang.",
    lose_generic: "Maaf, tiket anda tidak menang kali ini.",
    win_first: "Tahniah! Anda memenangi Hadiah Pertama."
  },

  ta: {
    title: "லாட்டரி டிக்கெட் சரிபார்ப்பு",
    subtitle: "உங்கள் TOTO அல்லது 4D டிக்கெட்டின் புகைப்படத்தை பதிவேற்றவும்",
    step1: "படி 1: டிக்கெட்டை பதிவேற்றவும்",
    check_ticket: "டிக்கெட்டை சரிபார்க்கவும்",
    hint: "நன்றாக வெளிச்சம் உள்ள இடத்தில் தெளிவான புகைப்படம் எடுக்கவும்.",
    result: "முடிவு",
    check_another: "மற்றொரு டிக்கெட்டை சரிபார்க்கவும்",
    loading: "டிக்கெட்டை சரிபார்க்கிறது, தயவுசெய்து காத்திருக்கவும்...",

    game: "விளையாட்டு",
    your_numbers: "உங்கள் எண்கள்",
    winning_numbers: "வெற்றி எண்கள்",

    prize_first: "முதல் பரிசு",
    prize_second: "இரண்டாம் பரிசு",
    prize_third: "மூன்றாம் பரிசு",
    prize_starter: "ஆரம்ப பரிசு",
    prize_consolation: "ஆறுதல் பரிசு",

    win_generic: "வாழ்த்துகள்! நீங்கள் வெற்றி பெற்றுள்ளீர்கள்.",
    lose_generic: "மன்னிக்கவும், இந்த முறை உங்கள் டிக்கெட் வெற்றி பெறவில்லை.",
    win_first: "வாழ்த்துகள்! நீங்கள் முதல் பரிசை வென்றுள்ளீர்கள்."
  }
};

/* ======================
   Language Switch
====================== */
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

/* ======================
   Upload Ticket
====================== */
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

/* ======================
   Display Result
====================== */
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

/* ======================
   Reset
====================== */
function reset() {
  document.getElementById("fileInput").value = "";
  document.getElementById("resultCard").style.display = "none";
  lastResultData = null;
}

/* ======================
   Init
====================== */
document.addEventListener("DOMContentLoaded", changeLanguage);