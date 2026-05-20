import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from gateway.cache.embedder import Embedder
from gateway.config import Settings


@pytest.mark.asyncio
async def test_embedder_local_fallback():
    # Verify embedder works offline/locally without API key
    settings = Settings(openai_api_key=None)
    with patch("gateway.cache.embedder.get_settings", return_value=settings):
        embedder = Embedder()
        vec = await embedder.embed("test message")
        assert len(vec) == 1536
        # Verify normalization
        assert abs(sum(x * x for x in vec) - 1.0) < 1e-5


@pytest.mark.asyncio
async def test_embedder_openai_api_success():
    # Verify embedder successfully calls OpenAI API when key is configured
    settings = Settings(openai_api_key="mock-key")
    mock_embedding = [0.1] * 1536
    
    with patch("gateway.cache.embedder.get_settings", return_value=settings):
        embedder = Embedder()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": mock_embedding}]
        }
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        mock_client_class = MagicMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with patch("gateway.cache.embedder.httpx.AsyncClient", mock_client_class):
            vec = await embedder.embed("hello world")
            assert vec == mock_embedding
            mock_client.post.assert_called_once()
            args, kwargs = mock_client.post.call_args
            assert args[0] == "https://api.openai.com/v1/embeddings"
            assert kwargs["json"]["model"] == "text-embedding-3-small"
            assert kwargs["json"]["input"] == "hello world"


@pytest.mark.asyncio
async def test_embedder_openai_api_failure_fallback():
    # Verify embedder falls back to local deterministic embedding when API fails
    settings = Settings(openai_api_key="mock-key")
    
    with patch("gateway.cache.embedder.get_settings", return_value=settings):
        embedder = Embedder()
        
        # Test HTTP failure (500)
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        mock_client_class = MagicMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with patch("gateway.cache.embedder.httpx.AsyncClient", mock_client_class):
            vec1 = await embedder.embed("hello")
            assert len(vec1) == 1536
            
        # Test exception raised
        mock_client_fail = AsyncMock()
        mock_client_fail.post.side_effect = Exception("network error")
        
        mock_client_class_fail = MagicMock()
        mock_client_class_fail.return_value.__aenter__.return_value = mock_client_fail
        
        with patch("gateway.cache.embedder.httpx.AsyncClient", mock_client_class_fail):
            vec2 = await embedder.embed("hello")
            assert len(vec2) == 1536
            # Assert local deterministic returns same vector for same string
            assert vec1 == vec2

