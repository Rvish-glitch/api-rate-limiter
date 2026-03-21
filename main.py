from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"hyy bro ,it is still in development"}
