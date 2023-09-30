import requests
import requests_cache
import decimal
import json

requests_cache.install_cache(cache_name = 'image_cache', backend='sqlite', expire_after=900)


class JSONENcoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,decimal.Decimal):
            return str(obj)
        return json.JSONEncoder(JSONENcoder,self).default(obj)
    

def get_image(search):

    url = "https://google-search72.p.rapidapi.com/imagesearch"

    querystring = {"q": search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "X-RapidAPI-Key": "42fd925984msh562e14a38e46f74p1d7d82jsnc9f5517ec678",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    print(data)
    img_url = data['items'][0]['originalImageUrl'] #traversing data dictionary to get the image url we want
    return img_url

def calc_roi(purch_price, exp_total, income_total):
    if income_total == None:
        income_total = 0
    initial_invest = (purch_price + exp_total)
    profit = income_total - initial_invest
    roi = profit / initial_invest
    return roi