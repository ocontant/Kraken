import pytest
from unittest.mock import AsyncMock, patch
from krakenfx.services.balanceService import fetch_account_balance

@pytest.mark.asyncio
async def test_fetch_account_balance():
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "error": [],
        "result": {
            "AAVE": "0.0000000000",
            "AVAX": "0.0000000000",
            "GALA": "0.0000000000",
            "KFEE": "0.00",
            "MATIC": "0.0000000000",
            "SOL": "0.0000000000",
            "USDC": "0.00001000",
            "USDT": "0.00000000",
            "XETH": "0.0000000000",
            "XXBT": "2.0023152700",
            "XXDG": "0.00000000",
            "XZEC": "0.0000000000",
            "ZUSD": "0.0000"
        }
    }
    mock_response.raise_for_status = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with pytest.raises(ValueError, match="API Error:"):
            result = await fetch_account_balance()
            await mock_response.raise_for_status()
            assert result.result.root["XXBT"] == "2.0023152700"
