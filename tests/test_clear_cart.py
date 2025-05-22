import json

def test_clear_cart_authenticated(logged_in_client):
    client, user, event = logged_in_client
    
    # Ajout au panier pour simuler un état
    client.post('/add_to_cart',
                data=json.dumps({"title": event.name, "price": event.price, "event_id": event.id}),
                content_type='application/json')
    
    # Vidage du panier (POST)
    response = client.post('/clear_cart')
    assert response.status_code == 204

def test_clear_cart_unauthenticated(client):
    # Simuler session temporaire
    with client.session_transaction() as sess:
        sess['temp_user_id'] = 'test-temp-id'
    
    response = client.post('/clear_cart')
    assert response.status_code == 204
