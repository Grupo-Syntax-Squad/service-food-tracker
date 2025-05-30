# service-food-tracker 🐶

[All commands](#command-blocks)

## Setup database

> [!NOTE] > <strong><h4>Install docker compose and start PostgreSQL</h4></strong>
>
> <details>
>  <summary><strong>Ubuntu</strong> (click here)</summary>
>
> ```bash
> sudo apt install docker-compose
> ```
>
> </details>
> <details>
>  <summary><strong>Windows</strong> (click here)</summary>
>
> ```powershell
> choco install docker-compose
> ```
>
> </details>
> <details>
>  <summary><strong>Mac</strong> (click here)</summary>
>
> ```bash
> brew install docker-compose
> ```
>
> </details>

##### After installed docker-compose:

```bash
docker-compose up -d
```

> This command will launch a postgres container configured to run the application database.

## Virtual enviroment

> [!NOTE] > <strong><h4>Install python venv</h4></strong>

<details>
<summary><strong>Ubuntu</strong> (click here)</summary>
   
```bash
sudo apt install python3.12-venv
```
## Install dependencies and Activate virtual enviroment

```bash
python3 -m venv .venv
source .venv/bin/activate
npm i
pip install -r requirements.txt
```

</details>
<details>
<summary><strong>Windows</strong></summary>

```powershell
pip install virtualenv
```

## Install dependencies and Activate virtual enviroment

```bash
python -m venv .venv
.\.venv\Scripts\Activate
npm i
pip install -r requirementsWindows.txt
```

</details>
<details>
<summary><strong>Mac</strong></summary>
   
```bash
brew install python@3.12
```

## Install dependencies and Activate virtual enviroment

```bash
python3 -m venv .venv
source .venv/bin/activate
npm i
pip install -r requirements.txt
```

> </details>

> [!IMPORTANT]
> To configure other requirements and dependencies run this:

```bash
npm install
```

## Alembic

> [!NOTE] > <strong><h4>Alembic init</h4></strong>

```bash
alembic init alembic
```

> [!NOTE] > <strong><h4>Set database URI inside of alembic.ini file</h4></strong>

```ini
sqlalchemy.url = postgresql://postgres:password@localhost/foodtracker
```

> [!IMPORTANT]
> After you set alembic, go to the alembic directory and paste in the file env.py this:

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from dotenv import load_dotenv
import os
from src.database.models import Base

load_dotenv()
#Configure environment variables
database_url = os.getenv('DATABASE_URL')
print(database_url)
if not database_url:
   raise ValueError("DATABASE_URL não encontrada no arquivo .env")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", database_url)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Alembic revision and upgrade

```bash
alembic revision --autogenerate
alembic upgrade head
```

> [!IMPORTANT]
> If you need to delete database and create again run this command:

```bash
alembic stamp head --purge
```

## To load the env variables in your envirorment:

```bash
export $(grep -v '^#' .env | xargs)
```

## Run application in development mode

```bash
cd src
fastapi dev main.py --host 0.0.0.0
```

<span id=#command-blocks></span>

## Commands blocks

```bash
# Ubuntu
sudo apt install python3.12-venv
docker-compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)

# Windows
pip install virtualenv
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)


# Mac
brew install python@3.12
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
```

### Alembic

```bash
alembic init alembic
alembic revision --autogenerate
alembic upgrade head
alembic stamp head --purge
```

### 🗃️ Directory Structure

<div align="center">

| Directory                         | Description                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| :open_file_folder: src/           | Main project directory, containing dependencies, source code, and media files.       |
| :open_file_folder: src/database   | Database-related code.                                                               |
| :open_file_folder: src/modules    | All project modules and communication with external services.                        |
| :open_file_folder: src/routers    | Service requests (backend server and API) via GET, POST, DELETE, and UPDATE methods. |
| :open_file_folder: src/schemas    | Project schemas and data models.                                                     |
| :page_facing_up: .env.example     | Example environment variables file.                                                  |
| :page_facing_up: .gitignore       | Specifies files and directories to be ignored by Git.                                |
| :page_facing_up: alembic.ini      | Configuration file for Alembic migrations.                                           |
| :page_facing_up: pyproject.toml   | Configuration file for Python dependencies and tools.                                |
| :page_facing_up: README.md        | Main documentation file for the project.                                             |
| :page_facing_up: requirements.txt | List of dependencies required to run the project.                                    |
