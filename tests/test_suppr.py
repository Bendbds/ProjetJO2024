from models import User, Event
import json

def test_remove_from_cart(logged_in_client):
    client, user, event = logged_in_client

    # Ajouter un article au panier
    client.post('/add_to_cart',
        data=json.dumps({
            "title": event.name,
            "price": event.price,
            "event_id": event.id
        }),
        content_type='application/json'
    )

    # Suppression avec requête POST (simulateur fetch)
    response = client.post(f'/remove_from_cart/{event.id}', follow_redirects=False)
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert 'message' in data
    assert 'supprimé' in data['message'] or 'succès' in data['message']

    # Pour vérifier que l'article est bien supprimé côté serveur, refaire un get panier
    response_panier = client.get('/panier')
    html = response_panier.data.decode('utf-8')
    assert event.name not in html
