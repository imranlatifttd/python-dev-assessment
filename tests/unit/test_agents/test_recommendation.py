import pytest
from app.agents.recommendation import ContentRecommendationAgent


def test_content_recommendation_agent_success(mocker, app):
    profile_data = {
        "name": "Surfer SEO",
        "industry": "SEO Software",
        "competitors": ["clearscope.io"]
    }
    query_data = {
        "query_text": "Surfer SEO vs Clearscope",
        "intent_category": "comparison",
        "domain_visible": False,
        "visibility_position": None
    }

    # Mock LLM response
    mock_json = '''
    {
      "recommendations": [
        {
          "content_type": "Comparison Guide",
          "title": "Surfer SEO vs Clearscope: The Ultimate 2026 Breakdown",
          "rationale": "Directly addresses the evaluation intent by providing an unbiased feature comparison.",
          "target_keywords": ["content optimization", "seo tools comparison"],
          "priority": "High"
        }
      ]
    }
    '''

    mock_response = mocker.Mock()
    mock_response.usage.input_tokens = 60
    mock_response.usage.output_tokens = 80
    mock_response.content = [mocker.Mock(text=mock_json)]

    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = mock_response
    mocker.patch('app.agents.base.get_anthropic_client', return_value=mock_client)

    with app.app_context():
        agent = ContentRecommendationAgent()
        results = agent.run(profile_data, query_data)

        assert len(results) == 1
        rec = results[0]
        assert rec["content_type"] == "Comparison Guide"
        assert rec["priority"] == "High"
        assert len(rec["target_keywords"]) == 2
        assert agent.tokens_used == 140