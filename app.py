from fastapi import FastAPI
import numpy as np
app = FastAPI()

@app.get("/health")
def health_check():
    return "test"#np.random.uniform(0,1)

