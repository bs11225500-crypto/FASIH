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

function updateImage() {
  document.getElementById("currentImage").src = images[currentImageIndex];
}


function collectFormAnswers() {
  const answers = {};

 
  document.querySelectorAll("input, textarea").forEach(input => {
    if (!input.name) return;

    if (input.type === "radio") {
      if (input.checked) {
        answers[input.name] = input.value;
      }
    } 
    else if (input.type !== "checkbox") {
      answers[input.name] = input.value;
    }
  });


  const selectedLetters = [];
  document.querySelectorAll('input[name="difficult_letters"]:checked')
    .forEach(cb => {
      selectedLetters.push(cb.value);
    });

  answers["difficult_letters"] = selectedLetters;

  return answers;
}



let mediaRecorder;
let audioChunks = [];
let imageRecordings = [null, null, null, null];
let uploadedAudioPaths = [null, null, null, null];


const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const redoBtn = document.getElementById("redoBtn");
const nextImageBtn = document.getElementById("nextImageBtn");

const statusText = document.getElementById("recordStatus");
const audioPreview = document.getElementById("audioPreview");

navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = e => {
      audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      audioChunks = [];

      imageRecordings[currentImageIndex] = audioBlob;

      audioPreview.src = URL.createObjectURL(audioBlob);
      audioPreview.style.display = "block";

      statusText.textContent = `✅ تم تسجيل الصوت للصورة ${currentImageIndex + 1}`;
      redoBtn.disabled = false;
    };
  })
  .catch(() => {
    alert("❌ لم يتم السماح باستخدام المايك");
  });

recordBtn.addEventListener("click", () => {
  mediaRecorder.start();
  statusText.textContent = "🎙️ جاري التسجيل...";
  recordBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
});

redoBtn.addEventListener("click", () => {
  imageRecordings[currentImageIndex] = null;
  audioPreview.src = "";
  audioPreview.style.display = "none";
  statusText.textContent = "🔄 يمكنك إعادة التسجيل";
  redoBtn.disabled = true;
});



nextImageBtn.addEventListener("click", async () => {
  const success = await uploadCurrentAudio();
  if (!success) return;

  if (currentImageIndex < images.length - 1) {
    currentImageIndex++;
    updateImage();

    audioPreview.src = "";
    audioPreview.style.display = "none";
    statusText.textContent = "";

    redoBtn.disabled = true;
    recordBtn.disabled = false;
    stopBtn.disabled = true;

} else {
    recordBtn.disabled = false;  
    stopBtn.disabled = true;
    alert("🎉 تم الانتهاء من تسجيل الأصوات، يمكنك الآن إكمال الاستبيان");
}

});


async function uploadCurrentAudio() {
  const audioBlob = imageRecordings[currentImageIndex];

  if (!audioBlob) {
    alert("⚠️ سجلي الصوت قبل الانتقال");
    return false;
  }

  const formData = new FormData();
  formData.append("audio", audioBlob);
  formData.append("image_index", currentImageIndex);

  try {
    const res = await fetch("/assessment/upload-audio/", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Upload failed");

    const data = await res.json();
    console.log("Uploaded:", data);
    uploadedAudioPaths[currentImageIndex] = data.file;

    
    return true;

  } catch (err) {
    alert("❌ لم يتم حفظ التسجيل، حاولي مرة أخرى");
    return false;
  }
}


const submitBtn = document.getElementById("submitAssessmentBtn");

if (submitBtn) {
  submitBtn.addEventListener("click", async () => {

    if (uploadedAudioPaths.includes(null)) {
      alert("⚠️ الرجاء تسجيل جميع الأصوات قبل الإرسال");
      return;
    }

   const assessmentData = {
   sections_answers: collectFormAnswers(),
   images: images.map((img, index) => ({
     image: img,
     audio: uploadedAudioPaths[index]
  }))
};


    try {
      const res = await fetch("/assessment/submit/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          assessment_data: assessmentData
        })
      });

      if (!res.ok) throw new Error("Submit failed");

      const data = await res.json();
      alert("✅ تم إرسال التقييم بنجاح");



    } catch (err) {
      alert("❌ حدث خطأ أثناء الإرسال");
      console.error(err);
    }
  });
}
