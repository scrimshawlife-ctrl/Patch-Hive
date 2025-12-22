from fastapi import FastAPI
from patch_hive.exports import EXPORTS

app = FastAPI()

@app.get("/abx/functions")
def abx_functions():
    return {"owner": "patch_hive", "functions": EXPORTS}
