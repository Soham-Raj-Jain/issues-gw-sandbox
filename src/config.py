### Coded by - Soham Jain - SJSUID- 019139796 ###
# -----------------------------------------------------------------------------
# src/config.py
# -----------------------------------------------------------------------------
# Purpose:
#   - Centralized configuration management for the project.
#   - Loads environment variables (from system or .env file).
#   - Validates values using Pydantic for type safety.
# -----------------------------------------------------------------------------

import os
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Load .env file automatically in development
# -----------------------------------------------------------------------------
# dotenv helps developers keep secrets (like tokens) in a `.env` file
# instead of hardcoding them into code or committing to Git.
# In production, environment variables should be set by the hosting system.
load_dotenv()


# -----------------------------------------------------------------------------
# Define a strongly-typed settings model using Pydantic
# -----------------------------------------------------------------------------
# - Each field corresponds to a required environment variable.
# - Pydantic validates types (e.g., PORT must be an integer).
# -----------------------------------------------------------------------------
class Settings(BaseModel):
    GITHUB_TOKEN: str        # Personal access token or fine-grained GitHub token
    GITHUB_OWNER: str        # GitHub org/user that owns the repo
    GITHUB_REPO: str         # Repository name
    WEBHOOK_SECRET: str      # Secret string used to validate GitHub webhooks
    PORT: int = 8080         # Default port for running the service


# -----------------------------------------------------------------------------
# Function: get_settings
# -----------------------------------------------------------------------------
# - Reads env vars and constructs a Settings object.
# - Raises a RuntimeError with clear message if something is missing or invalid.
# -----------------------------------------------------------------------------
def get_settings() -> Settings:
    try:
        # Read env vars and initialize Settings model
        return Settings(
            GITHUB_TOKEN=os.environ["GITHUB_TOKEN"],      # must exist
            GITHUB_OWNER=os.environ["GITHUB_OWNER"],      # mu_]()_
