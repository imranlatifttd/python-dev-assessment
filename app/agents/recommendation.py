from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.agents.prompts.recommendation import SYSTEM_PROMPT, USER_PROMPT


class RecommendationItemSchema(BaseModel):
    content_type: str = Field(..., max_length=100)
    title: str = Field(...)
    rationale: str = Field(...)
    target_keywords: list[str] = Field(..., min_length=1, max_length=10)
    priority: str = Field(pattern="^(High|Medium|Low)$")


class ContentRecommendationSchema(BaseModel):
    recommendations: list[RecommendationItemSchema]


class ContentRecommendationAgent(BaseAgent):
    """Generates actionable content recommendations for a target query"""

    def run(self, profile_data: dict, query_data: dict) -> list[dict]:
        """
        Executes the content recommendation logic

        :param profile_data: Dictionary containing business profile info
        :param query_data: Dictionary containing query_text, intent_category, and visibility
        :return: A list of recommendation dictionaries
        """
        # Determine visibility gap status for the prompt context
        visible = query_data.get("domain_visible", False)
        pos = query_data.get("visibility_position")
        if visible and pos:
            gap_status = f"Visible at position {pos}, but needs reinforcement."
        else:
            gap_status = "Not currently visible in AI answers."

        user_prompt = USER_PROMPT.format(
            name=profile_data.get("name", "Unknown"),
            industry=profile_data.get("industry", "Unknown"),
            competitors=", ".join(profile_data.get("competitors", [])),
            query=query_data.get("query_text", "Unknown"),
            intent=query_data.get("intent_category", "Unknown"),
            gap_status=gap_status
        )

        result = self._call_llm_and_parse(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=ContentRecommendationSchema
        )

        # Convert the pydantic models back to standard dicts for the database layer
        return [rec.model_dump() for rec in result.recommendations]