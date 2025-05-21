document.addEventListener("DOMContentLoaded", () => {
  const addButtons = document.querySelectorAll(".add-to-cart");

  // Fonction d’alerte type toast
  function showAlert(message, type = 'error') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    toastMessage.innerText = message;

    // Modification des couleurs en fonction du type de message
    toast.style.backgroundColor = type === 'error' ? '#f8d7da' : '#d4edda';
    toast.style.color = type === 'error' ? '#721c24' : '#155724';
    toast.style.borderColor = type === 'error' ? '#f5c6cb' : '#c3e6cb';
    toast.style.display = 'flex';

    setTimeout(() => {
      toast.style.display = 'none';
    }, 3000); // Disparition après 3 secondes
  }

  // Ajout au panier
  addButtons.forEach(button => {
    button.addEventListener("click", () => {
      const title = button.dataset.title;
      const price = button.dataset.price;
      const eventId = button.dataset.eventId;

      // Vérifie si toutes les données sont présentes avant d'envoyer la requête
      if (!title || !price || !eventId) {
        showAlert("Les données du produit sont manquantes.", 'error');
        return;
      }

      // Envoi de la requête d'ajout au panier
      fetch("/add_to_cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ title, price, event_id: eventId })
      })
      .then(res => res.json())  // Récupère la réponse JSON
      .then(data => {
        if (data.message) {
          if (data.message === "Vous devez être connecté pour ajouter un article.") {
            showAlert(data.message, 'error');
          } else if (data.message.includes("Erreur")) {
            showAlert(data.message, 'error');
          } else {
            showAlert(data.message, 'success');
          }
        } else {
          showAlert("Une erreur s'est produite lors de l'ajout au panier.", 'error');
        }
      })
      .catch(error => {
        console.error(error);
        showAlert("Vous devez être connecté pour ajouter un article.", 'error');
      });
    });
  });

  // Chargement des articles du panier
  if (document.getElementById("cart-items")) {
    fetch("/cart")
      .then(res => res.json())
      .then(data => {
        const cartContainer = document.getElementById("cart-items");
        const totalElement = document.getElementById("total");
        cartContainer.innerHTML = "";

        let total = 0;

        if (!data || data.length === 0) {
          cartContainer.innerHTML = "<p>Votre panier est vide.</p>";
          if (totalElement) totalElement.textContent = "Total Panier : 0 €";
        } else {
          data.forEach(item => {
            const div = document.createElement("div");
            div.classList.add("cart-item");
            div.textContent = `${item.offer_name} - €${item.price.toFixed(2)}`;
            cartContainer.appendChild(div);
            total += item.price;
          });

          if (totalElement) totalElement.textContent = `Total : €${total.toFixed(2)}`;
        }
      })
      .catch(error => {
        console.error(error);
        showAlert("Erreur lors du chargement du panier.", 'error');
      });
  }

  // Vider le panier
  const clearBtn = document.getElementById("clear-cart");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      fetch("/clear_cart", { method: "POST" })
        .then(() => {
          document.getElementById("cart-items").innerHTML = "<p>Votre panier est vide.</p>";
          document.getElementById("total").textContent = "Total Panier : 0 €";
          showAlert("Panier vidé avec succès.", 'success');
        })
        .catch(err => {
          console.error(err);
          showAlert("Erreur lors de la suppression du panier.", 'error');
        });
    });
  }

  // Vérification avant paiement
  const checkoutForm = document.querySelector("form[action='/create_checkout_session']");
  if (checkoutForm) {
    const isAuthenticated = document.body.getAttribute('data-authenticated') === 'true';  // Récupère la valeur du body
    checkoutForm.addEventListener("submit", (event) => {
      if (!isAuthenticated) {
        event.preventDefault();
        showAlert("Vous devez être connecté pour procéder au paiement.", 'error');
      }
    });
  }
});

