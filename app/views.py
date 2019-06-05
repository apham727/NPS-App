from flask import Flask, render_template, request, flash, redirect
from app import app
import os
import urllib.request, json



temp = ["ndb"]


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


endpoint = "https://developer.nps.gov/api/v1/parks?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}

@app.route('/')
@app.route('/index')
def index():
    # # Configure API request
    # endpoint = "https://developer.nps.gov/api/v1/parks?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
    # HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
    # req = urllib.request.Request(endpoint, headers=HEADERS)
    # # Execute request and parse response
    # response = urllib.request.urlopen(req).read()
    # data = json.loads(response.decode('utf-8'))
    #
    # # Prepare and execute output
    # for park in data["data"]:
    #     print(park["fullName"])
    print("DONE")
    return render_template('index.html')


@app.route('/search_result', methods=['POST'])
def search_result():
    ### Query the API for a park and take the first response
    query = request.form['query']
    endpoint = "https://developer.nps.gov/api/v1/parks?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
    url = endpoint + "&q=" + query + "&fields=images"
    req = urllib.request.Request(url, headers=HEADERS)
    response = urllib.request.urlopen(req).read()
    json_resp = json.loads(response.decode('utf-8'))

    # If the list is empty, the response returned nothing
    if not json_resp["data"]:
        return "Nothing found"

    # Otherwise, we take the top result
    top_result = json_resp["data"][0]
    park_code = top_result["parkCode"]
    # print(len(top_result))
    # print(top_result)
    # print(top_result["fullName"])
    # print(top_result["description"])

    #### Grab relevant information about the specific location #####
    ##### Alerts #####
    alerts = get_alerts(park_code)
    ### News Articles #####
    articles = get_new_articles(park_code)
    print("num news articles is " + str(len(articles)))

    # print(top_result)


    # In case the api doesn't return an image on the query
    try:
        image_url = top_result["images"][0]['url']
    except:
        image_url = ""

    return render_template('search_result.html',
                           name = top_result["fullName"],
                           description = top_result["description"],
                           image_url = image_url,
                           news_articles = articles, alerts = alerts)



def get_alerts(parkcode):
    alert_endpoint = "https://developer.nps.gov/api/v1/alerts?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
    url = alert_endpoint + "&parkCode=" + str(parkcode)
    req = urllib.request.Request(url, headers=HEADERS)
    response = urllib.request.urlopen(req).read()
    json_resp = json.loads(response.decode('utf-8'))

    # Extracts the top three alerts
    alerts = json_resp["data"]
    if len(json_resp["data"]) > 4:
        alerts = json_resp["data"][0:3]

    return alerts

def get_new_articles(parkcode):
    alert_endpoint = "https://developer.nps.gov/api/v1/articles?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
    url = alert_endpoint + "&parkCode=" + str(parkcode)
    req = urllib.request.Request(url, headers=HEADERS)
    article_response = urllib.request.urlopen(req).read()
    article_json_resp = json.loads(article_response.decode('utf-8'))

    # Extracts the top three news articles
    articles = article_json_resp["data"]
    if len(article_json_resp["data"]) > 4:
        articles = article_json_resp["data"][0:3]
    return articles

