from fastapi import FastAPI
from .agent.agent import getResponse

# app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")
app = FastAPI(title="HR Chatbot",
              summary="A chatbot to assit staffs with their enqiry")

@app.get("/api/py/healthcheck")
def healthchecker():
    return {"status": "success", "message": "Integrated FastAPI Framework with Next.js successfully!"}

@app.get("/get/response")
def getresponse(query):

    answer = getResponse(query)
    return answer

