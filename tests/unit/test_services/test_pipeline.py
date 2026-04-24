from app.models.pipeline_run import PipelineRun
from app.models.profile import BusinessProfile
from app.models.query import DiscoveredQuery
from app.models.recommendation import ContentRecommendation
from app.services.pipeline import initialize_pipeline_run, run_visibility_pipeline


def test_pipeline_success(client, db, mocker):
    # setup mock profile
    profile = BusinessProfile(
        name="Test Corp",
        domain="test.com",
        industry="Tech",
        description="A test.",
        competitors=[],
    )
    db.add(profile)
    db.commit()

    # initialize the run first so it exists in the DB for the pipeline to find!
    run_uuid = initialize_pipeline_run(profile.uuid)

    # mock query discovery agent class
    mock_discovery_cls = mocker.patch("app.services.pipeline.QueryDiscoveryAgent")
    mock_discovery = mock_discovery_cls.return_value
    mock_discovery.run.return_value = ["Query A", "Query B"]
    mock_discovery.tokens_used = 10

    # mock visibility scoring agent
    mock_scoring_cls = mocker.patch("app.services.pipeline.VisibilityScoringAgent")
    mock_scoring = mock_scoring_cls.return_value
    mock_scoring.run.side_effect = [
        {
            "query_text": "Query A",
            "estimated_search_volume": 100,
            "competitive_difficulty": 50,
            "opportunity_score": 0.8,
            "domain_visible": False,
            "visibility_position": None,
            "intent_category": "informational",
        },
        {
            "query_text": "Query B",
            "estimated_search_volume": 200,
            "competitive_difficulty": 60,
            "opportunity_score": 0.9,
            "domain_visible": False,
            "visibility_position": None,
            "intent_category": "transactional",
        },
    ]
    mock_scoring.tokens_used = 20

    # mock content recommendation agent
    mock_rec_cls = mocker.patch("app.services.pipeline.ContentRecommendationAgent")
    mock_rec = mock_rec_cls.return_value
    mock_rec.run.return_value = [
        {
            "content_type": "Blog",
            "title": "Test Title",
            "rationale": "Because",
            "target_keywords": ["test"],
            "priority": "High",
        }
    ]
    mock_rec.tokens_used = 30

    # execute pipeline using the newly created run_uuid
    result_uuid = run_visibility_pipeline(run_uuid)

    # verify database state
    run = db.get(PipelineRun, result_uuid)
    assert run is not None
    assert run.status == "completed"
    assert run.queries_discovered == 2
    assert run.queries_scored == 2
    assert run.tokens_used == 10 + (20 + 20) + (30 * 2)

    queries = db.query(DiscoveredQuery).filter_by(run_uuid=result_uuid).all()
    assert len(queries) == 2

    recs = db.query(ContentRecommendation).filter_by(profile_uuid=profile.uuid).all()
    assert len(recs) == 2


def test_pipeline_failure_handling(client, db, mocker):
    profile = BusinessProfile(
        name="Fail Corp",
        domain="fail.com",
        industry="Tech",
        description="A test.",
        competitors=[],
    )
    db.add(profile)
    db.commit()

    # initialize the run first
    run_uuid = initialize_pipeline_run(profile.uuid)

    # force query discovery agent to throw an exception
    mock_discovery_cls = mocker.patch("app.services.pipeline.QueryDiscoveryAgent")
    mock_discovery = mock_discovery_cls.return_value
    mock_discovery.run.side_effect = ValueError("LLM exploded")

    # execute pipeline using the newly created run_uuid
    result_uuid = run_visibility_pipeline(run_uuid)

    run = db.get(PipelineRun, result_uuid)
    assert run.status == "failed"
    assert run.error_message == "LLM exploded"
    assert run.queries_discovered == 0
