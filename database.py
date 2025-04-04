from sqlalchemy import create_engine, text

# engine = create_engine( "mysql+pymysql://username:pass@host/dbname?charset=utf8mb4")
db_connection_string = f"mysql+pymysql://sql12771036:3HyXMYXvZm@sql12.freesqldatabase.com:3306/sql12771036?charset=utf8mb4"
engine = create_engine(db_connection_string)

