import logging
import os
from typing import Final

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

KEY_VAULT_URI_ENV: Final = "KEY_VAULT_URI"

SECRET_ENVIRONMENT_MAPPING: Final = {
  "cache-connection-string": "CACHE_CONNECTION_STRING",
  "exchange-rate-api-app-id": "EXCHANGE_RATE_API_APP_ID",
  "finance-app-db-connection-string": "CONNECTION_STRING",
  "llm-processor-api-token": "API_TOKEN",
  "openai-api-key": "OPENAI_API_KEY",
  "rabbitmq-password": "RABBITMQ_PASS",
  "redis-password": "REDIS_PASSWORD",
  "registry-password": "REGISTRY_PASSWORD",
  "smtp-password": "SMTP_PASSWORD",
  "auth-secret-key": "AUTH_SECRET_KEY",
}

def load_environment() -> None:
  """Load shared settings and allow ignored local settings to override them."""
  load_dotenv(".env")
  load_dotenv(".env.local", override=True)

  key_vault_uri = os.getenv(KEY_VAULT_URI_ENV)
  if not key_vault_uri:
    logger.info("%s is not set; using local environment values", KEY_VAULT_URI_ENV)
    return

  _load_key_vault_secrets(key_vault_uri)
  logger.info("Loaded application secrets from Azure Key Vault")


def _load_key_vault_secrets(key_vault_uri: str) -> None:
  credential = DefaultAzureCredential()
  client = SecretClient(vault_url=key_vault_uri, credential=credential)

  for secret_name, environment_name in SECRET_ENVIRONMENT_MAPPING.items():
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

    os.environ[environment_name] = secret_value