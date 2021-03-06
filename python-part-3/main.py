import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import RedirectResponse

from config import settings
from automation import do_long_process, ipf_webhook
from models import Event

app = FastAPI()


@app.get("/", response_class=RedirectResponse)
async def redirect_root():
    return "/docs"


@app.get("/healthcheck", response_model=str)
async def root():
    return "Ok"


@app.post('/ipfabric', status_code=status.HTTP_204_NO_CONTENT)
async def ipfabric(event: Event, request: Request, bg_task: BackgroundTasks, x_ipf_signature: str = Header(None)):
    input_hmac = hmac.new(
        key=settings.ipf_secret.encode(),
        msg=await request.body(),
        digestmod="sha256"
    )
    if not hmac.compare_digest(input_hmac.hexdigest(), x_ipf_signature):
        raise HTTPException(status_code=400, detail="X-IPF-Signature does not match.")
    bg_task.add_task(do_long_process, event)
    bg_task.add_task(ipf_webhook, event)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
