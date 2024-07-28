from environs import Env

env = Env()
env.read_env()

OPENAI_API_KEY = env.str("OPENAI_API_KEY")
SESSION_MIDDL_SECRET_KEY  = env("SESSION_MIDDL_SECRET_KEY")
POSTGRES_URL = env("POSTGRES_URL")
# "postgresql+psycopg2://user:pass@localhost/mydatabase") 

SQLITE_URL = env("SQLITE_URL")