from typing import Annotated
from fastapi import FastAPI,Request, Response, Cookie, Form
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from db import create_db_and_tables, getCart_Print , addNewPrint,upsertCart,patchCartState, validate_email
from validations import Post_Print,Post_Cart,Patch_Cart,val_email

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="server/templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()



@app.get("/",response_class=HTMLResponse)
async def home_page(request: Request, res:Response):
    return templates.TemplateResponse(
        request=request, name="home.html", context={}      
    )



@app.get("/seecart/{cart_id}", response_class=HTMLResponse)
async def get_cart(cart_id : int,request: Request):
    print('************GET_CART****************')
    cartset,printsList = getCart_Print(cart_id) 
    #return cartset,printsList

    return templates.TemplateResponse(
        request=request, name="cart.html", context={"printList":printsList, "cart": cartset}      
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


##################__NAVIGATION__###########################
@app.get("/printcreation", response_class=HTMLResponse)
async def printcreation(request: Request, res:Response): 
    return templates.TemplateResponse(
        request=request, name="printCreation.html", context={}      
    )



##################__CREATION__###########################
@app.post("/printcreation")
async def val_printcreation( cart_id: Annotated[str, Form()],client_name: Annotated[str, Form()],client_email: Annotated[str, Form()] ,page_type: Annotated[str, Form()], page_size: Annotated[str, Form()], color: Annotated[str, Form()] , n_pages: Annotated[int, Form()], n_sides: Annotated[int, Form()] , n_copies: Annotated[int, Form()], res:Response,request: Request):
    if(client_email != '' and cart_id != ''):
        val = val_email(
            cart_id = int(cart_id, base=0), 
            email = client_email
            )
        
        validation = validate_email(val)
        if(validation == False):
            print('------------------validation_false------------------')
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
    else:
        post_cart = Post_Cart(
            client_name= client_name,
            client_email= client_email
        )
        addNewPrint(post_print,post_cart)


    addNewPrint(post_print,None)

    return await get_cart(post_print.cart_id, request)

    # cartset,printsList = await get_cart(post_print.cart_id)

    # print(printsList)

    # return templates.TemplateResponse(
    #     request=request, name="cart.html", context={"printList":printsList, "cart": cartset}      
    # )


##################__VALIDATION__###########################
@app.post("/authbyemail")
async def auth_byemail(body:val_email, res:Response):
    if(body):
        if(validate_email(body)):
            res.status_code = 200
            return True

    res.status_code = 404
    return 'El carrito no se encontró o el email es incorrecto'



