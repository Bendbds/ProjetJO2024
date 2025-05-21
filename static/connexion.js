// gestion de la validation des mots de passe
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const password = document.querySelector("input[name='password']");
  const confirmPassword = document.querySelector("input[name='confirm_password']");
  const errorBox = document.getElementById("password-error");
  const errorMessage = document.getElementById("password-error-message");

  form.addEventListener("submit", (event) => {
    if (password.value !== confirmPassword.value) {
      event.preventDefault(); // Empêche l'envoi du formulaire
      errorMessage.textContent = "Les mots de passe ne correspondent pas !";
      errorBox.style.display = "flex"; // Affiche la boîte d'erreur
    }
  });

  // Cache l'erreur si l'utilisateur modifie le champ
  confirmPassword.addEventListener("input", () => {
    errorBox.style.display = "none";
  });
});

// Gestion du modal d'erreur avec Flask flash messages
function showErrorModal(message) {
  document.getElementById("errorMessage").textContent = message;
  document.getElementById("errorModal").style.display = "block";
}

function closeModal() {
  document.getElementById("errorModal").style.display = "none";
}

window.onclick = function(event) {
  if (event.target == document.getElementById("errorModal")) {
    closeModal();
  }
};
