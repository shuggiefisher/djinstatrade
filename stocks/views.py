from pymongo import Connection

from django.shortcuts import render_to_response
from django.template import RequestContext

import logging, settings
logging.getLogger().setLevel(logging.DEBUG)
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = settings.LOG_FILE,
    filemode = 'a'
)

con = Connection('109.123.66.160', 27017)
db = con["instatrade"]

def home(request):
    
    stocks = list(db.stock.find())
    
    context_dict = RequestContext(request, {
            'stocks': stocks
        })
    return render_to_response('home.html', context_dict)

def stock(request, stock_name):
    
    logging.debug(stock_name)
    stock = list(db.stock.find({'name': stock_name}))[0]
    values = list(db.values.find({'stock_id': stock['_id']}))[0]
    sentiment = list(db.sentiment.find({'stock_id': stock['_id']}))[0]
    
    context_dict = RequestContext(request, {
            'stock': stock,
            'values': values,
            'sentiment': sentiment
        })
    return render_to_response('stock.html', context_dict)

