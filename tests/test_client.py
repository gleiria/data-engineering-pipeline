from pathlib import Path

import pytest
from unittest.mock import MagicMock
from src.client import load_yaml, fetch_weather

# I will perform pure unit tests only:
# • Does load_yaml() correctly read YAML?
# • Does fetch_weather() correctly handle a successful response?
# • Does it raise an error on failure?

def test_load_yaml(tmp_path: Path):
    # arrange: Given a sample YAML file
    sample_yaml = """
    key1: value1
    key2: value2
    """
    file = tmp_path / "test.yaml"
    file.write_text(sample_yaml)

    # act: When I load it using load_yaml()
    result = load_yaml(file)

    # assert: Then I should get the correct dictionary
    assert result == {'key1': 'value1', 'key2': 'value2'}



def test_fetch_weather_success(monkeypatch):
    # arrange: Given a successful API response
    # create mock response object
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'name': 'Lisbon',
        'main': {'temp': 20},
        'weather': [{'description': 'clear sky'}]
    }

    # make requests.get return the mock response
    def mock_get(*args, **kwargs):
        return mock_response
    
    monkeypatch.setattr("src.client.requests.get", mock_get)

    # act: When I call fetch_weather()
    result = fetch_weather("Lisbon", "fake_api_key", "metric")

    # assert: Then I should get the expected data
    assert result['name'] == 'Lisbon'
    assert result['main']['temp'] == 20
    assert result['weather'][0]['description'] == 'clear sky'




