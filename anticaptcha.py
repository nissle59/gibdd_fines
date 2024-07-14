import time
import logging
import requests


class Anticaptcha():
    def __init__(self, url ='http://90.188.15.14:9085', token = 'e9e783d3e52abd6101fc807ab1109400'):
        LOGGER = logging.getLogger(__name__ + ".Anticaptcha--init")
        self.url = url
        self.uin = self.url + '/in.php'
        self.ures = self.url + '/res.php'
        self.token = token
        self.id = None
        self.session = requests.session()
        # self.logger = logging.getLogger('Anticaptcha')
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded"
        })

    def _init_request(self, b64image:str):
        LOGGER = logging.getLogger(__name__ + ".Anticaptcha--_init_request")
        data = {
            'method':'base64',
            'body': b64image,
            'key': self.token
        }
        # config.logger.info(data)
        # config.logger.info(self.token)
        r = requests.post(self.uin, data=data)
        if r:
            # config.logger.info(r.text)
            buf = r.text.split('|')
            status = buf[0]
            self.id = buf[1]
            # config.logger.info(r.text)
            #config.logger.info(self.id)
            return self.id
        else:
            self.id = None
            return None

    def _resolve_request(self):
        LOGGER = logging.getLogger(__name__ + ".Anticaptcha--_resolve_request")
        #config.logger.info(self.id)
        if self.id:
            data = {
                'action': 'get',
                'id': self.id,
                'key': self.token
            }
            r = requests.post(self.ures, data=data)
            #config.logger.info(r.status_code)
            if r:
                buf = r.text.split('|')
                status = buf[0]
                result = buf[1]
                #config.logger.info(r.text)
                if status == 'OK':
                    return result
                else:
                    time.sleep(1)
                    return self._resolve_request()
                    #return None
            else:
                return None

    def resolve_captcha(self, captchaImage:str):
        LOGGER = logging.getLogger(__name__ + ".Anticaptcha--resolve_captcha")
        r = self._init_request(captchaImage)
        #config.logger.info(r)
        if r:
            r = self._resolve_request()
            if r:
                return r


if __name__ == '__main__':
    a = Anticaptcha()
    a.resolve_captcha('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')
