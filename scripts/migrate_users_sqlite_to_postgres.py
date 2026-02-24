import os
from sqlalchemy import create_engine, text

# Use the application's app context and models to insert into Postgres
from app import create_app, db
from app.models import User

APP = create_app()

SQLITE_URL = os.environ.get('SQLITE_URL', 'sqlite:///site.db')


def migrate_users():
    sqlite_engine = create_engine(SQLITE_URL)
    with APP.app_context():
        # Ensure target DB tables exist
        db.create_all()

        with sqlite_engine.connect() as conn:
            try:
                rows = conn.execute(text('SELECT id, username, fullname, email, role, password, created_at FROM "user"')).fetchall()
            except Exception:
                # Try without quoting (some SQLite setups)
                rows = conn.execute(text('SELECT id, username, fullname, email, role, password, created_at FROM user')).fetchall()

            inserted = 0
            for r in rows:
                # r is Row; map by position
                username = r['username'] if 'username' in r.keys() else r[1]
                email = r['email'] if 'email' in r.keys() else r[3]
                existing = User.query.filter_by(username=username).first()
                if existing:
                    continue

                user = User(
                    username=username,
                    fullname=(r['fullname'] if 'fullname' in r.keys() else r[2]),
                    email=email,
                    role=(r['role'] if 'role' in r.keys() else r[4]),
                    password=(r['password'] if 'password' in r.keys() else r[5]),
                )
                # Try to preserve created_at if available
                try:
                    user.created_at = (r['created_at'] if 'created_at' in r.keys() else r[6])
                except Exception:
                    pass

                db.session.add(user)
                inserted += 1

            db.session.commit()
            print(f"Inserted {inserted} users into target database")


if __name__ == '__main__':
    print('Starting migration: sqlite -> Postgres (users only)')
    migrate_users()
    print('Migration complete')
