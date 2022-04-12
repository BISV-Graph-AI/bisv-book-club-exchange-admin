import json

from fastapi import status


def test_create_seller(client, normal_user_token_headers):
    data = {
        "name": "Super Seller",
        "email": "test@doogle.com",
        "paypal": "",
        "zelle": "",
        "date_posted": "2022-04-01",
    }
    response = client.post(
        "/sellers/create-seller/", data=json.dumps(data), headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Super Seller"
    assert response.json()["email"] == "test@doogle.com"


def test_read_seller(client, normal_user_token_headers):
    data = {
        "name": "Super Seller",
        "email": "www.doogle.com",
        "paypal": "",
        "zelle": "",
        "date_posted": "2022-04-01",
    }
    response = client.post(
        "/sellers/create-seller/", json.dumps(data), headers=normal_user_token_headers
    )

    response = client.get("/sellers/get/1/")
    assert response.status_code == 200
    assert response.json()["title"] == "SDE super"


def test_read_sellers(client, normal_user_token_headers):
    data = {
        "name": "Super Seller",
        "email": "www.doogle.com",
        "paypal": "",
        "zelle": "",
        "date_posted": "2022-04-01",
    }
    client.post(
        "/sellers/create-seller/", json.dumps(data), headers=normal_user_token_headers
    )
    client.post(
        "/sellers/create-seller/", json.dumps(data), headers=normal_user_token_headers
    )

    response = client.get("/sellers/all/")
    assert response.status_code == 200
    assert response.json()[0]
    assert response.json()[1]


def test_update_a_seller(client, normal_user_token_headers):
    data = {
        "name": "Super Seller",
        "email": "www.doogle.com",
        "paypal": "",
        "zelle": "",
        "date_posted": "2022-04-01",
    }
    client.post(
        "/sellers/create-seller/", json.dumps(data), headers=normal_user_token_headers
    )
    data["title"] = "test new title"
    response = client.put("/sellers/update/1", json.dumps(data))
    assert response.json()["msg"] == "Successfully updated data."


def test_delete_a_seller(client, normal_user_token_headers):
    data = {
        "name": "Super Seller",
        "email": "www.doogle.com",
        "paypal": "",
        "zelle": "",
        "date_posted": "2022-04-01",
    }
    client.post(
        "/sellers/create-seller/", json.dumps(data), headers=normal_user_token_headers
    )
    client.delete("/sellers/delete/1", headers=normal_user_token_headers)
    response = client.get("/sellers/get/1/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
