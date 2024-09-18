from fastapi import FastAPI,Request, Response, Cookie
from fastapi.responses import HTMLResponse
from db import create_db_and_tables

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


##Get all prints types available on DB
@app.get("/prints")
async def get_tickets():
    return 


