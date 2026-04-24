from app.services.seo_provider import MockSEOProvider, RealSEOProvider
from app.utils.scoring import calculate_opportunity_score


def test_mock_provider_determinism():
    provider = MockSEOProvider()
    query = "What is the best SEO tool?"
    v1, d1 = provider.get_metrics(query, "example.com")
    v2, d2 = provider.get_metrics(query, "example.com")

    assert v1 == v2
    assert d1 == d2
    assert 10 <= v1 <= 10000
    assert 0 <= d1 <= 100


def test_real_provider_success(mocker, app):
    # Mock the HTTP response from DataForSEO so we don't make a real network call
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "tasks": [
            {
                "status_code": 20000,
                "result": [{"search_volume": 1500, "competition_index": 45}],
            }
        ]
    }
    mocker.patch("requests.post", return_value=mock_response)

    provider = RealSEOProvider()

    with app.app_context():
        # Temporarily inject dummy credentials into the Flask config for the test
        app.config["DATAFORSEO_LOGIN"] = "dummy_login"
        app.config["DATAFORSEO_PASSWORD"] = "dummy_password"

        volume, difficulty = provider.get_metrics("test query", "example.com")

    assert volume == 1500
    assert difficulty == 45  # Verifies we correctly cast the float to an int


def test_calculate_opportunity_score_max():
    score = calculate_opportunity_score(10000, 0, False, None, "transactional")
    assert score == 1.0


def test_calculate_opportunity_score_min():
    score = calculate_opportunity_score(0, 100, True, 1, "navigational")
    assert score == 0.045
