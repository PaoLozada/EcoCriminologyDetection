from fastapi import FastAPI, Request, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
from analysis import main_process, create_map, create_histogram, create_bar_chart

app = FastAPI()

# Configurar CORS para permitir todas las solicitudes (para desarrollo local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica los orígenes permitidos ['http://localhost', 'https://example.com']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar la carpeta estática para servir archivos como background.jpg
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Rutas existentes para procesar datos y gráficos
@app.get("/process_data")

async def process_data(request: Request):
    try:
        df_predictions = main_process()
        df_predictions.to_csv('static/df_predictions.csv', index=False)
        selected_columns = ['municipio', 'Level Deforestation', 'Level Illicit Use', 'Level Ecocidios', 'Level Environment Pollution']
        df_selected = df_predictions[selected_columns]
        df_predictions_html = df_selected.to_html(classes='table table-striped')
        return templates.TemplateResponse("process_data.html", {"request": request, "df_table": df_predictions_html})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@app.get("/create_map")
async def map():
    try:
        create_map()
        file_path = "static/map.html"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="map.html not found")
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/create_histogram", response_class=HTMLResponse)
async def histogram(request: Request):
    try:
        create_histogram()
        return templates.TemplateResponse("histogram.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/create_bar_chart", response_class=HTMLResponse)
async def bar_chart(request: Request):
    try:
        create_bar_chart()
        return templates.TemplateResponse("bar_chart.html", {"request": request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

'''if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)'''
