document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', async () => {
      const eventId = button.dataset.eventId;

      try {
        const response = await fetch(`/ajouter_au_panier/${eventId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        let result = null;
        const contentType = response.headers.get('content-type') || '';

        if (contentType.includes('application/json')) {
          result = await response.json();
        }

        if (response.status === 401 || (result && result.message && result.message.includes("connecté"))) {
          showToast("Vous devez être connecté pour ajouter au panier.", 'error');
        } else if (response.ok) {
          showToast("Billet ajouté au panier !", 'success');
        } else {
          showToast("Une erreur est survenue.", 'error');
        }
      } catch (error) {
        showToast("Erreur de communication avec le serveur.", 'error');
      }
    });
  });
});
