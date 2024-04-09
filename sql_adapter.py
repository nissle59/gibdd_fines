import asyncio
import datetime
import json
import random
import re
from itertools import cycle
from pathlib import Path

import config
from database import AsyncDatabase


def del_tz(dt: datetime.datetime):
    dt = dt.replace(tzinfo=None)
    return dt


def convert_to_ts(s: str, short=False):
    if s:
        if short:
            dt = datetime.datetime.strptime(s, '%Y-%m-%d')
        else:
            dt = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        dt = del_tz(dt)
    else:
        dt = None
    # dt = s
    return dt


camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


conf = config.DATABASE


def list_detector(input_data):
    new_data = {}
    if isinstance(input_data, list):
        try:
            data = [dict(record) for record in input_data][0]
        except:
            data = {}
    else:
        data = dict(input_data)
    for key, value in data.items():
        new_data[underscore_to_camel(key)] = data.get(key)
    return new_data


def list_detector_to_list(input_data):
    if isinstance(input_data, list):
        new_data = []
        # data = [dict(record) for record in input_data]
        for record in input_data:
            new_d = {}
            record = dict(record)
            for key, value in record.items():
                new_d[underscore_to_camel(key)] = record.get(key)
            new_data.append(new_d)
    else:
        new_data = {}
        data = dict(input_data)
        for key, value in data.items():
            new_data[underscore_to_camel(key)] = data.get(key)
    return new_data


async def get_setting(setting_name: str):
    query = f"SELECT value FROM dc_base.settings WHERE setting_name = '{setting_name}'"

    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return {}

    data = list_detector(data)

    return data[setting_name]


async def get_active_proxies(proxy_type: str):
    if proxy_type == "HTTPS":
        view_name = 'dc_base.https_active_proxies'
    elif proxy_type == 'SOCKS5':
        view_name = 'dc_base.socks_active_proxies'
    else:
        view_name = 'dc_base.active_proxies'

    query = f"SELECT * FROM {view_name}"
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return []

    data = list_detector_to_list(data)

    return data


async def get_cars_to_update():
    # touched_at = config.touched_at
    query = "SELECT * FROM fines_base.cars_to_update"
    # query = f"select vin, created_at from dcs
    # where dc_number is null or expiry_date < now() or created_at is null or (now()-touched_at) >= '{touched_at} days'"

    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)
        # config.logger.info(data)
        if data is None:
            return []
        # config.logger.info(data)
        data = [{'reg': item['regNumber'], 'sts': item['stsNumber']} for item in list_detector_to_list(data)]
        # config.logger.info(data)
        return data


'''
async def get_proxies_to_file(proxy_type='HTTPS'):
    if proxy_type == "HTTPS":
        view_name = 'dc_base.https_active_proxies'
    elif proxy_type == 'SOCKS5':
        view_name = 'dc_base.socks_active_proxies'
    else:
        view_name = 'dc_base.active_proxies'

    query = f"SELECT * FROM {view_name}"
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return []

    data = list_detector_to_list(data)

    config.proxies = [{'http': f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
                       'https': f'http://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{str(proxy["port"])}'}
                      for proxy in
                      data]
    print(len(config.proxies))
    with open('proxies.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(config.proxies, ensure_ascii=False, indent=2, default=str))
    config.r_proxies = cycle(config.proxies)
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)

    return data


def create_fines_for_car(car, force):
    with open(f'results/{car["request"].replace("/", "-")}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(car, ensure_ascii=False, indent=2, default=str, sort_keys=True))
    return None


def touch_car_at(reg, sts):
    return None


def get_cars_to_file():
    cars = asyncio.run(get_cars_to_update())
    with open('cars.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(cars, ensure_ascii=False, indent=2, default=str))


def get_cars_from_file():
    with open('cars.json', 'r', encoding='utf-8') as f:
        cars = json.loads(f.read())
    return cars
'''


async def all_paid(sts):
    async with AsyncDatabase(**conf) as db:
        done_q = f"update fines_base.fines set status = 'done' where sts_number = '{sts}'"
        data = await db.fetch(done_q)
        if data:
            return data
        else:
            return []


async def insert_fines(fines_list):
    async with AsyncDatabase(**conf) as db:
        with open('sql/insert_fine.sql', 'r', encoding='utf-8') as f:
            query = f.read()
        fines_list_arr = []
        sts = fines_list['sts']
        reg = fines_list['regnum']
        uins_q = f"SELECT resolution_number FROM fines_base.fines WHERE sts_number = '{sts}'"
        base_data = await db.fetch(uins_q)
        base_data = [item['resolutionNumber'] for item in list_detector_to_list(base_data)]
        set_done = []
        new_data = [fine['SupplierBillID'] for fine in fines_list['data']]
        for uin in base_data:
            if uin not in new_data:
                set_done.append(uin)
        if len(set_done) > 0:
            s = f"('{'\',\''.join(set_done)}')"
            done_q = f"update fines_base.fines set status = 'done' where resolution_number in {s}"
            done_data = await db.fetch(done_q)
        for fine in fines_list['data']:
            dt_discount = convert_to_ts(fine.get('DateDiscount', None))
            dt_ssp = convert_to_ts(fine.get('DateSSP', None), short=True)
            dt_create = convert_to_ts(fine.get('DateDecis', None))
            dt_post = convert_to_ts(fine.get('DatePost', None), short=True)
            if dt_discount:
                if (dt_discount - datetime.datetime.now()).days > 0:
                    expire_days = int((dt_discount - datetime.datetime.now()).days)
                else:
                    expire_days = 0
            else:
                expire_days = 0
            # if fine.get('enableDiscount', False):
            #     summa = int(round(fine.get('Summa', 0) / 2, 0))
            # else:
            summa = int(round(fine.get('Summa', 0), 0))
            config.fines_total.append(fine.get('SupplierBillID', None))
            fines_list_arr.append(
                (
                    dt_discount,
                    fine.get('KoAPcode', '0').replace('ч.', '.'),
                    int(fine.get('Division', 0)),
                    fine.get('KoAPtext'),
                    dt_create,
                    expire_days,
                    summa,
                    fine.get('SupplierBillID', None),
                    fine.get('enableDiscount', False),
                    sts,
                    dt_post,
                    dt_ssp
                )
            )
        # [config.logger.debug(str(fine)) for fine in fines_list_arr]
        upd_query = f"""
                    UPDATE fines_base.sts_regnumbers SET 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE sts_number = '{sts}' AND reg_number = '{reg}'
                """
        # config.logger.info(upd_query)

        data = await db.executemany(query, fines_list_arr)
        # config.logger.info(data)
        u_data = await db.fetch(upd_query)
        if data and u_data:
            return data
        else:
            return []


async def insert_divisions(fines_list):
    with open('sql/insert_division.sql', 'r', encoding='utf-8') as f:
        query = f.read()
    fines_list_arr = []
    for fine in fines_list['divisions']:
        fines_list_arr.append(
            (
                int(fine),
                fines_list['divisions'][fine]['name']
            )
        )
    async with AsyncDatabase(**conf) as db:
        data = await db.executemany(query, fines_list_arr)

    if data:
        return data
    else:
        return []


async def insert_laws(fines_list):
    with open('sql/insert_law.sql', 'r', encoding='utf-8') as f:
        query = f.read()
    fines_list_arr = []
    for fine in fines_list['data']:
        id = fine.get('KoAPcode', '0').replace('ч.', '.')
        number = fine.get('KoAPcode', '0').split('ч.')[0]
        try:
            part = fine.get('KoAPcode', '0').split('ч.')[1]
        except:
            part = None
        fines_list_arr.append(
            (
                id, number, part,
                fine.get('KoAPtext')
            )
        )
    async with AsyncDatabase(**conf) as db:
        data = await db.executemany(query, fines_list_arr)

    if data:
        return data
    else:
        return []


async def set_pair_invalid(sts, reg):
    query = f"""
        UPDATE fines_base.sts_regnumbers SET 
            is_valid = False, 
            invalid_at = CURRENT_TIMESTAMP
        WHERE sts_number = '{sts}' AND reg_number = '{reg}'
    """
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)
    if data:
        return True
    else:
        return False


async def touch_pair(sts, reg):
    query = f"""
            UPDATE fines_base.sts_regnumbers SET 
                touched_at = CURRENT_TIMESTAMP
            WHERE sts_number = '{sts}' AND reg_number = '{reg}'
        """
    # config.logger.info(query)
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)
    if data:
        return True
    else:
        return False


async def update_pair(sts, reg):
    query = f"""
            UPDATE fines_base.sts_regnumbers SET 
                updated_at = CURRENT_TIMESTAMP,
                last_checked_at = CURRENT_TIMESTAMP
            WHERE sts_number = '{sts}' AND reg_number = '{reg}'
        """
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)
    if data:
        return True
    else:
        return False


async def find_car(search):
    query = f"SELECT * FROM fines_base.sts_regnumbers WHERE sts_number = '{search}' OR reg_number = '{search}'"

    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)
        # config.logger.info(data)
        if data is None:
            return []
        # config.logger.info(data)
        data = [{'reg': item['regNumber'], 'sts': item['stsNumber']} for item in list_detector_to_list(data)]
        config.logger.info(data)
        return data
