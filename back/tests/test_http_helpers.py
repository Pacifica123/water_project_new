# back/tests/test_http_helpers.py
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from app.db.schemas import OperationResult
from app.utils.http_helpers import op_endpoint

app = FastAPI()

@app.post("/ok")
@op_endpoint
async def ok_endpoint():
    return OperationResult.ok(data={"a":1}, message="created", meta={"status_code":201})

@app.post("/fail")
@op_endpoint
async def fail_endpoint():
    return OperationResult.fail(message="invalid input", meta={"status_code":422})

@app.post("/err")
@op_endpoint
async def err_endpoint():
    return OperationResult.error("boom")

@pytest.mark.asyncio
async def test_ok_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/ok")
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "ok"
    assert body["data"] == {"a":1}

@pytest.mark.asyncio
async def test_fail_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/fail")
    assert r.status_code == 422
    # при fail бросается HTTPException, в тесте detail содержит тело
    assert "invalid input" in r.text

@pytest.mark.asyncio
async def test_err_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/err")
    assert r.status_code == 500
