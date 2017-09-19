from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
#from urllib.request import urlopen, Request
from urllib.error import HTTPError
import urllib.request
import json
import os
import datetime

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print("Response:")
    print(json.dumps(res, indent=4))
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "price":
        
        baseurl = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
        alpha_query = makeAlphaQuery(req)
        if alpha_query is None:
            return {}
        alpha_url = baseurl + alpha_query[0] + "&apikey=KO6S7F5GV15OQ4G7"
        result1 = urllib.request.urlopen(alpha_url).read()
        data = json.loads(result1)
        res = makeWebhookResult(data,alpha_query[1])
        return res
        
    # elif req.get("result").get("action") == "feelings":
    #     res = makeWebhookResult(getTwitterFeelings(req), req, stock_symbol)
    #     return res
    
    elif req.get("result").get("action") == "chart":
        res = getChart(req)
        return res
        
    else return {}
    

def getChart(req):
    result = req.get("result")
    parameters = result.get("parameters")
    stock_symbol = parameters.get("stock_symbol")
    chart_url = "https://www.etoro.com/markets/" + stock_symbol + "/chart"
    speech = 'Here is your chart:'
    chart_speech = "Chart for " + stock_symbol

    if source == 'facebook':
        return {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-wallstreetbot-webhook", 
            "data": {
                "facebook": {
                  "attachment": {
                    "type": "template",
                    "payload": {
                            "template_type":"button",
                            "text":speech,
                            "buttons":[
                              {
                                "type":"web_url",
                                "url":chart_url,
                                "title":chart_speech,
                                "webview_height_ratio": "compact"
                              },
                            ]
                        }
                     }
                }
            }
        }



def makeAlphaQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    stock_symbol = str(parameters.get("stock_symbol"))
    date = str(parameters.get("date"))
    if stock_symbol is None:
        return None
    return [stock_symbol,date]


def makeWebhookResult(data,date):
    timeseries = data.get("Time Series (Daily)")
    ofdate = timeseries.get(date)
    closevalue = str(ofdate.get("4. close"))
    print(json.dumps(closevalue, indent=4))

    speech = "The value of @stock_symbol 's share dated @date is: " + closevalue
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "stockkbot"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
