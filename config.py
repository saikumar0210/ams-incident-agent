"""
config.py

Centralized configuration for the AMS Incident Agent.
All values are loaded from environment variables with sensible defaults.
"""
import os

from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()


class Config:

    # =====================================================
    # Application
    # =====================================================

    APPLICATION_NAME = os.getenv(
        "APPLICATION_NAME",
        "AMS Incident Agent"
    )

    APPLICATION_VERSION = os.getenv(
        "APPLICATION_VERSION",
        "1.0.0"
    )

    # Deployment environment label e.g. DEV, STAGING, PROD
    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "DEV"
    )

    # =====================================================
    # Server
    # =====================================================

    # Host the FastAPI server binds to
    HOST = os.getenv(
        "HOST",
        "0.0.0.0"
    )

    # Port the FastAPI server listens on
    PORT = int(
        os.getenv(
            "PORT",
            "8001"
        )
    )

    # =====================================================
    # Groq
    # =====================================================

    # Groq API key for authenticating requests
    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY"
    )

    # Groq model to use for inference
    # Default: llama-3.3-70b-versatile — fast, free, and capable
    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )
