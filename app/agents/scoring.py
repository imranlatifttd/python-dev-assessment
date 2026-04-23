from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.agents.prompts.scoring import SYSTEM_PROMPT, USER_PROMPT
from app.utils.scoring import calculate_opportunity_score
from app.services.seo_provider import get_seo_provider


class VisibilityAnalysisSchema(BaseModel):
    domain_visible: bool
    visibility_position: int | None = Field(default=None, ge=1, le=10)
    intent_category: str = Field(...)


class VisibilityScoringAgent(BaseAgent):
    """Scores a discovered query for visibility and opportunity"""

    def run(self, query_text: str, domain: str) -> dict:
        user_prompt = USER_PROMPT.format(domain=domain, query=query_text)

        # LLM evaluation
        llm_result = self._call_llm_and_parse(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=VisibilityAnalysisSchema
        )

        # get metrics via strategy pattern factory
        seo_provider = get_seo_provider()
        volume, difficulty = seo_provider.get_metrics(query_text, domain)

        # calculate final opportunity score
        opp_score = calculate_opportunity_score(
            volume=volume,
            difficulty=difficulty,
            domain_visible=llm_result.domain_visible,
            visibility_position=llm_result.visibility_position,
            intent_type=llm_result.intent_category
        )

        return {
            "query_text": query_text,
            "estimated_search_volume": volume,
            "competitive_difficulty": difficulty,
            "domain_visible": llm_result.domain_visible,
            "visibility_position": llm_result.visibility_position,
            "intent_category": llm_result.intent_category,
            "opportunity_score": opp_score
        }