from pydantic import BaseModel

class Post_Cart(BaseModel):
    id: int | None = None
    client_name: str
    client_email: str
    state: str | None = 'New'

class Patch_Cart(BaseModel):
    state: str

class Post_Print(BaseModel):
    n_order: int
    pape_type: str
    n_prints: int
    color: str
    print_size: str
