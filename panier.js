document.addEventListener("DOMContentLoaded", () => {
  const addButtons = document.querySelectorAll(".add-to-cart");

  addButtons.forEach(button => {
    button.addEventListener("click", () => {
      const title = button.dataset.title;
      const price = button.dataset.price;

      fetch("/add_to_cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ title, price })
      }).then(res => {
        if (res.ok) {
          alert("Ajouté au panier!");
        } else {
          alert("Erreur lors de l'ajour au panier.");
        }
      });
    });
  });

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
      });
  }

  const clearBtn = document.getElementById("clear-cart");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      fetch("/clear_cart", { method: "POST" }).then(() => location.reload());
    });
  }
});
