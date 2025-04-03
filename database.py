from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


password = quote_plus("baps@1907")

# engine = create_engine( "mysql+pymysql://root:pass@host/dbname?charset=utf8mb4")
db_connection_string = f"mysql+pymysql://root:{password}@localhost:3306/project_quiz?charset=utf8mb4"
engine = create_engine(db_connection_string)

