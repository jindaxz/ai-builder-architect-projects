"""
Unit tests for Flask server
"""

import sys
sys.path.insert(0, '../src')

import pytest
from server import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_ollama_status(client):
    """Test Ollama status endpoint"""
    response = client.get('/ollama/status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'connected' in data


def test_summarize_missing_data(client):
    """Test summarize with missing data"""
    response = client.post('/summarize',
                          json={})
    assert response.status_code == 400


def test_summarize_missing_query(client):
    """Test summarize with missing query"""
    response = client.post('/summarize',
                          json={'results': []})
    assert response.status_code == 400


def test_summarize_missing_results(client):
    """Test summarize with missing results"""
    response = client.post('/summarize',
                          json={'query': 'test'})
    assert response.status_code == 400


def test_models_endpoint(client):
    """Test models listing endpoint"""
    response = client.get('/models')
    assert response.status_code == 200
    data = response.get_json()
    assert 'models' in data
    assert 'current' in data
