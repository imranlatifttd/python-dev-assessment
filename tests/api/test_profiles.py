def test_create_profile_success(client):
    payload = {
        "name": "Surfer SEO",
        "domain": "surferseo.com",
        "industry": "SEO Software",
        "description": "AI-powered SEO tool",
        "competitors": ["clearscope.io", "marketmuse.com"]
    }

    response = client.post("/api/v1/profiles", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert "profile_uuid" in data
    assert data["name"] == "Surfer SEO"
    assert data["status"] == "created"


def test_create_profile_validation_error(client):
    # Missing required field 'domain'
    payload = {
        "name": "Surfer SEO",
        "industry": "SEO Software",
        "description": "AI-powered SEO tool"
    }

    response = client.post("/api/v1/profiles", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert data["error"] == "Validation Error"
    assert any(detail["loc"] == ["domain"] for detail in data["details"])


def test_get_profile_success(client):
    # create a profile
    payload = {
        "name": "Frase",
        "domain": "frase.io",
        "industry": "SEO Tools",
        "description": "Content brief tool"
    }
    create_resp = client.post("/api/v1/profiles", json=payload)
    profile_uuid = create_resp.get_json()["profile_uuid"]

    # retrieve it
    response = client.get(f"/api/v1/profiles/{profile_uuid}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["profile_uuid"] == profile_uuid
    assert data["total_queries_discovered"] == 0
    assert data["avg_opportunity_score"] == 0.0


def test_get_profile_not_found(client):
    import uuid
    random_uuid = str(uuid.uuid4())

    response = client.get(f"/api/v1/profiles/{random_uuid}")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Not Found"