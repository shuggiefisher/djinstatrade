from pymongo import Connection

from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
import csv
from django.http import HttpResponse

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

def get_values_and_sentiment(stock_name):
    
    stock = list(db.stock.find({'name': stock_name}))[0]
    values = list(db.values.find({'stock_id': stock['_id']}))[0]
    sentiment = list(db.sentiment.find({'stock_id': stock['_id']}))[0]
    
    return stock, values, sentiment

def stock(request, stock_name):
    
    stock, values, sentiment = get_values_and_sentiment(stock_name)
    
    context_dict = RequestContext(request, {
            'stock': stock,
            'values': values,
            'sentiment': sentiment
        })
    return render_to_response('stock.html', context_dict)

#sentiment = ['time', 'positive', 'negative', 'neutral']
#values = ['time', 'value']

def unix_datetime_to_date(unix_datetime):
    return datetime.datetime.fromtimestamp(unix_datetime).strftime('%Y-%m-%d')
    
def envelope(request, stock_name):
    
    stock, values, sentiment = get_values_and_sentiment(stock_name)
    
    day_values = []
    for day in values['daily']:
        # create list of dictionary of Date : Stock Value pairs
        day_values.append(dict(time = day[0],
                               value = day[1],
                               date = unix_datetime_to_date(day[0])
                               ))
    
    # I don't know for sure if values and sentiment lists are in the same date order,
    # so I will have to manually find the matches
    for day in sentiment['daily']:
        for day_value in day_values:
            if day_value['time'] == day[0]:
                day_value['positive'] = day[1]
                day_value['negative'] = day[2]
                break
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=envelope.csv'
    
    writer = csv.writer(response)
    writer.writerow(['date','unix_datetime','stock_value','positive','negative'])
    for day_value in day_values:
        writer.writerow([day_value['date'],
                        day_value['time'],
                        day_value['value'],
                        day_value['positive'],
                        day_value['negative']
                        ])
    return response
    

