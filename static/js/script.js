let video = document.getElementById('webcam');
let emotionText = document.getElementById('emotion');
let audioPlayer = document.getElementById('player');

let currentEmotion = null;
let detectionInterval = null;

async function startDetection() {
  detectionInterval = setInterval(captureAndSendFrame, 2000);
}

function stopDetection() {
  clearInterval(detectionInterval);
}

async function captureAndSendFrame() {
  let canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  let base64Image = canvas.toDataURL('image/jpeg');

  let res = await fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: base64Image })
  });

  let data = await res.json();
  currentEmotion = data.emotion;
  emotionText.innerText = `Emotion Detected: ${data.emotion} 😄`;

  audioPlayer.src = data.song_url;
  audioPlayer.play();

  stopDetection(); // stop detecting once a song starts
}

// ⏭️ Switch to next song of current emotion
async function nextSong() {
  if (!currentEmotion) return;

  let res = await fetch(`/next?same_emotion=${currentEmotion}`);
  let data = await res.json();
  audioPlayer.src = data.song_url;
  audioPlayer.play();
}

// 🔁 Detect again
function detectAgain() {
  currentEmotion = null;
  emotionText.innerText = "Detecting emotion...";
  startDetection();
}

// 📸 Start webcam on load
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
    startDetection();
  })
  .catch(err => console.error("Webcam error:", err));
