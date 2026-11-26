
from fastapi import APIRouter
from fastapi.responses import JSONResponse



router = APIRouter()



@router.get("/escalation-logs")
def get_escalation_logs():
    import pandas as pd

    try:
        df = pd.read_csv("escalation.csv")
        logs = df.to_dict(orient="records")
        return logs
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "CSV file not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
