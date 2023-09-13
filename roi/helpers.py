import requests
import requests_cache
import decimal
import json




class JSONENcoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,decimal.Decimal):
            return str(obj)
        return json.JSONEncoder(JSONENcoder,self).default(obj)