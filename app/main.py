from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import app.models as models
import app.crud as crud
import app.schemas as schemas

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

items_per_row = 3
rows = 3


@app.get("/")
async def index(request: Request):
    items = crud.get_items()
    item_rows = [
        items[i : i + items_per_row] for i in range(0, len(items), items_per_row)
    ]

    return templates.TemplateResponse(
        "index.html", {"request": request, "item_rows": item_rows}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
