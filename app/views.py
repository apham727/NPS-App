from flask import Flask, render_template, request, flash, redirect
from app import app
from app.states import states
from app.api_helper import *


endpoint = "https://developer.nps.gov/api/v1/parks?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/state_filter', methods=['POST'])
def state_filter():
    state = request.form['state']
    # Request parks in the state
    endpoint = form_url("parks")
    url = endpoint + "&stateCode=" + state + "&fields=images"
    park_resp = nps_call(url)

    # Request visitor centers in the state
    endpoint = form_url("visitorcenters")
    url = endpoint + "&stateCode=" + state
    visitor_center_resp = nps_call(url)

    if not park_resp["data"] and not visitor_center_resp["data"]: # No parks or visitor centers found in this state
        return render_template("state_nothing.html",
                               state=state)


    return render_template("result_list.html",
                           parks=park_resp["data"],
                           visitor_centers=visitor_center_resp["data"],
                           state_name=states[state])



@app.route('/main_park_search', methods=['POST'])
def main_park_search():
    query = request.form['query']
    ## First check if the query contained 'visitor center'.
    vc_keywords = ["visitor", "center", "visitor center", "Visitor Center"]
    if any(vc_keyword in query for vc_keyword in vc_keywords):
        return vc_main_search(query) # Renders the visitor_center_result.html page for the top query


    ## then check if the query contains the phrase campground
    camp_keywords = ["campground", "camp ground", "Campground", "Camp Ground"]
    if any(camp_keyword in query for camp_keyword in camp_keywords):
        return campground_main_search(query)

    ### Query the API for a park and take the first response
    endpoint = form_url("parks")
    url = endpoint + "&q=" + query + "&fields=images"
    json_resp = nps_call(url)

    # If the list is empty, the response returned nothing
    if not json_resp["data"]:
        return render_template("bad_search.html",
                               query=query)

    # Otherwise, we take the top result
    top_result = json_resp["data"][0]
    park_code = top_result["parkCode"]

    alerts = top_n(get_category_parkcode(park_code, "alerts"),4)
    articles = top_n(get_category_parkcode(park_code, "articles"),4)


    # In case the api doesn't return an image on the query
    try:
        image_url = top_result["images"][0]['url']
    except:
        image_url = ""

    campgrounds = top_n(get_category_parkcode(park_code, "campgrounds"),4)
    visitor_centers = top_n(get_category_parkcode(park_code, "visitorcenters"),4)
    places = top_n(get_category_parkcode(park_code, "places"),4)

    return render_template('park_result.html',
                           name = top_result["name"],
                           description = top_result["description"],
                           image_url = image_url,
                           news_articles = articles,
                           alerts = alerts,
                           campgrounds=campgrounds,
                           visitor_centers=visitor_centers,
                           places=places)



@app.route('/park_search')
def park_search():
    park_code = request.args.get('park_code', None)
    top_result = get_category_parkcode(park_code, "parks")[0] # We take the first result
    alerts = top_n(get_category_parkcode(park_code, "alerts"), 4)
    articles = top_n(get_category_parkcode(park_code, "articles"), 4)

    # In case the api doesn't return an image on the query
    try:
        image_url = top_result["images"][0]['url']
    except:
        image_url = ""

    campgrounds = top_n(get_category_parkcode(park_code, "campgrounds"), 4)
    visitor_centers = top_n(get_category_parkcode(park_code, "visitorcenters"), 4)
    places = top_n(get_category_parkcode(park_code, "places"), 4)
    return render_template('park_result.html',
                           name = top_result["name"],
                           description = top_result["description"],
                           image_url = image_url,
                           news_articles = articles, alerts = alerts)


# Pass an optional 'query" parameter to query for visitor centers on that query string
@app.route('/visitor_center')
def vc_main_search(query=""):

    if not query: # We are calling this from the result_list.html
        park_code = request.args.get('park_code', None)
        top_result = get_category_parkcode(park_code, "visitorcenters")[0]  # We take the first result
    else: # We are manually querying for a specific visitor center
        endpoint = form_url("visitorcenters")
        url = endpoint + "&q=" + query
        json_resp = nps_call(url)
        # If the list is empty, the response returned nothing
        if not json_resp["data"]:
            return render_template("bad_search.html",
                                   query=query)

        top_result = json_resp["data"][0] # Take the first result


    return render_template('visitor_center_result.html',
                           name=top_result["name"],
                           description=top_result["description"],
                           url=top_result['url'])


# Searches for the campground
def campground_main_search(query):
    endpoint = form_url("campgrounds")
    url = endpoint + "&q=" + query + "&fields=images"
    json_resp = nps_call(url)
    # If the list is empty, the response returned nothing
    if not json_resp["data"]:
        return render_template("bad_search.html",
                               query=query)

    top_result = json_resp["data"][0]  # Take the first result

    # In case the api doesn't return an image on the query
    try:
        image_url = top_result["images"][0]['url']
    except:
        image_url = ""

    return render_template('campground_result.html',
                           name = top_result["name"],
                           description=top_result["description"],
                           image_url=image_url,
                           reseverationsUrl=top_result["reservationsUrl"])

