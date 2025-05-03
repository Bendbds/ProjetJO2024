// Fonction pour ajouter un article au panier
function addToCart(title, price) {
    // Récupère le panier actuel depuis le localStorage (ou crée un panier vide si aucun panier existant)
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
  
    // Ajoute le nouvel article dans le panier
    cart.push({ title, price });
  
    // Sauvegarde le panier mis à jour dans localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
  
    // Met à jour l'affichage du panier
    updateCartUI();
  }
  
  // Fonction pour mettre à jour l'interface du panier
  function updateCartUI() {
    // Récupère le panier depuis localStorage
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
  
    // Sélectionne l'élément HTML où afficher les articles du panier
    const cartContainer = document.getElementById('cart-items');
    const totalElement = document.getElementById('total');
    cartContainer.innerHTML = '';  // Réinitialise le contenu actuel du panier
  
    let total = 0;
  
    // Si le panier est vide, affiche un message
    if (cart.length === 0) {
      cartContainer.innerHTML = '<p>Votre panier est vide.</p>';
      totalElement.textContent = 'Total Panier : 0 €';
    } else {
      // Parcourt chaque élément du panier et l'affiche
      cart.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.classList.add('cart-item');
        cartItem.textContent = `${item.title} - ${item.price} €`;
        cartContainer.appendChild(cartItem);
  
        // Met à jour le total
        total += parseFloat(item.price);
      });
  
      // Affiche le total du panier
      totalElement.textContent = `Total Panier : ${total.toFixed(2)} €`;
    }
  }
  
  // Fonction pour vider le panier
  function clearCart() {
    localStorage.removeItem('cart');
    updateCartUI();
  }
  
  // Fonction pour initialiser le panier au chargement de la page
  document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();
  
    // Gère l'action du bouton "Vider le panier"
    const clearButton = document.getElementById('clear-cart');
    if (clearButton) {
      clearButton.addEventListener('click', clearCart);
    }
  });
  
  // Ajout de l'événement d'ajout au panier dans index.html
  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function(event) {
      const title = event.target.getAttribute('data-title');  // Récupère le titre du produit
      const price = event.target.getAttribute('data-price');  // Récupère le prix du produit
      addToCart(title, price);  // Ajoute au panier
    });
  });
  