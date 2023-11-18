import asyncio
import datetime
import aiofiles
import json
import requests

async def get_rainfall():
    # Get the rainfall stats from the cache
    async with aiofiles.open('data/rainfall.json', 'r') as f:
        stats = json.loads(await f.read())
    return stats

async def update_rainfall_cache():
    STATION = ['berrylands', '286392TP']
    # Get the rainfall data from the API
    data = await get_rainfall_data(STATION[1])
    time_now = datetime.datetime.now()
    # Initialise the datetimes defining the start of each day
    yesterday_start = (time_now - datetime.timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
    today_start = time_now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Initialise the counting variables
    total = 0
    total_today = 0
    total_yesterday = 0
    # Initalise the flags
    today = False
    yesterday = False
    # Loop through each reading in the data
    for reading in data:
        total += data[reading]
        if not yesterday and not today:
            if datetime.datetime.strptime(reading, '%Y-%m-%dT%H:%M:%SZ') > yesterday_start:
                yesterday = True
        elif yesterday:
            if datetime.datetime.strptime(reading, '%Y-%m-%dT%H:%M:%SZ') > today_start:
                yesterday = False
                today = True
            else:
                total_yesterday += data[reading]
        elif today:
            total_today += data[reading]
            # By the end of the for loop, the last_reading variable should be correct
            # probably a bad way to do this, but we ball
            last_reading = reading
    average_total_day = total / 7
    async with aiofiles.open('data/rainfall.json', 'w') as f:
        await f.write(json.dumps({
            'total': round(total, 1),
            'total_today': round(total_today, 1),
            'total_yesterday': round(total_yesterday, 1),
            'average_total_day': round(average_total_day, 1),
            "units": "mm",
            "last_reading": last_reading,
            "station": STATION[0],
            "updated": round(time_now.timestamp(), 0)
        }, indent=4))
    
    



async def get_rainfall_data(station = '286392TP'):
    time_now = datetime.datetime.now()
    week_ago = time_now - datetime.timedelta(weeks=1)
    # Generate the correct URL for the request
    url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{station}/readings?since={week_ago.strftime('%Y-%m-%dT%H:%M:00Z')}&_limit=1000"
    response = requests.get(url)
    data = response.json()
    # Create a dict of the data
    rainfall_dict = {}
    for i in data['items']:
        rainfall_dict[i['dateTime']] = i['value']
    return rainfall_dict


asyncio.run(update_rainfall_cache())
