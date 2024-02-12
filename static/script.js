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

const menu = document.querySelector(".menu");

menu.addEventListener("click", function (e) {
  e.preventDefault();
  console.log("menu clicked");
  document.querySelector(".push").classList.toggle("sidebarshow");
});

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

  // var selectedOption = document.querySelector(
  //   'input[name="tripple"]:checked'
  // ).value;

  const keywordInput = document.getElementById("keyword");
  if (urlsInput.value == "") {
    return;
  }

  showLoading();

  const urls = urlsInput.value.split(",").map((link) => link.trim());

  const keyword = keywordInput.value;
  const prompt = promptInput.value;

  const from_date = document.getElementById("datePicker").value;
  const to_date = document.getElementById("userInput").value;

  const selectedOptions = [];

  document
    .querySelectorAll('.form-group input[type="checkbox"]')
    .forEach((checkbox) => {
      if (checkbox.checked) {
        selectedOptions.push(checkbox.name);
      }
    });

  // const formData = {
  //   html: document.getElementById("html").checked,
  //   css: document.getElementById("css").checked,
  //   javascript: document.getElementById("javascript").checked,
  // };

  const postData = {
    urls: urls,
    keyword: keyword,
    prompt: prompt,
    from_date: from_date,
    to_date: to_date,
    selectedOption: selectedOptions,
  };

  // Send data to the backend
  console.log(prompt);
  console.log(keyword);

  fetch("/scrape", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(postData),
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

function openBot() {
  var openBotUrl = "/chatbot";
  window.open(openBotUrl, "_blank");
}
