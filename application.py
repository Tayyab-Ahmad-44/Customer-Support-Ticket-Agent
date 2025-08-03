
from fastapi import FastAPI

from core.cors import setup_cors
from core.logging import configure_logging
from routers.home import router as home_router
from routers.query import router as query_router
from routers.store_pdf_in_db import router as store_pdf_router


#Configure logging
configure_logging()



application = FastAPI()



# Enable CORS
setup_cors(application)



application.include_router(home_router)
application.include_router(store_pdf_router)
application.include_router(query_router)
