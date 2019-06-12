from flask import Flask, render_template, request, flash, redirect
from app import app
from app.states import states
from app.api_helper import *
from urllib.parse import quote


endpoint = "https://developer.nps.gov/api/v1/parks?api_key=1dPktcL1TRUd1cJLwxBWAgJuaVwmmwbvTMfe41rV"
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/state_filter', methods=['POST'])
def state_filter():
    state = request.form['state']
    state = state.replace(" ", "_")
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


    return render_template("filter_result_list.html",
                           parks=park_resp["data"],
                           visitor_centers=visitor_center_resp["data"],
                           state_name=states[state])



@app.route('/main_park_search', methods=['POST'])
def main_park_search():
    query = request.form['query']
    category = request.form['category']
    keyword = query.split()[0] #Take first word of query

    ## Check if the user is querying for visitor centers
    if category == "visitor_centers":
        return vc_main_search(keyword) # Renders the visitor_center_result.html page for the top query

    ## then check if the user is querying for campgrounds
    if category == "campgrounds":
        return campground_main_search(keyword)

    ## Otherwise, user is querying for parks
    endpoint = form_url("parks")
    url = endpoint + "&q=" + keyword + "&fields=images"
    park_resp = nps_call(url)

    # If the list is empty, the response returned nothing
    if not park_resp["data"]:
        return render_template("bad_search.html",
                               query=keyword)

    return render_template("park_result_list.html",
                           parks=park_resp["data"],
                           keyword=keyword)



@app.route('/park_redirect', methods=['POST', 'GET'])
def park_redirect():
    park_code = request.args.get('park_code', None)
    top_result = get_category_parkcode(park_code, "parks")[0] # We take the first result
    # In case the api doesn't return an image on the query
    try:
        image_url = top_result["images"][0]['url']
    except:
        image_url = ""

    alerts = top_n(get_category_parkcode(park_code, "alerts"), 4)
    articles = top_n(get_category_parkcode(park_code, "articles"), 4)
    campgrounds = top_n(get_category_parkcode(park_code, "campgrounds"), 4)
    visitor_centers = top_n(get_category_parkcode(park_code, "visitorcenters"), 4)
    places = top_n(get_category_parkcode(park_code, "places"), 4)
    return render_template('park_result.html',
                           name=top_result["name"],
                           description=top_result["description"],
                           image_url=image_url,
                           news_articles=articles,
                           alerts=alerts,
                           campgrounds=campgrounds,
                           visitor_centers=visitor_centers,
                           places=places)


# Pass an optional 'query" parameter to query for visitor centers on that query string
@app.route('/visitor_center', methods=['POST', 'GET'])
def vc_main_search(query=""):
    if not query: # We are calling this from the filter_result_list.html
        park_code = request.args.get('park_code', None)
        top_result = get_category_parkcode(park_code, "visitorcenters")[0]  # We take the first result
    else: # We are manually querying for a specific visitor center
        endpoint = form_url("visitorcenters")
        url = endpoint + "&q=" + query.split()[0]
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
    url = endpoint + "&q=" + query.split()[0]  # Take first word of query and form url with keyword
    json_resp = nps_call(url)
    # If the list is empty, the response returned nothing
    if not json_resp["data"]:
        return render_template("bad_search.html",
                               query=query)

    top_result = json_resp["data"][0]  # Take the first result


    return render_template('campground_result.html',
                           name = top_result["name"],
                           description=top_result["description"])


@app.route('/campground_redirect', methods=['POST', 'GET'])
def campground_redirect():
    campground_name = request.args.get('campground_name', None)
    campground_keyword = campground_name.split()[0] # Split on whitespace and take first word
    endpoint = form_url("campgrounds")
    url = endpoint + "&q=" + campground_keyword + "&fields=images"

    json_resp = nps_call(url)
    print(url)
    print(json_resp)
    # If the list is empty, the response returned nothing
    if not json_resp["data"]:
        return render_template("bad_search.html",
                               query=id)

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