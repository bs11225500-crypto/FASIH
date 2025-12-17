document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("container");
  const signUpBtn = document.getElementById("goToSignUp");
  const signInBtn = document.getElementById("goToSignIn");

  if (signUpBtn) {
    signUpBtn.addEventListener("click", function () {
      container.classList.add("right-panel-active");
    });
  }

  if (signInBtn) {
    signInBtn.addEventListener("click", function () {
      container.classList.remove("right-panel-active");
    });
  }
});
