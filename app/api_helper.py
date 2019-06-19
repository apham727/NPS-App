import urllib.request, json

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}


def top_n(arr,n):
    """
    Takes the first n elements of a JSON array.
    :param arr: the array to be truncated.
    :param n: the number of elements to truncate.
    :return: the truncated array.
    """
    if len(arr) > n:
        return arr[0:n-1]
    else:
        return arr

def nps_call(url):
    """
    Calls the National Park service and parses the response into json.
    :param url: a valid url that queries the NPS API
    :return: the JSON-formatted response from the NPS API.
    """
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req).read()
    json_resp = json.loads(resp.decode('utf-8'))
    return json_resp



def form_url(category):
    """
    Forms the main url for making an API call to a particular NPS category
    Examples of some categories include 'parks', 'visitorcenters', 'places'
    :param category: a valid category to query the NPS in the url
    :return: a valid url that can be used to query the NPS API
    """
    return "https://developer.nps.gov/api/v1/" + category + "?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"


def get_category_parkcode(parkcode, category):
    """
    Wrapper function that functions in views.py may call to get a certain category of information
    corresponding to a certain park.
    :param parkcode: a valid US national park code
    :param category: a valid category to query the NPS in the url
    :return: the top response of the NPS service to the query
    """
    endpoint = form_url(category)
    url = endpoint + "&parkCode=" + str(parkcode)
    if category=="people" or category=="places":
        url = url + "&fields=images" # Lets NPS API know to return image urls
    if category == "parks":
        url = url + "&fields=images,addresses"
    if category == "visitorcenters" or category == "campgrounds":
        url = url + "&fields=addresses"
    return nps_call(url)["data"]

