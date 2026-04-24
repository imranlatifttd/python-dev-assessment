from flask import Blueprint, jsonify
from sqlalchemy.sql import func

from app.extensions import db_session
from app.models.profile import BusinessProfile
from app.models.query import DiscoveredQuery
from app.schemas.profile import (
    ProfileCreateRequest,
    ProfileDetailResponse,
    ProfileResponse,
)
from app.utils.validation import validate_request

profiles_bp = Blueprint("profiles", __name__)


@profiles_bp.route("/profiles", methods=["POST"])
@validate_request(ProfileCreateRequest)
def create_profile(data: ProfileCreateRequest):
    """Register a new business profile"""
    # Create the SQLAlchemy model instance from the validated pydantic data
    new_profile = BusinessProfile(**data.model_dump())

    db_session.add(new_profile)
    db_session.commit()
    db_session.refresh(new_profile)

    # Serialize back out through pydantic
    response_data = ProfileResponse.model_validate(new_profile)
    return jsonify(response_data.model_dump(mode="json")), 201


@profiles_bp.route("/profiles/<uuid:profile_uuid>", methods=["GET"])
def get_profile(profile_uuid):
    """Retrieve a profile and its summary stats"""
    profile = db_session.get(BusinessProfile, profile_uuid)

    if not profile:
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "details": [
                        {"msg": "Profile not found", "type": "resource_missing"}
                    ],
                }
            ),
            404,
        )

    # Calculate summary stats using SQLAlchemy aggregation
    total_queries = (
        db_session.query(func.count(DiscoveredQuery.uuid))
        .filter(DiscoveredQuery.profile_uuid == profile_uuid)
        .scalar()
        or 0
    )

    avg_score = (
        db_session.query(func.avg(DiscoveredQuery.opportunity_score))
        .filter(DiscoveredQuery.profile_uuid == profile_uuid)
        .scalar()
        or 0.0
    )

    # Build the detail response
    response_data = ProfileDetailResponse(
        uuid=profile.uuid,
        name=profile.name,
        domain=profile.domain,
        status=profile.status,
        created_at=profile.created_at,
        total_queries_discovered=total_queries,
        avg_opportunity_score=round(avg_score, 4),
    )

    return jsonify(response_data.model_dump(mode="json")), 200
