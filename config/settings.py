"""Typed application configuration from environment and Azure Key Vault."""

import logging
import os
from dataclasses import dataclass
from typing import Final

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

logger = logging.getLogger(__name__)

KEY_VAULT_URI_ENV: Final = "KEY_VAULT_URI"

# Only secrets consumed by this service belong here. Keep Key Vault names aligned
# with the variables documented in README.md.
SECRET_ENVIRONMENT_MAPPING: Final = {
    "llm-processor-api-token": "API_TOKEN",
    "openai-api-key": "OPENAI_API_KEY",
    "rabbitmq-password": "RABBITMQ_PASS",
}


@dataclass(frozen=True)
class Settings:
    key_vault_uri: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment_name: str | None = None
    azure_openai_pdf_deployment_name: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_api_key: str | None = None
    openai_api_key: str | None = None
    mcp_api_base_url: str | None = None
    api_token: str | None = None
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_pass: str = "guest"

    @classmethod
    def from_mapping(cls, values: dict[str, str | None]) -> "Settings":
        """Build typed settings from environment-style variable names."""
        port_value = values.get("RABBITMQ_PORT") or "5672"
        try:
            rabbitmq_port = int(port_value)
        except ValueError as error:
            raise ValueError("RABBITMQ_PORT must be an integer") from error

        return cls(
            key_vault_uri=values.get("KEY_VAULT_URI"),
            azure_openai_endpoint=values.get("AZURE_OPENAI_ENDPOINT"),
            azure_openai_deployment_name=values.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_openai_pdf_deployment_name=values.get("AZURE_OPENAI_PDF_DEPLOYMENT_NAME"),
            azure_openai_api_version=values.get("AZURE_OPENAI_API_VERSION") or "2024-10-21",
            azure_openai_api_key=values.get("AZURE_OPENAI_API_KEY"),
            openai_api_key=values.get("OPENAI_API_KEY"),
            mcp_api_base_url=values.get("MCP_API_BASE_URL"),
            api_token=values.get("API_TOKEN"),
            rabbitmq_host=values.get("RABBITMQ_HOST") or "localhost",
            rabbitmq_port=rabbitmq_port,
            rabbitmq_user=values.get("RABBITMQ_USER") or "guest",
            rabbitmq_pass=values.get("RABBITMQ_PASS") or "guest",
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the settings initialized by the single configuration loader."""
    if _settings is not None:
        return _settings
    return load_settings()


def load_settings() -> Settings:
    """Load process environment values, supplemented by Key Vault secrets."""
    global _settings

    process_values = dict(os.environ)
    key_vault_uri = process_values.get(KEY_VAULT_URI_ENV)
    key_vault_values: dict[str, str | None] = {}
    if key_vault_uri:
        key_vault_values = _load_key_vault_secrets(
            key_vault_uri, explicit_values=process_values
        )
        logger.info("Azure Key Vault is configured")
    else:
        logger.info("%s is not set; using process environment values", KEY_VAULT_URI_ENV)

    # The runtime only reads its process environment. Local development tools
    # populate that environment from .env.local before starting the app.
    values = {**key_vault_values, **process_values}
    _settings = Settings.from_mapping(values)
    return _settings


def _load_key_vault_secrets(
    key_vault_uri: str, explicit_values: dict[str, str]
) -> dict[str, str]:
    requested_secrets = []
    for secret_name, environment_name in SECRET_ENVIRONMENT_MAPPING.items():
        explicit_value = bool(explicit_values.get(environment_name))
        if environment_name == "OPENAI_API_KEY":
            explicit_value = explicit_value or bool(explicit_values.get("AZURE_OPENAI_API_KEY"))
        if not explicit_value:
            requested_secrets.append((secret_name, environment_name))

    if not requested_secrets:
        return {}

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)
    secrets: dict[str, str] = {}

    for secret_name, environment_name in requested_secrets:
        try:
            secret_value = client.get_secret(secret_name).value
        except Exception as error:
            raise RuntimeError(
                f"Unable to load Key Vault secret '{secret_name}' from {KEY_VAULT_URI_ENV}"
            ) from error

        if secret_value is None:
            raise RuntimeError(
                f"Key Vault secret '{secret_name}' from {KEY_VAULT_URI_ENV} has no value"
            )
        secrets[environment_name] = secret_value

    return secrets
