from pydantic import BaseModel

class Post_Cart(BaseModel):
    id: int | None = None
    client_name: str
    client_email: str
    state: str | None = 'New'

class Patch_Cart(BaseModel):
    state: str

class Post_Print(BaseModel):
    cart_id: int
    page_type: str
    page_size: str
    n_prints: int
    n_copies: int
    color: str
    url_file: str

