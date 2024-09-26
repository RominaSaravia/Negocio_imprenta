from sqlmodel import Field, Session, SQLModel, create_engine, select,delete,join
from validations import Post_Print,Post_Cart,Patch_Cart,Post_Print_Cart,val_email,Post_user
from datetime import datetime

class Cart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True,unique=True)
    client_name: str = Field(index=True)
    client_email: str
    state: str
    date: str 

class Print(SQLModel, table=True):
    id: int =  Field(default=None, primary_key=True, unique=True)
    cart_id: int = Field(default=None, foreign_key="cart.id")
    page_type: str
    page_size: str
    n_prints: int
    n_copies: int
    color: str
    price: float | None = Field(default=None, index=True)
    url_file: str

class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    password:str

    


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///server/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


#----------------------------CART_TABLE-------------------------------------
def getAllCarts():
    with Session(engine) as session:
        result = []
        result = session.exec(select(Cart)).all()        
        return result
    
def getCart_Print(cart_id:int):
    with Session(engine) as session:
        cart_print = session.exec(  select(Cart,Print).join(Print,isouter=True).where(Cart.id == cart_id) )
        cartset = {}
        printsList = []
        for c, p in cart_print:
            if(c != None):
                cartset = dict(c)
            if(p != None):
                printsList.append(p)

        if(cartset == None or cartset == {}):
            return {'Method':'getCart_Print','isError':True}, ['Error','No Cart Found']
        return cartset,printsList
    

def getCart_Print(cart_id:int):
    with Session(engine) as session:
        cart_print = session.exec(  select(Cart,Print).join(Print,isouter=True).where(Cart.id == cart_id) )
        cartset = {}
        printsList = []
        for c, p in cart_print:
            if(c != None):
                cartset = dict(c)
            if(p != None):
                printsList.append(p)

        if(cartset == None or cartset == {}):
            return {'Method':'getCart_Print','isError':True}, ['Error','No Cart Found']
        return cartset,printsList
    
# Desde el negocio actualiza el state del carrito
def patchCartState(cart_id, cartBody:Patch_Cart):
    with Session(engine) as session:
        cartItem = session.exec( select(Cart).where(Cart.id == cart_id) ).first() #Verifico en la DB la existencia del record
        if(cartItem != None):
            cartItem.state = cartBody.state
            session.add(cartItem)
            session.commit()
            session.refresh(cartItem)
            return cartItem
        else:
            return 'Error: No hay carrito'
        

# El user quiere hacer una nueva compra o modificar un carrito existente
def upsertCart(cartBody:Post_Cart):
    with Session(engine) as session:
        if(cartBody.id): # El body tiene un Id
            result = session.exec( select(Cart).where(Cart.id == cartBody.id) ).first() # verifico en la DB la existencia del record
    
        if(cartBody.id == None or result == None ): # si el carrito no existe o el body no tiene Id (Si se pasó un id y no existe, se crea el carrito)
            result = Cart(
            client_name = cartBody.client_name,
            client_email = cartBody.client_email,
            state = cartBody.state,
            date = datetime.today().strftime('%Y-%m-%d %H:%M:%S') 
            )
        else:
            result.state = cartBody.state # En el caso de quere CANCELAR el pedido
            result.client_email = cartBody.client_email
            result.client_name = cartBody.client_name

        session.add(result)
        session.commit()
        session.refresh(result)
        return result

#----------------------------PRINTS_TABLE-------------------------------------

def getAllPrints():
    with Session(engine) as session:
        result = []
        result = session.exec(select(Print)).all()        
        return result

def getAllPrints():
    with Session(engine) as session:
        result = []
        result = session.exec(select(Print)).all()        
        return result

def addNewPrint(newPrint: Post_Print, newCart: Post_Cart | None = None ):
    with Session(engine) as session:

        if(newPrint.cart_id != None):
            cartItem = session.exec( select(Cart).where(Cart.id == newPrint.cart_id) ).first() # verifico que exista el carrito en la DB
        else:
            cartItem = upsertCart(newCart)
            newPrint.cart_id = cartItem.id

        if( cartItem != None):
            newPrintComplete, error = completePrintDetails(newPrint)
            if (error == '' or error == None):
                session.add(newPrintComplete)
                session.commit()
                session.refresh(newPrintComplete)
                return newPrintComplete
            else:
                return error


        else: # el carrito no se encuentra en la DB
            return 'Error: No hay carrito'



def validate_email(data:val_email):
    with Session(engine) as session:
        cartItem = session.exec( select(Cart).where(Cart.id == data.cart_id).where(Cart.client_email == data.client_email) ).first() 
        if (cartItem != None):
            return True
        return False      


def completePrintDetails(newPrint: Post_Print):
    color_price = 0
    page_price = 0
    print_price = 0
    error = ''

    PrintCompleto = Print(
        cart_id= newPrint.cart_id,
        page_size = newPrint.page_size,
        page_type = newPrint.page_type,
        color = newPrint.color,
        n_copies=newPrint.n_copies,
        n_prints=newPrint.n_prints,
        url_file = newPrint.url_file
        )
    
    # Determinar el precio de la impresion
    match newPrint.color:
        case "color":
            color_price = 500
        case "byn":
            color_price = 250
        case _:
            color_price = 0
            error += 'Falta detallar que color de la impresion. '
    # Determinar el precio del tamaño de la hoja de impresion
    match newPrint.page_size:
        case "A4":
            page_price = 500
        case "A3":
            page_price = 1000
        case _:
            error += 'Falta detallar que tamaño de hoja. '
    # Determinar el precio del papel a usar
    match newPrint.page_type:
        case "Obra 80gr":
            print_price = 250
        case "Ilustracion 120gr":
            print_price = 350
        case _:
            error += 'Falta detallar el tipo de hoja a imprimir. '

    PrintCompleto.price = (color_price + page_price + print_price) * newPrint.n_copies
    print(PrintCompleto)
    return PrintCompleto, error


def deletePrint(id:int):
    with Session(engine) as session:
        print("delete DB")
        result = session.exec(delete(Print).where(Print.id == id))
        session.commit()
        return result

###############__LOGIN___###############################
def authUser(attempEmail,attempPassword):
    with Session(engine) as session:
        user = session.exec( select(Users.id).where(Users.email == attempEmail).where(Users.password == attempPassword) ).first()
    if user != None:
        return user
    
    return None

def addNewUser(user: Post_user ):
    with Session(engine) as session:
        newUser = Users( first_name = user.first_name, last_name = user.last_name , email = user.email, password = user.password)
        session.add(newUser)
        session.commit()
        session.refresh(newUser)
        return newUser