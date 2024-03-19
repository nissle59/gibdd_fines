import datetime
import random
import threading
import time
import warnings
from itertools import cycle

import requests

import config
from anticaptcha import Anticaptcha

warnings.filterwarnings("ignore")


def get_proxies_from_url(url=f"http://api-external.tm.8525.ru/proxies?token=5jossnicxhn75lht7aimal7r2ocvg6o7"):
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        try:
            plist = r.json().get('results')
        except:
            plist = []
    else:
        plist = []
    return plist


def get_vins_from_url(url='http://api-external.tm.8525.ru/vins?token=5jossnicxhn75lht7aimal7r2ocvg6o7'):
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        try:
            plist = r.json().get('results')
        except:
            plist = []
    else:
        plist = []
    return plist


class VinDcCheck:
    def __init__(self, proxy=None):
        self.results = []
        self.captch_req_url = 'https://check.gibdd.ru/captcha'
        self.dc_check_url = 'https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/diagnostic'
        self.session = requests.Session()
        # self.api_key = sql_adapter.get_setting('captcha_api_key')
        self.api_key = 'e9e783d3e52abd6101fc807ab1109400'
        self.solver = Anticaptcha(token=self.api_key)
        self.proxy = proxy
        self.captcha = None
        if proxy is not None:
            print(proxy)

    def get_captcha(self):
        print('Getting captcha data')
        if self.proxy:
            try:
                r = self.session.get(self.captch_req_url, verify=False, proxies=self.proxy)
            except:
                self.proxy = next(r_proxies)
                return self.get_captcha()
        else:
            r = self.session.get(self.captch_req_url, verify=False)
        if r:
            result = r.json()
            # config.logger.info(result.get('token'))
            res = self.resolve_captcha(result.get('base64jpg'))
            # config.logger.info(js)
            result.update({'code': res})
        else:
            result = None
        # config.logger.info(json.dumps(result, ensure_ascii=False, indent=2))
        # with open('session.headers', 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(self.session.headers.__dict__, ensure_ascii=False, indent=2))
        #     f.write(json.dumps(r.headers.__dict__, ensure_ascii=False, indent=2))
        # with open('session.cookies', 'wb') as f:
        #     try:
        #         print(self.session.cookies.__dict__)
        #     except:
        #         pass
        #     pickle.dump(self.session.cookies, f)
        return result

    def resolve_captcha(self, captcha_img_b64):
        return self.solver.resolve_captcha(captcha_img_b64)

    def get_vin_code(self, vin_code):
        if not self.captcha:
            self.captcha = self.get_captcha()
        if self.captcha:
            c_token = self.captcha.get('token')
            try:
                c_code = int(self.captcha.get('code'))
            except:
                c_code = 0
            params = {
                'vin': vin_code,
                'checkType': 'diagnostic',
                'captchaWord': c_code,
                'captchaToken': c_token
            }
            self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            if self.proxy:
                try:
                    r = self.session.post(self.dc_check_url, data=params, verify=False, proxies=self.proxy)
                except requests.exceptions.SSLError as ssl_error:
                    self.proxy = next(r_proxies)
                    print(f'{proxy["http"].split("@")[1]} - SSL Error: {ssl_error}, change proxy')
                    return self.get_vin_code(vin_code)
            else:
                r = self.session.post(self.dc_check_url, data=params, verify=False)
            try:
                res = r.json()

                if res.get('code', 200) in ['201', 201]:
                    time.sleep(1)
                    print(f'{vin_code} Captcha error, retrying...')
                    self.captcha = None
                    return self.get_vin_code(vin_code)

                result = res.get('RequestResult').get('diagnosticCards')
                for r in result:
                    r['vin'] = vin_code
                print(f'[{c_code}] {vin_code} - {str(result[0]["dcNumber"])}')

            except Exception as e:
                print(f'[{c_code}] {vin_code} - None')
                try:
                    if res.get('code', 200) in ['201', 201]:
                        pass
                    else:
                        print(e)
                        # if RequestResult.status in ['NO_DATA','ERROR']: need catcher
                        with open(f'responses/{vin_code}.txt', 'w') as f:
                            ex = ''
                            for arg in e.args:
                                ex += arg + '\n'
                            f.write(str(r.status_code) + '\n' + r.text + '\n\n' + str(ex))
                    result = None
                    print(f'{vin_code} - Failed')
                except:
                    result = None
            return result

    # def get_vin_codes(self, cars: list, use_proxy=False):
    #     for vin in cars:
    #         # self.get_vin_code(vin, proxy)
    #         c = 0
    #         prx = None
    #         while c <= config.tries:
    #             try:
    #                 force = False
    #                 if use_proxy:
    #                     prx = next(config.r_proxies)
    #                     config.logger.debug(f'Trying proxy {prx["http"]}')
    #                 if not (vin.get('createdAt', None)):
    #                     force = True
    #                 vin = self.get_vin_code(vin['vin'], prx)
    #                 asyncio.run(sql_adapter.create_dc_for_vin(vin[0], force))
    #                 # sql_adapter.create_dc_for_vin(vin)
    #                 self.results.append(vin[0])
    #                 break
    #             except StopIteration:
    #                 if use_proxy:
    #                     config.r_proxies = cycle(config.proxies)
    #                     prx = next(config.r_proxies)
    #                 c += 1
    #             except Exception as e:
    #                 config.logger.info(e)
    #                 if use_proxy:
    #                     prx = next(config.r_proxies)
    #                 c += 1
    #
    # def multithreading_get_vins(self, cars, use_proxy=True):
    #     start_dt = datetime.datetime.now()
    #     arr_length = len(cars)
    #     self.results = []
    #     t_s = []
    #     tc = config.threads
    #     l_count, l_mod = divmod(len(cars), tc)
    #     l_count += 1
    #     # l_mod = len(cars) % tc
    #     # if l_mod != 0:
    #     #
    #     #     l_mod = len(cars) % config.threads
    #     #     if l_mod == 0:
    #     #         tc = config.threads
    #     #         l_count = len(cars) // tc
    #     #
    #     #     else:
    #     #         tc = config.threads - 1
    #     #         l_count = len(cars) // tc
    #
    #     l_c = []
    #     for i in range(0, config.threads):
    #         config.logger.info(f'{i + 1} of {config.threads}')
    #         min = l_count * i
    #         max = min + l_count
    #         if max > len(cars):
    #             max = min + l_mod
    #         l_c.append(cars[min:max])
    #
    #     for i in range(0, config.threads):
    #         t_s.append(
    #             threading.Thread(target=self.get_vin_codes, args=(l_c[i], use_proxy), daemon=True))
    #     for t in t_s:
    #         t.start()
    #         config.logger.info(f'Started thread #{t_s.index(t) + 1} of {len(t_s)} with {len(l_c[t_s.index(t)])} cars')
    #
    #     for t in t_s:
    #         t.join()
    #         config.logger.info(f'Joined thread #{t_s.index(t) + 1} of {len(t_s)} with {len(l_c[t_s.index(t)])} cars')
    #     stop_dt = datetime.datetime.now()
    #     dt_diff = (stop_dt - start_dt).total_seconds()
    #     if dt_diff > 60:
    #         dt_m, dt_s = divmod(dt_diff, 60)
    #         dt_str = f'{arr_length} records: {int(dt_m)} minutes {round(dt_s)} seconds passed'
    #     elif dt_diff > 3600:
    #         dt_m, dt_s = divmod(dt_diff, 60)
    #         dt_h, dt_m = divmod(dt_m, 60)
    #         dt_str = f'{arr_length} records: {int(dt_h)} hours {int(dt_m)} minutes {round(dt_s)} seconds passed'
    #     else:
    #         dt_str = f'{arr_length} records: {round(dt_diff)} seconds passed'
    #     config.logger.info(dt_str)


def process_thread(vins: list):
    v = VinDcCheck(next(config.r_proxies))
    # v.get_vin_code(cars[0])
    # for vin in cars:
    #     v.get_vin_code(vin)
    #     t = 0.1 + (random.randint(0, 100) / 200)
    #     time.sleep(round(t, 2))
    for vin in vins:
        # self.get_vin_code(vin, proxy)
        c = 0
        prx = None
        while c <= config.tries:
            try:
                force = False
                if v.proxy:
                    # v.proxy = next(config.r_proxies)
                    config.logger.debug(f'Trying proxy {v.proxy["http"]}')
                if not (vin.get('createdAt', None)):
                    force = True
                # vin = v.get_vin_code(vin['vin'])
                vin = v.get_vin_code(vin['vin'])
                t = 0.1 + (random.randint(0, 100) / 200)
                time.sleep(round(t, 2))
                # asyncio.run(sql_adapter.create_dc_for_vin(vin[0], force))
                # sql_adapter.create_dc_for_vin(vin)
                # self.results.append(vin[0])
                break
            except StopIteration:
                if v.proxy:
                    config.r_proxies = cycle(config.proxies)
                    v.proxy = next(config.r_proxies)
                c += 1
            except Exception as e:
                config.logger.info(e)
                if v.proxy:
                    v.proxy = next(config.r_proxies)
                c += 1


def mulithreaded_processor():
    start_dt = datetime.datetime.now()
    length_of_vins_list = len(vins)
    # self.results = []
    array_of_threads = []
    threads_count = config.threads
    vins_in_thread, vins_in_last_thread = divmod(length_of_vins_list, threads_count)
    vins_in_thread += 1

    l_c = []
    for i in range(0, threads_count):
        config.logger.info(f'{i + 1} of {config.threads}')
        slice_low = vins_in_thread * i
        slice_high = slice_low + vins_in_thread
        if slice_high > len(vins):
            slice_high = slice_low + vins_in_last_thread
        l_c.append(vins[slice_low:slice_high])

    for i in range(0, threads_count):
        array_of_threads.append(
            threading.Thread(target=process_thread, args=(l_c[i]), daemon=True))
    for thread in array_of_threads:
        thread.start()
        config.logger.info(
            f'Started thread #{array_of_threads.index(thread) + 1} of {len(array_of_threads)} with {len(l_c[array_of_threads.index(thread)])} cars')

    for thread in array_of_threads:
        thread.join()
        config.logger.info(
            f'Joined thread #{array_of_threads.index(thread) + 1} of {len(array_of_threads)} with {len(l_c[array_of_threads.index(thread)])} cars')
    stop_dt = datetime.datetime.now()
    dt_diff = (stop_dt - start_dt).total_seconds()
    if dt_diff > 60:
        dt_m, dt_s = divmod(dt_diff, 60)
        dt_str = f'{length_of_vins_list} records: {int(dt_m)} minutes {round(dt_s)} seconds passed'
    elif dt_diff > 3600:
        dt_m, dt_s = divmod(dt_diff, 60)
        dt_h, dt_m = divmod(dt_m, 60)
        dt_str = f'{length_of_vins_list} records: {int(dt_h)} hours {int(dt_m)} minutes {round(dt_s)} seconds passed'
    else:
        dt_str = f'{length_of_vins_list} records: {round(dt_diff)} seconds passed'
    config.logger.info(dt_str)


if __name__ == '__main__':
    vins = [
        'YS2P8X40005650198',
        'X8955713550AL1015',
        'Z90628155K1000009',
        'Z9M93403350139634',
        'WDB9702571L796996',
        'X6S58149ZD0001972',
        'WMA06XZZ3LP134718',
        'X90561420P2002339',
        'XLRTE47MS0G294403',
        'W095850007EL05118',
        'XLRTE47MS0G163762',
        'LVBS6PEB9NR016360',
        'WMA06XZZ2LP140333',
        'WMAH05ZZ68W110421',
        'WMA06WZZXHP088080',
        'XLEG4X20005289799',
        'X96330202B2412094',
        'X8955713560AL1148',
        'YV2TBM0A1EB676580',
        'YS2P8X40005591398',
        '9BSG4X20003935533',
        'WMA06XZZ6LP137144',
        'X9056216DD0002141',
        'YV2VBM0C3CB634922',
        'Z0W06WZZ0FV000627',
        'VF617GKA000005875',
        'LFWKWXPN081F00108',
        'X0P65341070000001',
        'VF625GPA000000796',
        'X89637432C4FB5035',
        'WJME2NPH404361780',
        'XDC732407J9001338',
        'XU547508AE0000356',
        'XTC652095L2543034',
        'WMA30XZZ5EW191722',
        'X634744H4H0000715',
        'YV2F2B3G3LA342765',
        'X0V6712HED0000090',
        'YS2G4X20005576603',
        'Z8J2818ZYG0000533',
        'XU547506AM0000161',
        'X89557131J9AH5275',
        'X89174421B0EU9026',
        '1FUJA6CK24DM52394',
        'X89549130D0AK0016',
        'XUL5759N2E0000024',
        'X3W6539CBD0000679',
        'YS2P4X20002099315',
        'XUHMK1128M0000009',
        'X8947667C70AR4034',
        'VF624GPA000074972',
        'Z6FXXXESFXCK68820',
        'XSU28187A80000532',
        'XTC549005J2517376',
        'WMAH05ZZZ3G160034',
        'Z0G658200K5000045',
        'LZGJLDR48CX061755',
        'XDW37026AD0000273',
        'Z9M9321635G686188',
        'WDB9300571L163998',
        'LZGJR4T42MX129539',
        'LZGJR4V45NX042006',
        'Z8C55729DM0001010',
        'X89557131E4AH5654',
        'X89783437D0EX9071',
        'X3W6539A070000487',
        'Y3M551605B0017411',
        'X89VL116H60AG3032',
        'X8958171B10AF4217',
        'X5H564204G0000022',
        'XUH27350EF0000058',
        'X89657191K1AH5193',
        'XWDBHD81070000227',
        'X96330232F2627811',
        'XU42824FSG0000436',
        'XUL17363LJ0000090',
        'LFXAH78WXP3004094',
        'X9633023262148512',
        'LVBS6PEB9PR013526',
        'XUL17363LJ0000089',
        'XTC549005L2537590',
        'WDB9634031L938544',
        'XE26589J9P0000095',
        'WDB9340321L409177',
        '9BSG6X40003976234',
        'LFWMXXRX9M1F46292',
        'WDB9700671K428307',
        'X5H450083C0000011',
        'VF625GPA000004676',
        'X9H47415CGA200026',
        'Z8C55721AM0000079',
        'Z9M9323155G719896',
        'XTC549005M2558619',
        'X634744R4E0000025',
        'WMA89XZZ9GP078896',
        'X9PJSG0D1CW106955',
        'X89254501B0AA3046',
        'Z9M9440325G856229',
        'YS2G4X20002087677',
        'Z9G4389UDN0000273'
    ]

    vins = [{'vin': vin, 'createdAt': None} for vin in vins]
    pxs = []
    config.proxies = get_proxies_from_url()
    for proxy in config.proxies:
        # print(proxy)
        px = f'{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
        d = {
            'http': 'http://' + px,
            'https': 'http://' + px
        }
        if proxy['enabled'] == 1:
            if proxy['type'] == 'HTTPS':
                pxs.append(d)
    config.r_proxies = cycle(pxs)
    for i in range(random.randint(0, len(config.proxies))):
        next(config.r_proxies)

    process_thread(vins)
