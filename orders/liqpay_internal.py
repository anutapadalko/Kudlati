import base64
import hashlib
import json


class LiqPay:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    def cnb_data(self, params):
        params['public_key'] = self.public_key
        json_params = json.dumps(params)
        return base64.b64encode(json_params.encode('utf-8')).decode('utf-8')

    def cnb_signature(self, params):
        data = self.cnb_data(params)
        return self.str_to_sign(self.private_key + data + self.private_key)

    def str_to_sign(self, str_val):
        return base64.b64encode(hashlib.sha1(str_val.encode('utf-8')).digest()).decode('utf-8')
