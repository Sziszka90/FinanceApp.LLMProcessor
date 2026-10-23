import pytest
from pydantic import ValidationError

from models.ChatMessage import ChatMessage
from models.McpTopTransactionGroupsRequest import McpTopTransactionGroupsRequest


def test_chat_message_accepts_aliases_and_trims_whitespace() -> None:
    message = ChatMessage.model_validate({"Role": " user ", "Content": " hello "})

    assert message.role == "user"
    assert message.content == "hello"


def test_mcp_top_groups_validator_uses_pydantic_v2_info_signature() -> None:
    with pytest.raises(ValidationError):
        McpTopTransactionGroupsRequest.model_validate(
            {
                "tool_name": "GetTopTransactionGroups",
                "start_date": " ",
                "end_date": "2026-01-01T00:00:00Z",
                "user_id": "user-1",
                "correlation_id": "request-1",
            }
        )
