import asyncio
import json
import random
import threading
from itertools import cycle
from pathlib import Path
import logging
import config
import parser
import sql_adapter

LOGGER = logging.getLogger(__name__)


async def multithreaded_find_dcs(use_proxy=True):
    LOGGER = logging.getLogger(__name__ + ".multithreaded_find_dcs")
    cars = await sql_adapter.get_cars_to_update()
    LOGGER.info(len(cars))
    parser.mulithreaded_processor(cars)


def update_proxies_from_file():
    LOGGER = logging.getLogger(__name__ + ".update_proxies_from_file")
    with open('proxies.json', 'r', encoding='utf-8') as f:
        config.proxies = json.loads(f.read())
    LOGGER.info(len(config.proxies))
    config.r_proxies = cycle(config.proxies)
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)
    return config.proxies


def test():
    LOGGER = logging.getLogger(__name__ + ".test")
    cars = sql_adapter.get_cars_from_file()
    #config.logger.info(len(cars))
    update_proxies_from_file()
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)
    LOGGER.info('Updating started')
    #tc = parser.Fines(proxy=next(config.r_proxies))
    #print(cars[0])
    try:
        prx = next(config.r_proxies)
    except StopIteration:
        config.r_proxies = cycle(config.proxies)
        prx = next(config.r_proxies)
    tc = parser.Fines(prx)
    for car in cars:
        reg = car['reg']
        sts = car['sts']
        c = 0
        while c <= config.tries:
            try:
                force = False
                if tc.proxy:
                    LOGGER.debug(f'Trying proxy {tc.proxy["http"]}')
                car = tc.get_fines(reg, sts)
                LOGGER.debug(json.dumps(car, ensure_ascii=False, indent=2, default=str, sort_keys=True))
                break
            except StopIteration:
                if tc.proxy:
                    config.r_proxies = cycle(config.proxies)
                    tc.proxy = next(config.r_proxies)
                c += 1
            except Exception as e:
                LOGGER.info(e)
                if tc.proxy:
                    tc.proxy = next(config.r_proxies)
                c += 1


async def queue_dc(vin_code):
    LOGGER = logging.getLogger(__name__ + ".queue_dc")
    await update_proxies()
    find_dc(vin_code)


def q_dc(vin_code):
    LOGGER = logging.getLogger(__name__ + ".q_dc")
    asyncio.run(update_proxies())
    find_dc(vin_code)


# async def queue_dc_all():
#     # await update_proxies()
#     cars = await sql_adapter.get_vins_to_update()
#     jobs = []
#     for vin in cars:
#         jobs.append(config.queue.enqueue(multi_dc, vin, timeout=3600))
#     return jobs


# def multi_dc(cars):
#     asyncio.run(update_proxies())
#     parser.mulithreaded_processor(cars)


def find_dc(vin_code):
    LOGGER = logging.getLogger(__name__ + ".find_dc")
    LOGGER.info(f'Started parsing of [{vin_code}]')
    t1 = threading.Thread(target=parser.process_thread, args=([vin_code],), daemon=True)
    t1.start()
    t1.join()


async def dc(vin_code):
    LOGGER = logging.getLogger(__name__ + ".dc")
    return await sql_adapter.find_vin_actual_dc(vin_code)


async def dcs_ended(vin_code):
    LOGGER = logging.getLogger(__name__ + ".dcs_ended")
    return await sql_adapter.find_vin_ended_dcs(vin_code)


async def update_proxies():
    LOGGER = logging.getLogger(__name__ + ".update_proxies")
    #proxies = parser.get_proxies_from_url()
    config.proxies = [{'http': f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
                       'https': f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{str(proxy["port"])}'}
                      for proxy in
                      await sql_adapter.get_active_proxies('HTTPS')]
    LOGGER.info(len(config.proxies))
    config.r_proxies = cycle(config.proxies)
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)
    return config.proxies
    #return await sql_adapter.update_proxies(proxies)


async def find_fines(search: str | list):
    LOGGER = logging.getLogger(__name__ + ".find_fines")
    cars = []
    if isinstance(search, str):
        if search.find(',') > 0:
            search = search.split(',')
            for item in search:
                cars.extend(await sql_adapter.find_car(item))
        else:
            cars.extend(await sql_adapter.find_car(search))
    elif isinstance(search, list):
        for item in search:
            cars.extend(await sql_adapter.find_car(item))
    if len(cars) > 0:
        LOGGER.info(cars)
        parser.mulithreaded_processor(cars)
        # parser.process_thread([cars])





if __name__ == "__main__":
    #asyncio.run(sql_adapter.get_proxies_to_file())
    #sql_adapter.get_cars_to_file()
    asyncio.run(update_proxies())
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)
    LOGGER.info('Updating started')
    asyncio.run(find_fines('9920188781'))
