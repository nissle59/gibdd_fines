import json
import random
import logging
from fastapi import FastAPI, responses, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import config
import service

LOGGER = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    LOGGER = logging.getLogger(__name__ + ".startup")
    await service.update_proxies()
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)
    LOGGER.info("%s: " + 'Updating started', config.name)
    # await mdc()


@app.get("/find_fines_for_car")
async def bdc(search, background_tasks: BackgroundTasks):
    LOGGER = logging.getLogger(__name__ + ".find_fines_for_car")
    background_tasks.add_task(service.find_fines, search)

    res = json.dumps(
        {"status": "success"},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        default=str
    )
    err = {"status": "error"}
    err = json.dumps(err, indent=4, sort_keys=True, default=str)

    if res:
        return responses.Response(
            content=res,
            status_code=200,
            media_type='application/json'
        )

    else:
        return responses.Response(
            content=err,
            status_code=500,
            media_type='application/json'
        )

@app.get("/get_all_fines")
async def mfines(background_tasks: BackgroundTasks, use_proxy=True):
    LOGGER = logging.getLogger(__name__ + ".get_all_fines")
    # config.threads = threads
    background_tasks.add_task(
        service.multithreaded_find_dcs, use_proxy
    )
    res = json.dumps(
        {"status": "success"},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        default=str
    )
    err = {"status": "error"}
    err = json.dumps(err, indent=4, sort_keys=True, default=str)

    if res:
        return responses.Response(
            content=res,
            status_code=200,
            media_type='application/json'
        )

    else:
        return responses.Response(
            content=err,
            status_code=500,
            media_type='application/json'
        )
