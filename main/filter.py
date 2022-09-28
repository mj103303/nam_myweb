from main import app, time, datetime
from main import app


@app.template_filter("formatdatetime")
def format_datetime(value):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    
    value = datetime.fromtimestamp(int(value) / 1000) + offset
    return value.strftime("%Y-%m-%d %H:%M:%S")