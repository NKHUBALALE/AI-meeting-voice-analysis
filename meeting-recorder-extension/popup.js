let mediaRecorder = null;
let recordedChunks = [];
let activeStream = null;

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

startBtn.addEventListener("click", async () => {

  try {

    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
      audio: true
    });

    activeStream = stream;

    // Check if audio is actually available
    const audioTracks = stream.getAudioTracks();
    if (audioTracks.length === 0) {
      alert("No system audio detected. For audio recording, please select a Chrome tab.");
    }

    mediaRecorder = new MediaRecorder(stream);

    recordedChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    };

    //  UPDATED PART (backend + download)
    mediaRecorder.onstop = async () => {

      if (recordedChunks.length === 0) {
        console.log("No data recorded.");
        return;
      }

      const blob = new Blob(recordedChunks, { type: "video/webm" });
      const url = URL.createObjectURL(blob);

      //  Keep download feature
      chrome.downloads.download({
        url: url,
        filename: "meeting_recording.webm"
      });

      //  Send to backend
      try {
        const formData = new FormData();
        formData.append("file", blob, "meeting.webm");

        const resultsDiv = document.getElementById("results");
        if (resultsDiv) {
          resultsDiv.innerHTML = "Analyzing...";
        }
        console.log("Sending to backend...");

        const response = await fetch("https://bobbie-expostulatory-donald.ngrok-free.dev/analyze", {
          method: "POST",
          body: formData
        });

        const data = await response.json();

        console.log("Analysis Result:", data);

        // Save result for popup or future UI
        chrome.storage.local.set({ analysisResult: data });

        // Show results immediately
        const r = data;

        document.getElementById("results").innerHTML = `
          <p><b>Volume:</b> ${r.volume}</p>
          <p><b>Pace:</b> ${r.pace} (${r.wpm} WPM)</p>
          <p><b>Tone:</b> ${r.tone}</p>
          <p><b>Score:</b> 
            <span style="color:${r.confidence_score > 80 ? 'green' : 'orange'}">
              ${r.confidence_score}
            </span>
          </p>
          <p><b>Profile:</b> ${r.profile}</p>

          <h4>Feedback:</h4>
          <ul>${r.feedback.map(f => `<li>${f}</li>`).join("")}</ul>
        `;

      } catch (error) {
        console.error("Upload failed:", error);
      }

      recordedChunks = [];

      // Stop all tracks cleanly
      if (activeStream) {
        activeStream.getTracks().forEach(track => track.stop());
        activeStream = null;
      }
    };

    mediaRecorder.start();

    startBtn.disabled = true;
    stopBtn.disabled = false;

  } catch (error) {

    if (error.name === "NotAllowedError") {
      console.log("User cancelled screen selection.");
    } else {
      console.error("Screen capture failed:", error);
      alert("Failed to start screen recording.");
    }

  }

});

stopBtn.addEventListener("click", () => {

  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }

  startBtn.disabled = false;
  stopBtn.disabled = true;

});

// Load and display results when popup opens
document.addEventListener("DOMContentLoaded", () => {

  chrome.storage.local.get("analysisResult", (data) => {

    if (!data.analysisResult) return;

    const r = data.analysisResult;

    document.getElementById("results").innerHTML = `
      <p><b>Volume:</b> ${r.volume}</p>
      <p><b>Pace:</b> ${r.pace} (${r.wpm} WPM)</p>
      <p><b>Tone:</b> ${r.tone}</p>
      <p><b>Score:</b> ${r.confidence_score}</p>
      <p><b>Profile:</b> ${r.profile}</p>

      <h4>Feedback:</h4>
      <ul>${r.feedback.map(f => `<li>${f}</li>`).join("")}</ul>
    `;
  });

});