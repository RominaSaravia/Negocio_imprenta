from pydantic import BaseModel

class Post_Cart(BaseModel):
    client_name: str
    client_email: str
    url_file: str

class Post_Print(BaseModel):
    n_order: int
    pape_type: str
    n_prints: int
    color: str
    print_size: str
