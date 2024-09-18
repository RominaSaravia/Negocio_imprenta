from sqlmodel import Field, Session, SQLModel, create_engine, select,delete

class Cart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True,unique=True)
    client_name: str = Field(index=True)
    client_email: str
    price: float | None = Field(default=None, index=True)
    state: str
    date: str = ''

class Print(SQLModel, table=True):
    id: int =  Field(default=None, primary_key=True, unique=True)
    cart_id: int = Field(default=None, foreign_key="cart.id")
    Page_Size: str 
    n_Pages: str
    price: float | None = Field(default=None, index=True)
    state: str
    date: str = ''

    


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///server/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)