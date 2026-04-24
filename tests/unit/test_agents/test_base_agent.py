import pytest
from pydantic import BaseModel

from app.agents.base import BaseAgent


class DummySchema(BaseModel):
    name: str
    score: int


class DummyAgent(BaseAgent):
    def run(self):
        pass


def test_extract_json_clean(mocker):
    mocker.patch("app.agents.base.get_anthropic_client")
    agent = DummyAgent()
    clean_json = '{"name": "test", "score": 100}'
    result = agent._extract_json_from_text(clean_json)
    assert result == {"name": "test", "score": 100}


def test_extract_json_markdown(mocker):
    mocker.patch("app.agents.base.get_anthropic_client")
    agent = DummyAgent()
    markdown_json = """Here is your data:
    ```json
    {
        "name": "markdown",
        "score": 50
    }
    ```"""
    result = agent._extract_json_from_text(markdown_json)
    assert result == {"name": "markdown", "score": 50}


def test_extract_json_no_markdown_fluff(mocker):
    mocker.patch("app.agents.base.get_anthropic_client")
    agent = DummyAgent()
    fluff_json = 'Sure! Here it is: {"name": "fluff", "score": 10} Lemme know if you need anything else.'
    result = agent._extract_json_from_text(fluff_json)
    assert result == {"name": "fluff", "score": 10}


def test_extract_json_failure(mocker):
    mocker.patch("app.agents.base.get_anthropic_client")
    agent = DummyAgent()
    bad_text = "I am sorry, I cannot fulfill this request."
    with pytest.raises(ValueError, match="No JSON object or array found"):
        agent._extract_json_from_text(bad_text)


def test_call_llm_and_parse_success(mocker, app):
    # Mock the anthropic client response
    mock_response = mocker.Mock()
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 20
    mock_response.content = [mocker.Mock(text='{"name": "mocked", "score": 99}')]

    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = mock_response

    mocker.patch("app.agents.base.get_anthropic_client", return_value=mock_client)

    with app.app_context():
        agent = DummyAgent()
        result = agent._call_llm_and_parse("sys", "user", DummySchema)

        assert isinstance(result, DummySchema)
        assert result.name == "mocked"
        assert result.score == 99
        assert agent.tokens_used == 30
