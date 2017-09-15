
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

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
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "CurrentPrice.price":
        return {}
    baseurl = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
    alpha_query = makeAlphaQuery(req)
    if alpha_query is None:
        return {}
    alpha_url = baseurl + alpha_query + "&apikey=W6FZRHLN6JUQWMX7"
    result = urlopen(alpha_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeAlphaQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    stock_symbol = str(parameters.get("stock_symbol"))
    date = parameters.get("date")
    if stock_sumbol is None:
        return None
    if date is None:
        date = str(datetime.date.today())

    return [stock_symbol,date]


def makeWebhookResult(data):
    timeseries = rcvd_data.get("Time Series (Daily)")
    ofdate = timeseries.get(stockdate)
    closevalue = str(ofdate.get("4. close"))
    print(json.dumps(closevalue, indent=4))

    speech = "Today's price is " + closevalue
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
