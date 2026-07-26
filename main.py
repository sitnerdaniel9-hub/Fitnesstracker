from models.base import Base
from cli import run_cli
from db import engine, get_db

Base.metadata.create_all(engine)

def main():
    db = get_db()
    session = next(db)
    try:
        run_cli(session)
    finally:
        db.close()


if __name__ == "__main__":
    main()
