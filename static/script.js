console.log("connected");

const prompt = document.querySelectorAll(".main-prompt");
const displayScreen = document.querySelector(".prompt-screen");
const sendBtn = document.querySelector(".send");
const section = document.querySelector(".prompt");

const output = document.querySelector(".test");
const NormalScreen = document.querySelector(".test-2");

// sendBtn.addEventListener("click", function () {
//   let val = prompt.value;
//   console.log(val);
//   if (!val) {
//     return;
//   } else {
//     output.classList.toggle("overlay");

//     NormalScreen.classList.toggle("hidden");
//   }

//   console.log("clcked");
// });

const LightmodeButton = document.querySelector(".light");
const DarkmodeButton = document.querySelector(".dark");

const topNav = document.querySelector(".top-panel");
const pushSection = document.querySelector(".push");
const linkBox = document.querySelector(".about");

const menu = document.querySelector(".menu");
const logoProj = document.querySelector(".logo");
const ans = document.querySelectorAll(".ans-1");

const promptSection = document.querySelector(".prompt-section");
console.log(promptSection);

const modeChanger = () => {
  topNav.classList.toggle("dark-mode-bg");
  topNav.classList.toggle("light-mode-bg");

  section.classList.toggle("dark-mode-screen");
  section.classList.toggle("light-mode-screen");

  displayScreen.classList.toggle("dark-mode-screen");
  displayScreen.classList.toggle("light-mode-screen");

  // output.classList.toggle("dark-mode-bg-ans");
  // output.classList.toggle("light-mode-bg-ans");

  prompt.forEach((prom) => {
    prom.classList.toggle("dark-mode-input");
    prom.classList.toggle("light-mode-input");
  });

  promptSection.classList.toggle("dark-mode-bg");
  promptSection.classList.toggle("light-mode-bg");

  pushSection.classList.toggle("dark-mode-bg");
  pushSection.classList.toggle("light-mode-bg");

  LightmodeButton.classList.toggle("hide");
  DarkmodeButton.classList.toggle("hide");

  linkBox.classList.toggle("bg-border");

  LightmodeButton.classList.toggle("active");
  DarkmodeButton.classList.toggle("active");
};

// displayScreen
// section
//
console.log(ans);
//#f0f4f9;
DarkmodeButton.addEventListener("click", function () {
  modeChanger();
});

LightmodeButton.addEventListener("click", function () {
  modeChanger();
});

const messages = [
  { message: "Hello!", timestamp: "2023-12-01T12:30:00" },
  { message: "How are you?", timestamp: "2023-12-01T12:35:00" },
  { message: "I am good, thanks!", timestamp: "2023-12-01T12:40:00" },
  { message: "Great!", timestamp: "2023-12-01T12:45:00" },
];

function showHistory() {
  const datePicker = document.getElementById("datePicker");
  const selectedDate = datePicker.value;

  const filteredMessages = messages.filter((message) => {
    const messageDate = new Date(message.timestamp).toISOString().split("T")[0];
    return messageDate === selectedDate;
  });

  displayMessages(filteredMessages);
}

function displayMessages(messagesToShow) {
  const chatHistory = document.getElementById("chatHistory");
  chatHistory.innerHTML = ""; // Clear chat history

  messagesToShow.forEach((message) => {
    const messageElement = document.createElement("div");
    const formattedDate = new Date(message.timestamp).toLocaleTimeString();
    messageElement.classList.add("message");
    messageElement.innerHTML = `<strong>${formattedDate}:</strong> ${message.message}`;
    chatHistory.appendChild(messageElement);
  });
}

function sendMessage() {
  const userInput = document.getElementById("userInput");
  const message = userInput.value.trim();
  const timestamp = new Date().toISOString();

  if (message !== "") {
    messages.push({ message, timestamp });
    userInput.value = "";
    showHistory(); // Refresh chat history after sending a new message
  }
}

// Display messages for the default date (today)
showHistory();

menu.addEventListener("click", function () {
  document.querySelector(".push").classList.toggle("sidebarshow");
});

// handling the backend....

// function showLoadingScreen() {
//   document.querySelector(".loading-screen").style.display = "block";
//   promptSection.style.display = "none";
// }

// function hideLoadingScreen() {
//   document.querySelector(".loading-screen").style.display = "none";
//   promptSection.style.display = "block";
// }

// function redirectToResultPage() {
//   // Redirect to result.html
//   const checkurl = document.getElementById("urls");

//   if (checkurl.value == "") {
//     return;
//   } else {
//     window.location.href = "/result";
//     sendData();
//   }
// }
// script.js

function showLoading() {
  document.querySelector(".loading-screen").style.display = "flex";
  document.querySelector(".prompt-section").style.display = "none";
}

function hideLoading() {
  document.querySelector(".loading-screen").style.display = "none";
  document.querySelector(".prompt-section").style.display = "flex";
}

function sendData() {
  const urlsInput = document.getElementById("urls");
  const promptInput = document.getElementById("prompt");
  console.log("urlsInput.value:", urlsInput.value); // Debug statement

  const keywordInput = document.getElementById("keyword");
  if (urlsInput.value == "") {
    return;
  }

  showLoading();

  const urls = urlsInput.value.split(",").map((link) => link.trim());

  const keyword = keywordInput.value;
  const prompt = promptInput.value;

  // Send data to the backend
  console.log(prompt);
  console.log(keyword);
  fetch("/scrape", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ urls, keyword, prompt }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.text();
    })
    .then((data) => {
      // Handle the response from the backend if needed
      console.log("Receved after the responseeee", data);
      hideLoading();

      window.location.href =
        "/result?response_complete=" + encodeURIComponent(data);
      // document.querySelector(
      //   ".ans-11"
      // ).innerHTML = `<p class="result">${data.result}</p>`;
    })
    .catch((error) => {
      // hideLoadingScreen();
      console.error("Error:", error);
    });
}
