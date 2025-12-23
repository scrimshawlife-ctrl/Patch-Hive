from fastapi import FastAPI
from patchhive.exports import EXPORTS

app = FastAPI()

@app.get("/abx/functions")
def abx_functions():
    return {
        "owner": "patchhive",
        "functions": EXPORTS
    }
