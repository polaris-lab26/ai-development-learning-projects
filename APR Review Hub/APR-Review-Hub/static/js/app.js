(function () {
  "use strict";

  // Mobile menu button (the menu stays visible if JavaScript is unavailable).
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });
    // Escape closes the open mobile menu and returns focus to its button.
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true" && nav.classList.contains("is-open")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        toggle.focus();
      }
    });
  }

  // Move focus to the success message so keyboard and screen-reader users reach it.
  var status = document.querySelector('[role="status"]');
  if (status) {
    status.setAttribute("tabindex", "-1");
    status.focus();
  }

  // Move focus to the error summary when a form is redisplayed with errors.
  var summary = document.getElementById("error-summary");
  if (summary) {
    summary.focus();
  }

  // Confirmation dialog for Submit, Resubmit, Approve and Return.
  var dialog = document.getElementById("confirm-dialog");
  if (!dialog || typeof dialog.showModal !== "function") {
    return;
  }
  var text = document.getElementById("confirm-text");
  var pending = null;

  document.addEventListener("submit", function (event) {
    var form = event.target;
    var submitter = event.submitter;
    if (!form.matches("[data-confirm-form]") || !submitter || !submitter.dataset.confirm) {
      return;
    }
    if (form.dataset.confirmed) {
      delete form.dataset.confirmed;
      return;
    }
    // Invalid forms go to the server so the error summary is shown instead.
    var needs = submitter.dataset.needs;
    if (!form.checkValidity() || (needs && !form.elements[needs].value.trim())) {
      return;
    }
    event.preventDefault();
    pending = { form: form, submitter: submitter };
    text.textContent = submitter.dataset.confirm;
    dialog.showModal();
  });

  document.getElementById("confirm-ok").addEventListener("click", function () {
    var chosen = pending;
    pending = null;
    dialog.close();
    if (chosen) {
      chosen.form.dataset.confirmed = "true";
      chosen.form.requestSubmit(chosen.submitter);
    }
  });

  document.getElementById("confirm-cancel").addEventListener("click", function () {
    var chosen = pending;
    pending = null;
    dialog.close();
    if (chosen) {
      chosen.submitter.focus();
    }
  });
})();
