
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(application):
    """Configure and add CORS middleware to the FastAPI application."""

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
