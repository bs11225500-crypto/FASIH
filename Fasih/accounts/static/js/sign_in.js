// اختياري: يضمن أن أي زر/رابط محدد يشتغل كرابط طبيعي
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-auth-link]").forEach((el) => {
    el.addEventListener("click", () => {
      // لا شيء مطلوب هنا — مجرد وجود الملف يمنع لبس الفريق
      // وتقدرين لاحقاً تضيفين tracking أو loading state
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
