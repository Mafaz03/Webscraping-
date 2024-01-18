// static/your_custom_script.js
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("loading-screen").style.display = "none";

  document.getElementById("send-btn").addEventListener("click", function () {
    // Show loading screen
    document.getElementById("loading-screen").style.display = "block";

    // Simulate backend processing
    setTimeout(function () {
      // Hide loading screen
      document.getElementById("loading-screen").style.display = "none";

      // Display the result content
      document.getElementById("result-content").innerHTML =
        "<p>Result data goes here...</p>";
    }, 3000); // Simulating a 3-second backend processing time
  });
});
