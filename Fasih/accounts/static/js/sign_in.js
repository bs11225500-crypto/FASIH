document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-auth-link]").forEach((el) => {
    el.addEventListener("click", () => {
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const password = document.getElementById("password");
  const password2 = document.getElementById("password2");

  if (!password || !password2) return;

  const rules = {
    length: document.getElementById("rule-length"),
    upper: document.getElementById("rule-upper"),
    lower: document.getElementById("rule-lower"),
    number: document.getElementById("rule-number"),
  };

  const matchText = document.getElementById("match-password");

  password.addEventListener("input", () => {
    const value = password.value;

    toggleRule(rules.length, value.length >= 8);
    toggleRule(rules.upper, /[A-Z]/.test(value));
    toggleRule(rules.lower, /[a-z]/.test(value));
    toggleRule(rules.number, /[0-9]/.test(value));

    checkMatch();
  });

  password2.addEventListener("input", checkMatch);

  function toggleRule(element, condition) {
    if (condition) {
      element.classList.add("valid");
      element.textContent = "✔ " + element.textContent.replace("❌", "").replace("✔", "").trim();
    } else {
      element.classList.remove("valid");
      element.textContent = "❌ " + element.textContent.replace("✔", "").replace("❌", "").trim();
    }
  }

  function checkMatch() {
    if (!password2.value) {
      matchText.textContent = "";
      matchText.className = "password-match";
      return;
    }

    if (password.value === password2.value) {
      matchText.textContent = "✔ كلمتا المرور متطابقتان";
      matchText.className = "password-match success";
    } else {
      matchText.textContent = "❌ كلمتا المرور غير متطابقتين";
      matchText.className = "password-match error";
    }
  }
});

const passwordInput = document.getElementById("password");
const rules = {
  length: value => value.length >= 8,
  uppercase: value => /[A-Z]/.test(value),
  lowercase: value => /[a-z]/.test(value),
  number: value => /[0-9]/.test(value),
};

passwordInput.addEventListener("input", () => {
  const value = passwordInput.value;

  Object.keys(rules).forEach(rule => {
    const ruleElement = document.querySelector(
      `.password-rules p[data-rule="${rule}"]`
    );

    if (rules[rule](value)) {
      ruleElement.classList.add("valid");
    } else {
      ruleElement.classList.remove("valid");
    }
  });
});
const form = passwordInput.closest("form");

form.addEventListener("submit", e => {
  const value = passwordInput.value;
  const isValid = Object.values(rules).every(rule => rule(value));

  if (!isValid) {
    e.preventDefault();
    alert("كلمة المرور لا تحقق جميع الشروط");
  }
});
