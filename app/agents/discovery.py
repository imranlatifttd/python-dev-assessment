from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.agents.prompts.discovery import SYSTEM_PROMPT, USER_PROMPT


class DiscoveredQueriesSchema(BaseModel):
    queries: list[str] = Field(..., min_length=1, max_length=30)


class QueryDiscoveryAgent(BaseAgent):
    """Discovers relevant AI search queries for a given business profile"""

    def run(self, profile_data: dict) -> list[str]:
        """
        Executes the discovery pipeline

        :param profile_data: Dictionary containing name, domain, industry,
                             description and competitors.
        :return: A list of discovered query strings
        """
        user_prompt = USER_PROMPT.format(
            name=profile_data.get("name", "Unknown"),
            domain=profile_data.get("domain", "Unknown"),
            industry=profile_data.get("industry", "Unknown"),
            description=profile_data.get("description", "Unknown"),
            competitors=", ".join(profile_data.get("competitors", []))
        )

        # BaseAgent handles the LLM call, JSON parsing, retries and pydantic validation
        result = self._call_llm_and_parse(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=DiscoveredQueriesSchema
        )

        return result.queries