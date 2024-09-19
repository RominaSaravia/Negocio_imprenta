from fastapi import FastAPI,Request, Response, Cookie
from fastapi.responses import HTMLResponse
from db import create_db_and_tables, getCart_Print , addNewPrint,upsertCart,patchCartState
from validations import Post_Print,Post_Cart,Patch_Cart

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()



@app.get("/",response_class=HTMLResponse)
async def read_items():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/seecart/{cart_id}")
async def get_cart(cart_id : int):
    print('************GET_CART****************')
    result,result2 = getCart_Print(cart_id) 
    return result,result2

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