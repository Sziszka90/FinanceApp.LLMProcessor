from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from config.settings import load_settings
from services.TokenService import TokenService


def test_token_service_accepts_a_valid_bearer_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KEY_VAULT_URI", raising=False)
    monkeypatch.setenv("API_TOKEN", "expected-token")
    load_settings()
    service = TokenService(Mock())

    assert service.validate_token("Bearer expected-token") is True


@pytest.mark.parametrize("authorization", ["Basic expected-token", "Bearer ", "Bearer wrong"])
def test_token_service_rejects_invalid_authorization(
    monkeypatch: pytest.MonkeyPatch, authorization: str
) -> None:
    monkeypatch.delenv("KEY_VAULT_URI", raising=False)
    monkeypatch.setenv("API_TOKEN", "expected-token")
    load_settings()
    service = TokenService(Mock())

    with pytest.raises(HTTPException) as error:
        service.validate_token(authorization)

    assert error.value.status_code == 401


def test_token_service_rejects_requests_when_no_server_token_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("KEY_VAULT_URI", raising=False)
    monkeypatch.delenv("API_TOKEN", raising=False)
    load_settings()
    service = TokenService(Mock())

    with pytest.raises(HTTPException):
        service.validate_token("Bearer any-token")
