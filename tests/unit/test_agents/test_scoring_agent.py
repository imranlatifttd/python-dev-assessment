from app.agents.scoring import VisibilityScoringAgent
from app.services.seo_provider import MockSEOProvider


def test_visibility_scoring_agent_success(mocker, app):
    # Mock the LLM Response
    mock_response = mocker.Mock()
    mock_response.usage.input_tokens = 30
    mock_response.usage.output_tokens = 20
    mock_response.content = [
        mocker.Mock(
            text='{"domain_visible": false, "visibility_position": null, "intent_category": "comparison"}'
        )
    ]

    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = mock_response
    mocker.patch("app.agents.base.get_anthropic_client", return_value=mock_client)

    # Force the factory to return the MockProvider so we don't hit DataForSEO
    mocker.patch("app.agents.scoring.get_seo_provider", return_value=MockSEOProvider())

    with app.app_context():
        agent = VisibilityScoringAgent()
        result = agent.run("Clearscope vs Surfer SEO", "surferseo.com")

        assert result["query_text"] == "Clearscope vs Surfer SEO"
        assert result["domain_visible"] is False
        assert result["intent_category"] == "comparison"
        assert "estimated_search_volume" in result
        assert "competitive_difficulty" in result
        assert "opportunity_score" in result
        assert agent.tokens_used == 50
