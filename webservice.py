from flask import Flask, render_template, request, redirect, url_for
import requests
import pygal
from datetime import datetime

app = Flask(__name__)

API_KEY = '5JUJV1WUJIBMM95'
timeSeries = {
    "Intraday": "TIME_SERIES_INTRADAY&interval=15min",
    "Daily": "TIME_SERIES_DAILY",
    "Weekly": "TIME_SERIES_WEEKLY",
    "Monthly": "TIME_SERIES_MONTHLY"
}
chartTypes = {
    "Bar": "bar",
    "Line": "line"
}

def fetch_stock_symbols():
    return ["AAPL", "GOOGL"]  

@app.route('/', methods=['GET', 'POST'])
def index():
    symbols = fetch_stock_symbols()  
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        chart_type = request.form.get('chartType')
        time_series = request.form.get('timeSeries')
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')

        return redirect(url_for('show_chart', symbol=symbol, chart_type=chart_type, time_series=time_series, start_date=start_date, end_date=end_date))

    return render_template('index.html', symbols=symbols, chartTypes=chartTypes.keys(), timeSeriesKeys=timeSeries.keys())

@app.route('/chart')
def show_chart():
    symbol = request.args.get('symbol')
    chart_type = request.args.get('chart_type')
    time_series = request.args.get('time_series')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    symbols = fetch_stock_symbols()
    
    stock_data = get_stock_data(symbol, timeSeries[time_series])
    if not stock_data:
        return "Error: Could not fetch data for the selected stock symbol and time series."
    
    filtered_data = filter_data_by_date(stock_data, start_date, end_date)
    
    chart = generate_chart(chart_type, filtered_data, f"Stock Data for {symbol}")
    chart_svg = chart.render_data_uri()
    
    return render_template('chart.html', chart_svg=chart_svg, symbols=symbols, chartTypes=chartTypes.keys(), timeSeriesKeys=timeSeries.keys())


def get_stock_data(symbol, time_series_function):
    url = f"https://www.alphavantage.co/query?function={time_series_function}&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "Error Message" in data:
        return None
    
    if time_series_function in data:
        return data[time_series_function]
    
    print(f"Unexpected API response structure: {data}") 
    return None


def filter_data_by_date(stock_data, start_date, end_date):
    filtered_data = {}
    for date, daily_data in sorted(stock_data.items()):
        if start_date <= date <= end_date:
            filtered_data[date] = daily_data
    return filtered_data

def generate_chart(chart_type, data, title):
    chart = pygal.Bar() if chart_type == "Bar" else pygal.Line()
    chart.title = title
    chart.x_labels = sorted(data.keys())
    chart.add('Price', [float(data[date]['4. close']) for date in sorted(data.keys())])
    return chart

if __name__ == '__main__':
    app.run(debug=True)
