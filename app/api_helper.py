import urllib.request, json

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}


# Takes the first n elements of a JSON array
def top_n(arr,n):
    if len(arr) > n:
        return arr[0:n-1]
    else:
        return arr

def nps_call(url):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req).read()
    json_resp = json.loads(resp.decode('utf-8'))
    return json_resp


# Forms the main url for making an API call to a particular NPS category
# Examples of some categories include 'parks', 'visitorcenters', 'places'
def form_url(category):
    return "https://developer.nps.gov/api/v1/" + category + "?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"


def get_category_parkcode(parkcode, category):
    endpoint = form_url(category)
    url = endpoint + "&parkCode=" + str(parkcode)
    if category == "parks" or category=="people" or category=="places":
        url = url + "&fields=images" # Lets NPS API know to return image urls
    return nps_call(url)["data"]

