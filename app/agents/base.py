import json
import re
from typing import Any
from pydantic import BaseModel, ValidationError
import structlog
from app.services.llm_client import get_anthropic_client

logger = structlog.get_logger(__name__)


class AgentError(Exception):
    """Custom exception for agent execution failures"""
    pass


class BaseAgent:
    """Abstract base class for all AI agents"""

    # Using Claude
    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self.client = get_anthropic_client()
        self.tokens_used = 0

    def _extract_json_from_text(self, text: str) -> dict | list:
        """Extracts JSON from text, handling markdown blocks"""
        # Try to find JSON within markdown blocks first
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: find the first { or [ and the last } or ]
            start_idx = text.find('{')
            list_start_idx = text.find('[')

            if start_idx == -1 and list_start_idx == -1:
                raise ValueError("No JSON object or array found in response.")

            if start_idx != -1 and (list_start_idx == -1 or start_idx < list_start_idx):
                end_idx = text.rfind('}') + 1
                json_str = text[start_idx:end_idx]
            else:
                end_idx = text.rfind(']') + 1
                json_str = text[list_start_idx:end_idx]

        return json.loads(json_str)

    def _call_llm_and_parse(self, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        """
        Calls the LLM, extracts JSON, validates against a Pydantic schema
        and handles parsing retries
        """
        max_parse_attempts = 2

        for attempt in range(max_parse_attempts):
            try:
                logger.info("Calling LLM", model=self.MODEL, attempt=attempt + 1)

                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=4096,
                    temperature=0.2,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )

                # Track tokens
                self.tokens_used += response.usage.input_tokens + response.usage.output_tokens

                raw_text = response.content[0].text
                parsed_json = self._extract_json_from_text(raw_text)

                # Validate the extracted JSON against our expected pydantic schema
                validated_data = schema.model_validate(parsed_json)
                return validated_data

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("Failed to parse JSON from LLM", error=str(e), attempt=attempt + 1)
                if attempt == max_parse_attempts - 1:
                    raise AgentError(f"Failed to extract valid JSON after {max_parse_attempts} attempts: {str(e)}")
                # If we fail, we could append an error message to the prompt and try again
                # but simple retries often work for transient claude generation

            except ValidationError as e:
                logger.warning("LLM output did not match schema", error=str(e), attempt=attempt + 1)
                if attempt == max_parse_attempts - 1:
                    raise AgentError(f"LLM output failed schema validation: {str(e)}")

            except Exception as e:
                logger.error("Unexpected LLM error", error=str(e))
                raise AgentError(f"LLM call failed: {str(e)}")

        raise AgentError("Agent execution failed completely.")

    def run(self, *args, **kwargs) -> Any:
        """To be implemented by child classes"""
        raise NotImplementedError