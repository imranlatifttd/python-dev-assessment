import uuid


def test_trigger_analysis_not_found(client):
    random_uuid = str(uuid.uuid4())
    response = client.post(f"/api/v1/profiles/{random_uuid}/analyze")
    assert response.status_code == 404


def test_trigger_analysis_success(client, db, mocker, app):
    # create a profile via the API
    payload = {
        "name": "Test API Corp",
        "domain": "testapi.com",
        "industry": "Tech",
        "description": "API Testing",
        "competitors": []
    }
    create_resp = client.post("/api/v1/profiles", json=payload)
    profile_uuid = create_resp.get_json()["profile_uuid"]

    mock_run_uuid = uuid.uuid4()

    from app.models.pipeline_run import PipelineRun
    dummy_run = PipelineRun(uuid=mock_run_uuid, profile_uuid=uuid.UUID(profile_uuid), status="completed")
    db.add(dummy_run)
    db.commit()

    # mock BOTH initialization and execution so the endpoint fetches our dummy run
    mocker.patch('app.api.pipeline.initialize_pipeline_run', return_value=mock_run_uuid)
    mocker.patch('app.api.pipeline.run_visibility_pipeline', return_value=mock_run_uuid)

    app.config["ASYNC_PIPELINE"] = False

    # trigger the analysis
    response = client.post(f"/api/v1/profiles/{profile_uuid}/analyze")

    assert response.status_code == 202
    data = response.get_json()
    assert data["status"] == "completed"
    assert "run_uuid" in data


def test_get_run_status(client, db):
    # create a dummy run
    from app.models.pipeline_run import PipelineRun
    from app.models.profile import BusinessProfile

    profile = BusinessProfile(name="Status Test", domain="status.com", industry="Tech", description="Test")
    db.add(profile)
    db.commit()

    run = PipelineRun(profile_uuid=profile.uuid, status="running")
    db.add(run)
    db.commit()

    response = client.get(f"/api/v1/runs/{run.uuid}")
    assert response.status_code == 200
    assert response.get_json()["status"] == "running"


def test_get_queries_and_recs_empty(client, db):
    from app.models.profile import BusinessProfile
    profile = BusinessProfile(name="Empty Test", domain="empty.com", industry="Tech", description="Test")
    db.add(profile)
    db.commit()

    q_response = client.get(f"/api/v1/profiles/{profile.uuid}/queries")
    assert q_response.status_code == 200
    assert q_response.get_json()["queries"] == []

    r_response = client.get(f"/api/v1/profiles/{profile.uuid}/recommendations")
    assert r_response.status_code == 200
    assert r_response.get_json()["recommendations"] == []


def test_trigger_analysis_rate_limit(client, db, mocker, app):
    # setup mock profile
    from app.models.profile import BusinessProfile
    profile = BusinessProfile(name="Rate Limit Corp", domain="ratelimit.com", industry="Tech",
                              description="Testing 429")
    db.add(profile)
    db.commit()

    mocker.patch('app.tasks.execute_pipeline_task.delay')

    app.config["ASYNC_PIPELINE"] = True

    mock_ip = {'REMOTE_ADDR': '127.0.0.2'}
    resp1 = client.post(f"/api/v1/profiles/{profile.uuid}/analyze", environ_base=mock_ip)
    resp2 = client.post(f"/api/v1/profiles/{profile.uuid}/analyze", environ_base=mock_ip)
    resp3 = client.post(f"/api/v1/profiles/{profile.uuid}/analyze", environ_base=mock_ip)

    # assertions
    assert resp1.status_code == 202
    assert resp2.status_code == 202
    assert resp3.status_code == 429

    error_data = resp3.get_json()
    assert error_data["error"] == "Too Many Requests"
    assert error_data["details"][0]["type"] == "rate_limit_exceeded"