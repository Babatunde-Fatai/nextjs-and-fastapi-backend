from fastapi import FastAPI
from .agent.agent import getResponse
from .data.insert_to_db import populate_table
from .data.get_from_db import get_invoice_data, get_procurement_reports
from langserve import add_routes


# app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")
app = FastAPI(title="Sourcing Chatbot",
              summary="A chatbot to assist staffs with their enqiry")

@app.get("/api/py/healthcheck")
def healthchecker():
    return {"status": "success", "message": "Integrated FastAPI Framework with Next.js successfully!"}

@app.get("/get/AI/response")
def get_AI_response(query):

    answer = getResponse(query)

    return answer

@app.post("/post/create-table")
def insert_to_table(num: int = 200):

    res = populate_table(num)

    return res

@app.get("/post/get-details")
def get_from_table(supplier_id_name = [], data_type=str):

    # res = search_suppliers(supplier_id=supplier_id, supplier_name=supplier_name)
    res = get_invoice_data(supplier_id_name, data_type)

    return res


