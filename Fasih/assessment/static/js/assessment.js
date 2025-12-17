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
  if (currentImageIndex < images.length - 1) {
    currentImageIndex++;
    updateImage();
  } else {
    alert("تم الانتهاء من وصف الصور");
  }
});

