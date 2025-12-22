document.addEventListener("DOMContentLoaded", function () {
  const openBtn = document.getElementById("openRejectModal");
  const closeBtn = document.getElementById("closeRejectModal");
  const modal = document.getElementById("rejectModal");
  const overlay = document.getElementById("rejectOverlay");

  if (openBtn) {
    openBtn.addEventListener("click", () => {
      modal.style.display = "block";
      overlay.style.display = "block";
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
      overlay.style.display = "none";
    });
  }

  if (overlay) {
    overlay.addEventListener("click", () => {
      modal.style.display = "none";
      overlay.style.display = "none";
    });
  }
});
