from pydantic import BaseModel

class val_email(BaseModel):
    cart_id: int
    client_email: str

class Post_Cart(BaseModel):
    id: int | None = None
    client_name: str
    client_email: str
    state: str | None = 'New'

class Patch_Cart(BaseModel):
    state: str

class Post_Print(BaseModel):
    cart_id: int | None = None
    page_type: str
    page_size: str
    n_prints: int
    n_copies: int
    color: str
    url_file: str

class Post_Print_Cart(BaseModel):
    client_name: str
    client_email: str
    cart_id: int | None = None
    page_type: str
    page_size: str
    n_prints: int
    n_copies: int
    color: str
    url_file: str

class Post_user(BaseModel):
    first_name: str
    last_name: str
    email: str
    password:str


class Delete_Print(BaseModel):
    id: str
