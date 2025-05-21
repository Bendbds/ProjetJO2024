// panier_main.js

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  const msg = document.getElementById('toast-message');

  msg.textContent = message;
  toast.style.backgroundColor = type === 'error' ? '#f8d7da' : '#d4edda';
  toast.style.color = type === 'error' ? '#721c24' : '#155724';
  toast.style.borderColor = type === 'error' ? '#f5c6cb' : '#c3e6cb';
  toast.style.display = 'flex';

  setTimeout(() => {
    toast.style.display = 'none';
  }, 3000);
}

function hideToast() {
  document.getElementById('toast').style.display = 'none';
}

function showModal(message) {
  const modal = document.getElementById('errorModal');
  const errorMessage = document.getElementById('errorMessage');
  errorMessage.textContent = message;
  modal.style.display = 'block';
}

function closeModal() {
  document.getElementById('errorModal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  const isAuthenticated = document.body.getAttribute('data-authenticated') === 'true';

  // Bloquer le paiement si non connecté
  const checkoutForm = document.getElementById('checkout-form');
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', function (e) {
      if (!isAuthenticated) {
        e.preventDefault();
        showToast("Vous devez être connecté pour procéder au paiement.", 'error');
      }
    });
  }

  // Vider le panier
  const clearBtn = document.getElementById("clear-cart");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      fetch("/clear_cart", { method: "POST" })
        .then(response => {
          if (!response.ok) throw new Error('Erreur serveur');
          return response.text();
        })
        .then(() => {
          const cartItems = document.getElementById("cart-items");
          if (cartItems) cartItems.innerHTML = "<p>Votre panier est vide.</p>";
          const total = document.getElementById("total");
          if (total) total.textContent = "Total Panier : 0 €";
          showToast("Panier vidé avec succès.", 'success');
        })
        .catch(err => {
          console.error(err);
          showToast("Erreur lors de la suppression du panier.", 'error');
        });
    });
  }
});
