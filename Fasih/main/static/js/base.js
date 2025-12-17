document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".main-navbar");

    window.addEventListener("scroll", function () {
        if (window.scrollY > 80) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });
});
