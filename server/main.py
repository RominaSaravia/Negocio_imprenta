from typing import Annotated
from fastapi import FastAPI,Request, Response, Cookie, Form
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from db import create_db_and_tables, getCart_Print , addNewPrint,upsertCart,patchCartState, validate_email,authUser,addNewUser,deletePrint
from validations import Post_Print,Post_Cart,Patch_Cart,val_email,Post_user,Delete_Print

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory="server/templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.mount(
    "/server/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "server/static"),
    name="static",
)



@app.get("/",response_class=HTMLResponse)
async def home_page(request: Request, res:Response):
    userId = validateAuth(request._cookies)

    return templates.TemplateResponse(
        request=request, name="home.html", context={"logged":userId}      
    )



@app.get("/seecart/{cart_id}", response_class=HTMLResponse)
async def get_cart(cart_id : int,request: Request):
    userId = validateAuth(request._cookies)

    cartset,printsList = getCart_Print(cart_id) 

    return templates.TemplateResponse(
        request=request, name="cart.html", context={"printList":printsList, "cart": cartset, "logged":userId}      
    )


@app.post("/newCart")
async def post_cart(body: Post_Cart):
    result = upsertCart(body)
    return result

##########__ONLY__ADMIN__#################


@app.patch("/newStateOnCart/{cart_id}")
async def patch_cart(body: Patch_Cart, cart_id : int):
    result = patchCartState(cart_id, body)
    return result




##########################################

@app.post("/newPrint")
async def post_print(body: Post_Print):
    result = addNewPrint(body)
    return result

@app.delete("/deletePrint/{id}")
async def delete_print(id: int):
    print("delete main")
    result = deletePrint(id)
    return result


##################__NAVIGATION__###########################
@app.get("/printcreation", response_class=HTMLResponse)
async def printcreation(request: Request, res:Response): 
    return templates.TemplateResponse(
        request=request, name="printCreation.html", context={}      
    )



##################__CREATION__###########################
@app.post("/printcreation", response_class=RedirectResponse)
async def val_printcreation( cart_id: Annotated[str, Form()],client_name: Annotated[str, Form()],client_email: Annotated[str, Form()] ,page_type: Annotated[str, Form()], page_size: Annotated[str, Form()], color: Annotated[str, Form()] , n_pages: Annotated[int, Form()], n_sides: Annotated[int, Form()] , n_copies: Annotated[int, Form()], res:Response,request: Request) ->RedirectResponse :
    if(client_email != '' and cart_id != ''):
        val = val_email(
            cart_id = int(cart_id, base=0), 
            client_email = client_email
            )
        
        validation = validate_email(val)
        if(validation == False):
            return 'Error: Email incorrecto' 
    
    n_prints = n_pages * n_sides
    post_print = Post_Print(
                    page_type =page_type,
                    page_size =page_size,
                    n_prints= n_prints,
                    n_copies = n_copies,
                    color =color,
                    url_file = ''
                    )
    if(cart_id != '' and cart_id != None ):
        post_print.cart_id = int(cart_id)
        addNewPrint(post_print,None)
        redirectR = RedirectResponse(url='/seecart/'+cart_id,status_code=303)
        return redirectR
    else:
        post_cart = Post_Cart(
            client_name= client_name,
            client_email= client_email
        )
        addNewPrint(post_print,post_cart)
        redirectR = RedirectResponse(url='/seecart/'+str(post_print.cart_id),status_code=303 )
        return redirectR
        


##################__VALIDATION__###########################
@app.post("/authbyemail")
async def auth_byemail(body:val_email, res:Response):
    if(body):
        if(validate_email(body)):
            res.status_code = 200
            return True

    res.status_code = 404
    return 'El carrito no se encontró o el email es incorrecto'



############__USER__######
@app.post("/newUser")
async def newUser(user:Post_user):
    return addNewUser(user)


#################__LOGIN__####################################   

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request, res:Response): 
    return templates.TemplateResponse(
        request=request, name="login.html", context={}      
    )

@app.post("/login")
async def validateLogin(email: Annotated[str, Form()] ,password: Annotated[str, Form()], res:Response) ->RedirectResponse :
    userAuth = authUser(email, password)

    if userAuth != None :
        res.status_code = 200
        redirectR = RedirectResponse(url='/',status_code=303)
        redirectR.set_cookie('cookieUserId', userAuth)
        return redirectR
    else:
        res.status_code = 404
        redirectR = RedirectResponse(url='/login',status_code=303)
        return redirectR

#### ------------COOKIES----------------------------

def validateAuth(cookies):
    if 'cookieUserId' in cookies.keys():
        return cookies['cookieUserId']
    else:
        return False

@app.get("/auth/{userId}")
async def authenticate( res:Response, userId:int=1):
    res.set_cookie('cookieUserId',userId)
    return 'Authenticated OK'


@app.get("/read_cookie")
async def get_cookie(request: Request):
    print(f'Cookie: {request._cookies}')
    userId = validateAuth(request._cookies)
    return userId

@app.get("/delete_cookie", response_class=RedirectResponse)
async def delete_cookie()->RedirectResponse :
    redirect = app.url_path_for('get_login')
    redirectR = RedirectResponse(url='/login')
    redirectR.delete_cookie('cookieUserId')
    return redirectR
