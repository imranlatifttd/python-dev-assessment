import pytest
from app.agents.discovery import QueryDiscoveryAgent


def test_query_discovery_agent_success(mocker, app):
    # Setup mock profile
    profile_data = {
        "name": "Surfer SEO",
        "domain": "surferseo.com",
        "industry": "SEO Software",
        "description": "AI-powered SEO content optimization tool",
        "competitors": ["clearscope.io", "marketmuse.com"]
    }

    # Mock the anthropic client and its response
    mock_response = mocker.Mock()
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 100
    mock_response.content = [
        mocker.Mock(text='{"queries": ["What is the best SEO tool?", "Surfer SEO vs Clearscope"]}')]

    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = mock_response

    mocker.patch('app.agents.base.get_anthropic_client', return_value=mock_client)

    with app.app_context():
        agent = QueryDiscoveryAgent()
        queries = agent.run(profile_data)

        # Verify the output
        assert len(queries) == 2
        assert "What is the best SEO tool?" in queries
        assert agent.tokens_used == 150

        # Verify the prompt injection worked correctly
        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_content = call_kwargs['messages'][0]['content']
        assert "Surfer SEO" in user_content
        assert "clearscope.io, marketmuse.com" in user_content