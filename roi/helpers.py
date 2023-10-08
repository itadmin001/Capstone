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

    url = f"https://api.unsplash.com/search/photos?page=1&query={search}"

    # querystring = {"q": search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "Authorization": "Client-ID p_CW5xrY6ic4EVgsoTGR9ZJpNmD_6k2AGAT64yonGk8",
        "X-Total": "1"
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    img_url = data['results'][0]['urls']['raw']
    return img_url

def calc_roi(purch_price, exp_total, income_total):
    print(purch_price, exp_total, income_total)
    if income_total is None:
        income_total = 0
    exp_total = exp_total - purch
    initial_invest = purch_price
    profit = income_total - initial_invest
    print(f"init invest: {initial_invest}")
    print(f"profit: {profit}")
    roi = (profit / initial_invest) * 100
    print(roi)
    return roi


def array_merge( first_array , second_array ):
    print("array merge")
    if isinstance( first_array , list ) and isinstance( second_array , list ):
        print("first if")
        return first_array + second_array
    elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
        print('elif 1')
        return dict( list( first_array.items() ) + list( second_array.items() ) )
    elif isinstance( first_array , set ) and isinstance( second_array , set ):
        print("elif 2")
        return first_array.union( second_array )
    else:
        print("else")
        return False