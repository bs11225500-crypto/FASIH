let stream;
let mediaRecorder;
let recordedChunks = [];

const statusText = document.getElementById("status");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const retryBtn = document.getElementById("retryBtn");

async function startCamera() {
  stream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: true
  });

  document.getElementById("camera").srcObject = stream;
}

async function startRecording() {
  if (!stream) await startCamera();

  recordedChunks = [];
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) recordedChunks.push(e.data);
  };

  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: "video/webm" });
    console.log("Recorded blob:", blob);

    statusText.innerText = "✅ تم تسجيل المحاولة، يمكنك الإعادة أو المتابعة";

    retryBtn.style.display = "inline-block";
    startBtn.style.display = "none";
    stopBtn.style.display = "none";
  };

  mediaRecorder.start();

  statusText.innerText = "🔴 جاري التسجيل...";
  startBtn.style.display = "none";
  stopBtn.style.display = "inline-block";
  retryBtn.style.display = "none";
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();

    document.getElementById("retryBtn").style.display = "inline-block";
    document.getElementById("finishBtn").style.display = "inline-block";
    document.getElementById("startBtn").style.display = "none";
  }
}


function retryRecording() {
  recordedChunks = [];
  document.getElementById("retryBtn").style.display = "none";
  document.getElementById("finishBtn").style.display = "none";
  document.getElementById("startBtn").style.display = "inline-block";
}

function finishTask() {
  if (!recordedChunks.length) {
    alert("لم يتم تسجيل أي محاولة");
    return;
  }

  const blob = new Blob(recordedChunks, { type: "video/webm" });
  const formData = new FormData();
  formData.append("video", blob);

  fetch(FINISH_TASK_URL, {   
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": CSRF_TOKEN
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "success") {
      window.location.href = TASKS_URL;
    } else {
      alert("حدث خطأ أثناء الإرسال");
    }
  })
  .catch(err => {
    console.error(err);
    alert("خطأ في الاتصال");
  });
}


window.onload = startCamera;
