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

    mediaRecorder.onstop = () => {

      if (recordedChunks.length === 0) {
        console.log("No data recorded.");
        return;
      }

      const blob = new Blob(recordedChunks, { type: "video/webm" });
      const url = URL.createObjectURL(blob);

      chrome.downloads.download({
        url: url,
        filename: "meeting_recording.webm"
      });

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