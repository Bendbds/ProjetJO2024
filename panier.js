document.addEventListener("DOMContentLoaded", () => {
  const addButtons = document.querySelectorAll(".add-to-cart");

  // Fonction pour afficher les alertes personnalisées
  function showAlert(message, type = 'error') {
    const alertContainer = document.getElementById("custom-alert");
    if (alertContainer) {
      alertContainer.innerHTML = `<div class="alert ${type}">${message}</div>`;
      alertContainer.style.display = 'block';  // Affiche l'alerte
      setTimeout(() => {
        alertContainer.style.display = 'none';  // Cache l'alerte après 5 secondes
      }, 5000);
    }
  }

  addButtons.forEach(button => {
    button.addEventListener("click", () => {
      const title = button.dataset.title;
      const price = button.dataset.price;
      const eventId = button.dataset.eventId;

      // Envoi de la requête pour ajouter l'élément au panier
      fetch("/add_to_cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ title, price, event_id: eventId })
      })
      .then(res => {
        if (res.ok) {
          return res.json();  // On attend la réponse JSON si la requête est réussie
        } else {
          return res.json().then(data => {
            // Gérer le message d'erreur du serveur
            showAlert(data.message || "Erreur lors de l'ajout au panier.", 'error');
          });
        }
      })
      .then(data => {
        if (data && data.message) {
          // Affichage du message du serveur
          showAlert(data.message, 'success');
        }
      })
      .catch(error => {
        // Si une erreur se produit (par exemple non connecté)
        showAlert("Vous devez être connecté pour commander.", 'error');
      });
    });
  });

  // Gérer l'affichage du panier
  if (document.getElementById("cart-items")) {
    fetch("/cart")
      .then(res => res.json())
      .then(data => {
        const cartContainer = document.getElementById("cart-items");
        const totalElement = document.getElementById("total");
        cartContainer.innerHTML = "";

        let total = 0;

        if (data.length === 0) {
          cartContainer.innerHTML = "<p>Votre panier est vide.</p>";
          totalElement.textContent = "Total Panier : 0 €";
        } else {
          data.forEach(item => {
            const div = document.createElement("div");
            div.classList.add("cart-item");
            div.textContent = `${item.offer_name} - €${item.price}`;
            cartContainer.appendChild(div);
            total += item.price;
          });

          totalElement.textContent = `Total: €${total.toFixed(2)}`;
        }
      })
      .catch(error => {
        showAlert("Une erreur s'est produite lors du chargement du panier.", 'error');
      });
  }

  // Gérer l'effacement du panier
  const clearBtn = document.getElementById("clear-cart");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      fetch("/clear_cart", { method: "POST" })
        .then(() => location.reload());
    });
  }
});
