from fastapi import FastAPI
import pandas as pd
import uvicorn
from flask_sqlalchemy import SQLAlchemy



app = FastAPI()



@app.route('/sign', methods=['POST','GET'])
def sign():
    if request.method == 'POST':
        
        return f"Received name: {name}, email: {email}"
    return 


@app.get("/")
def read_root():
    return 'ana oficial information'

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)