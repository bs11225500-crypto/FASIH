document.addEventListener("DOMContentLoaded", function () {

    const steps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    const progressText = document.querySelector(".progress-text");
    const progressFill = document.querySelector(".progress-fill");

    function updateProgress() {
    const total = steps.length;
    progressText.textContent = `${currentStep + 1} / ${total}`;
    progressFill.style.width = `${((currentStep + 1) / total) * 100}%`;
    }


    function showStep(index) {
    steps.forEach(step => step.classList.remove("active"));
    steps[index].classList.add("active");
    updateProgress();
    }


    document.querySelectorAll(".next-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            if (currentStep < steps.length - 1) {
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    document.querySelectorAll(".prev-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    showStep(currentStep);
});


const images = [
  "/static/img/img1.jpeg",
  "/static/img/img2.jpeg",
  "/static/img/img3.jpeg",
  "/static/img/img4.jpeg"
];

let currentImageIndex = 0;
let recordings = []; 

function updateImage() {
  document.getElementById("currentImage").src =
    images[currentImageIndex];
}
document.getElementById("nextImageBtn").addEventListener("click", () => {
  uploadCurrentAudio(); 

  if (currentImageIndex < images.length - 1) {
    currentImageIndex++;
    updateImage();

    audioPreview.src = "";
    audioPreview.style.display = "none";
    recordStatus.textContent = "";

    redoBtn.disabled = true;   
    recordBtn.disabled = false;
    stopBtn.disabled = true;

  } else {
    alert("تم الانتهاء من وصف الصور");
  }
});


let mediaRecorder;
let audioChunks = [];


let imageRecordings = [null, null, null, null];

const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const statusText = document.getElementById("recordStatus");
const audioPreview = document.getElementById("audioPreview");


navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      audioChunks = [];

      
      imageRecordings[currentImageIndex] = audioBlob;

      const audioURL = URL.createObjectURL(audioBlob);
      audioPreview.src = audioURL;
      audioPreview.style.display = "block";

      statusText.textContent = ` تم تسجيل الصوت للصورة ${currentImageIndex + 1}`;
      console.log("All recordings:", imageRecordings);
    };
  })
  .catch(error => {
    alert(" لم يتم السماح باستخدام المايك");
    console.error(error);
  });

recordBtn.addEventListener("click", () => {
  mediaRecorder.start();
  statusText.textContent = " جاري التسجيل...";
  recordBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
  redoBtn.disabled = false;
});

redoBtn.addEventListener("click", () => {
 
  imageRecordings[currentImageIndex] = null;

  
  audioPreview.src = "";
  audioPreview.style.display = "none";
  recordStatus.textContent = "🔄 يمكنك إعادة التسجيل الآن";

  redoBtn.disabled = true;
});


function uploadCurrentAudio() {
  const audioBlob = imageRecordings[currentImageIndex];

  if (!audioBlob) {
    alert(" ما فيه تسجيل لهذه الصورة");
    return;
  }

  const formData = new FormData();
  formData.append("audio", audioBlob);
  formData.append("image_index", currentImageIndex);

  fetch("/assessment/upload-audio/", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    console.log("Uploaded:", data);
  })
  .catch(err => {
    console.error(err);
    alert(" لم يتم حفظ التسجيل، حاولي مرة أخرى");
  });
}
