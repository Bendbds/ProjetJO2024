def test_mes_billets_page(logged_in_client):
    client, user, event = logged_in_client

    response = client.get('/mes_billets')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Vos billets" in html or "Billets" in html
