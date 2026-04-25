print('Importing settings...')
from app.core.config import settings
print('Importing logging...')
from app.core.logging import setup_logging
print('Importing database...')
from app.core.database import init_db
print('Importing routers...')
from app.routers import auth
print('Done')
