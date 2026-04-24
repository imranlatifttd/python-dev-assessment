import threading
from flask import Blueprint, jsonify, current_app
from app.extensions import db_session
from app.models.profile import BusinessProfile
from app.models.pipeline_run import PipelineRun
from app.models.query import DiscoveredQuery
from app.models.recommendation import ContentRecommendation
from app.services.pipeline import run_visibility_pipeline, initialize_pipeline_run
from app.schemas.pipeline import PipelineRunResponse
from app.schemas.query import DiscoveredQueryResponse
from app.schemas.recommendation import ContentRecommendationResponse
import app.tasks
from app.limiter import limiter

pipeline_bp = Blueprint("pipeline", __name__)


@pipeline_bp.route("/profiles/<uuid:profile_uuid>/analyze", methods=["POST"])
@limiter.limit("2 per minute")
def trigger_analysis(profile_uuid):
    """Triggers the multi-agent AI visibility pipeline for a profile"""
    profile = db_session.get(BusinessProfile, profile_uuid)

    if not profile:
        return jsonify(
            {"error": "Not Found", "details": [{"msg": "Profile not found", "type": "resource_missing"}]}), 404

    try:
        # initialize the run in the DB to get a UUID instantly
        run_uuid = initialize_pipeline_run(profile.uuid)

        # check feature flag to determine sync vs async execution
        if current_app.config.get("ASYNC_PIPELINE"):
            app.tasks.execute_pipeline_task.delay(str(run_uuid))
        else:
            run_visibility_pipeline(run_uuid)

        # fetch and return the run state (will be 'pending' if async, 'completed' if sync)
        run = db_session.get(PipelineRun, run_uuid)
        response_data = PipelineRunResponse.model_validate(run)

        return jsonify(response_data.model_dump(mode="json")), 202

    except Exception as e:
        return jsonify({"error": "Pipeline Error", "details": [{"msg": str(e), "type": "execution_failed"}]}), 500


@pipeline_bp.route("/runs/<uuid:run_uuid>", methods=["GET"])
def get_run_status(run_uuid):
    """Retrieves the status of a specific pipeline run"""
    run = db_session.get(PipelineRun, run_uuid)

    if not run:
        return jsonify({"error": "Not Found", "details": [{"msg": "Run not found", "type": "resource_missing"}]}), 404

    response_data = PipelineRunResponse.model_validate(run)
    return jsonify(response_data.model_dump(mode="json")), 200


@pipeline_bp.route("/profiles/<uuid:profile_uuid>/queries", methods=["GET"])
def get_profile_queries(profile_uuid):
    """Retrieves all scored queries discovered for a profile sorted by opportunity"""
    profile = db_session.get(BusinessProfile, profile_uuid)
    if not profile:
        return jsonify(
            {"error": "Not Found", "details": [{"msg": "Profile not found", "type": "resource_missing"}]}), 404

    queries = db_session.query(DiscoveredQuery).filter_by(
        profile_uuid=profile_uuid
    ).order_by(DiscoveredQuery.opportunity_score.desc()).all()

    response_data = [DiscoveredQueryResponse.model_validate(q).model_dump(mode="json") for q in queries]
    return jsonify({"queries": response_data}), 200


@pipeline_bp.route("/profiles/<uuid:profile_uuid>/recommendations", methods=["GET"])
def get_profile_recommendations(profile_uuid):
    """Retrieves actionable content recommendations for a profile"""
    profile = db_session.get(BusinessProfile, profile_uuid)
    if not profile:
        return jsonify(
            {"error": "Not Found", "details": [{"msg": "Profile not found", "type": "resource_missing"}]}), 404

    recs = db_session.query(ContentRecommendation).filter_by(
        profile_uuid=profile_uuid
    ).all()

    response_data = [ContentRecommendationResponse.model_validate(r).model_dump(mode="json") for r in recs]
    return jsonify({"recommendations": response_data}), 200