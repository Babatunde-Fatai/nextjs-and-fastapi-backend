from fastapi import FastAPI
from .agent.agent import getResponse
from .data.insert_to_db import populate_table

# app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")
app = FastAPI(title="Sorcing Chatbot",
              summary="A chatbot to assist staffs with their enqiry")

@app.get("/api/py/healthcheck")
def healthchecker():
    return {"status": "success", "message": "Integrated FastAPI Framework with Next.js successfully!"}

@app.get("/get/response")
def getresponse(query):

    answer = getResponse(query)
    return answer

@app.post("/post/create-table")
def getresponse(num: int = 200):

    res = populate_table(num)

    
    return res


