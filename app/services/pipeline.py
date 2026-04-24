from datetime import datetime, timezone
import uuid
import structlog
from app import extensions
from app.models.profile import BusinessProfile
from app.models.pipeline_run import PipelineRun
from app.models.query import DiscoveredQuery
from app.models.recommendation import ContentRecommendation
from app.agents.discovery import QueryDiscoveryAgent
from app.agents.scoring import VisibilityScoringAgent
from app.agents.recommendation import ContentRecommendationAgent

logger = structlog.get_logger(__name__)

def initialize_pipeline_run(profile_uuid: uuid.UUID) -> uuid.UUID:
    """Creates a pending run in the DB to immediately return to the user"""
    run = PipelineRun(
        profile_uuid=profile_uuid,
        status="pending",
        started_at=datetime.now(timezone.utc)
    )
    extensions.db_session.add(run)
    extensions.db_session.commit()
    return run.uuid

def run_visibility_pipeline(run_uuid: uuid.UUID) -> uuid.UUID:
    """Executes the multi-agent AI pipeline for a given run"""
    run = extensions.db_session.get(PipelineRun, run_uuid)
    if not run:
        raise ValueError(f"Run with UUID {run_uuid} not found.")

    profile = extensions.db_session.get(BusinessProfile, run.profile_uuid)

    profile_uuid = profile.uuid
    
    # update status to running
    run.status = "running"
    extensions.db_session.commit()

    total_tokens = 0

    try:
        profile_data = {
            "name": profile.name,
            "domain": profile.domain,
            "industry": profile.industry,
            "description": profile.description,
            "competitors": profile.competitors
        }

        # query Discovery
        discovery_agent = QueryDiscoveryAgent()
        queries = discovery_agent.run(profile_data)
        total_tokens += discovery_agent.tokens_used
        run.queries_discovered = len(queries)

        extensions.db_session.commit()

        # visibility Scoring
        scoring_agent = VisibilityScoringAgent()
        scored_queries_data = []

        for q_text in queries:
            score_data = scoring_agent.run(query_text=q_text, domain=profile.domain)
            total_tokens += scoring_agent.tokens_used

            db_query = DiscoveredQuery(
                profile_uuid=profile_uuid,
                run_uuid=run.uuid,
                query_text=score_data["query_text"],
                estimated_search_volume=score_data["estimated_search_volume"],
                competitive_difficulty=score_data["competitive_difficulty"],
                opportunity_score=score_data["opportunity_score"],
                domain_visible=score_data["domain_visible"],
                visibility_position=score_data["visibility_position"],
                discovered_at=datetime.now(timezone.utc)
            )
            extensions.db_session.add(db_query)
            extensions.db_session.flush()

            scored_queries_data.append({"db_model": db_query, "data": score_data})

        run.queries_scored = len(scored_queries_data)
        extensions.db_session.commit()

        # content recommendations (only for top 3 highest opportunity queries to save tokens)
        scored_queries_data.sort(key=lambda x: x["data"]["opportunity_score"], reverse=True)
        top_queries = scored_queries_data[:3]

        rec_agent = ContentRecommendationAgent()
        for item in top_queries:
            db_q = item["db_model"]
            q_data = item["data"]

            recs = rec_agent.run(profile_data=profile_data, query_data=q_data)
            total_tokens += rec_agent.tokens_used

            for rec_data in recs:
                db_rec = ContentRecommendation(
                    profile_uuid=profile_uuid,
                    query_uuid=db_q.uuid,
                    content_type=rec_data["content_type"],
                    title=rec_data["title"],
                    rationale=rec_data["rationale"],
                    target_keywords=rec_data["target_keywords"],
                    priority=rec_data["priority"]
                )
                extensions.db_session.add(db_rec)

        # finalize the run
        run.status = "completed"
        run.tokens_used = total_tokens
        run.completed_at = datetime.now(timezone.utc)
        extensions.db_session.commit()

        logger.info("Pipeline completed successfully", run_uuid=str(run.uuid), tokens=total_tokens)
        return run.uuid

    except Exception as e:
        logger.exception("Pipeline failed", error=str(e), profile_uuid=str(profile_uuid))
        extensions.db_session.rollback()

        # re-fetch the run from the DB to cleanly update the status after the rollback
        failed_run = extensions.db_session.get(PipelineRun, run.uuid)
        if failed_run:
            failed_run.status = "failed"
            failed_run.error_message = str(e)
            failed_run.completed_at = datetime.now(timezone.utc)
            extensions.db_session.commit()

        return run.uuid