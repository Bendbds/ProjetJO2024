document.addEventListener("DOMContentLoaded", () => {
  // Mettre à jour l'affichage du panier
  updateCartUI();

  function updateCartUI() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const cartContainer = document.getElementById("cart-items");
    const totalElement = document.getElementById("total");
    cartContainer.innerHTML = "";  // Réinitialise l'affichage

    let total = 0;

    if (cart.length === 0) {
      cartContainer.innerHTML = "<p>Votre panier est vide.</p>";
      totalElement.textContent = "Total Panier : 0 €";
    } else {
      cart.forEach(item => {
        const cartItem = document.createElement("div");
        cartItem.classList.add("cart-item");
        cartItem.textContent = `${item.title} - ${item.price} € x ${item.quantity}`;
        cartContainer.appendChild(cartItem);

        total += item.price * item.quantity;
      });

      totalElement.textContent = `Total Panier : ${total.toFixed(2)} €`;
    }
  }

  // Gère l'événement de vider le panier
  const clearButton = document.getElementById("clear-cart");
  if (clearButton) {
    clearButton.addEventListener("click", () => {
      localStorage.removeItem("cart");
      updateCartUI();  // Rafraîchit l'interface après avoir vidé le panier
    });
  }
});



  /*
fetch('/api/cart/add', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify(offer)
});
*/
