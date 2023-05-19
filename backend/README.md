## How to run docker:
1. run this command in the terminal:
`docker-compose -f docker-compose.yaml up -d`

## How to make migrations:
1. If 'alembic.ini' hasn't been created yet, run it in a terminal:
`cd backend`
`alembic init migrations`

2. In 'backend/alembic.ini' set the url to the db.
_For example:_
`sqlalchemy.url = postgresql://%(DB_USER)s:%(DB_PASS)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s`
Where are the environment variables defined in the ".env" file.
To include these variables, insert the following block of code into the 'migrations/env.py' file after `config = context.config`:
`from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS`
`section = config.config_ini_section`
`config.set_section_option(section, "DB_HOST", DB_HOST)`
`config.set_section_option(section, "DB_PORT", DB_PORT)`
`config.set_section_option(section, "DB_USER", DB_USER)`
`config.set_section_option(section, "DB_NAME", DB_NAME)`
`config.set_section_option(section, "DB_PASS", DB_PASS)`

3. In the 'migrations/env.py' file, replace 'target_metadata = ' with:
`import sys`
`from pathlib import Path`
`sys.path.append(Path(__file__).parent.parent.parent.__str__())`
`from app.db.models import Base`
`target_metadata = Base.metadata`

4. run these commands in the terminal:
`alembic revision --autogenerate`
`alembic upgrade heads`
