import requests
from bs4 import BeautifulSoup
from pprint import pprint
import datetime
import aiofiles
import asyncio
import json


# Subroutine to update the cache of stream data
async def update_cache(all=False):
    time_now = datetime.datetime.now()
    day_ago = time_now - datetime.timedelta(days=1)
    week_ago = time_now - datetime.timedelta(weeks=1)
    if not all:
        async with aiofiles.open('data/flow_day.json', 'r') as f:
            contents = json.loads(await f.read())
        # Get a datetime object of the last reading in the cache
        last_reading = datetime.datetime.strptime(list(contents['data'].keys())[-1], '%Y-%m-%dT%H:%M:%SZ')
        # Get the stream since the last reading (as long as the last reading is within one day ago)
        new_data = get_stream_kingston(since = last_reading if last_reading > day_ago else day_ago, advanced = True)
        new_contents = {'data': {}}
        # Iterate through the current data and add any data from the last day to the new contents dict
        for i in contents['data']:
            if datetime.datetime.strptime(i, '%Y-%m-%dT%H:%M:%SZ') > day_ago:
                new_contents['data'][i] = contents['data'][i]
        # Iterate through the new data and add all of it to the new contents dict
        for i in new_data:
            new_contents['data'][i] = new_data[i]
        new_contents['updated'] = round(time_now.timestamp(), 0)
        async with aiofiles.open('data/flow_day.json', 'w') as f:
            await f.write(json.dumps(new_contents, indent=4))
        # -------------------------------
        # Do the same for the week cache
        # -------------------------------
        async with aiofiles.open('data/flow_week.json', 'r') as f:
            contents = json.loads(await f.read())
        # Get a datetime object of the last reading in the cache
        last_reading = datetime.datetime.strptime(list(contents['data'].keys())[-1], '%Y-%m-%dT%H:%M:%SZ')
        # Get the stream since the last reading (as long as the last reading is within one week ago)
        new_data = get_stream_kingston(since = last_reading if last_reading > week_ago else week_ago, advanced = True)
        new_contents = {'data': {}}
        # Iterate through the current data and add any data from the last week to the new contents dict
        for i in contents['data']:
            if datetime.datetime.strptime(i, '%Y-%m-%dT%H:%M:%SZ') > week_ago:
                new_contents['data'][i] = contents['data'][i]
        # Iterate through the new data and add all of it to the new contents dict
        for i in new_data:
            new_contents['data'][i] = new_data[i]
        new_contents['updated'] = round(time_now.timestamp(), 0)
        async with aiofiles.open('data/flow_week.json', 'w') as f:
            await f.write(json.dumps(new_contents, indent=4))
    # If requested, update the entire cache
    else:
        full_data = get_stream_kingston(since = day_ago, advanced = True)
        async with aiofiles.open('data/flow_day.json', 'w') as f:
            await f.write(json.dumps({'data': full_data, 'updated': round(time_now.timestamp(), 0)}, indent=4))
        full_data = get_stream_kingston(since = week_ago, advanced = True)
        async with aiofiles.open('data/flow_week.json', 'w') as f:
            await f.write(json.dumps({'data': full_data, 'updated': round(time_now.timestamp(), 0)}, indent=4))


# Function to scrape the river conditions page and return a dictionary of locks and their status
def get_boards():
    url = 'https://www.gov.uk/guidance/river-thames-current-river-conditions'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all table rows in the page (luckily for us, there is only one table)
    locks = soup.find_all('tr')
    locks_dict = {}
    # Each table row corresponds to a lock (or a heading)
    for lock in locks:
        lock_list = []
        for i in lock.contents:
            # Ensure that the item is not a newline and is a data element, not a heading
            if i != '\n' and i.name == 'td':
                lock_list.append(i.string)
        # Ensure that the list is not empty, which it would be if the row was a heading
        if lock_list:
            locks_dict[lock_list[0]] = lock_list[1]
    
    return locks_dict


# Function to get stream flow speed data from the cached file
async def get_stream(timeframe):
    time_now = datetime.datetime.now()
    # Get the day timeframe cache
    if timeframe == 'day':
        async with aiofiles.open('data/flow_day.json', 'r') as f:
            contents = json.loads(await f.read())
        return contents['data']
    # Get the week timeframe cache
    elif timeframe == 'week':
        async with aiofiles.open('data/flow_week.json', 'r') as f:
            contents = json.loads(await f.read())
        return contents['data']
    elif timeframe == 'both':
        async with aiofiles.open('data/flow_day.json', 'r') as f:
            day_contents = json.loads(await f.read())
        async with aiofiles.open('data/flow_week.json', 'r') as f:
            week_contents = json.loads(await f.read())
        return day_contents['data'], week_contents['data']
    else:
        return 'invalid timeframe'

async def after_return():
      pass



# Low level function to get the stream flow speed data. May modify to allow other stations in the future.
def get_stream_kingston(since = 'today', until = None, advanced = False):
    # Create the url basaed on the parameters
    if advanced:
        url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/3400TH/readings?since={since.strftime('%Y-%m-%dT%H:%M:00Z')}&_limit=1000&parameter=flow"
    elif since == 'today':
        url = 'https://environment.data.gov.uk/flood-monitoring/data/readings?stationReference=3400TH&today&parameter=flow'
    elif until:
        try:
            url = f"https://environment.data.gov.uk/flood-monitoring/data/readings?stationReference=3400TH&startdate={since.strftime('%Y-%m-%d')}&enddate={until.strftime('%Y-%m-%d')}&parameter=flow"
        except:
            return 'Invalid date format, use datetime'
    else:
        try:
            url = f"https://environment.data.gov.uk/flood-monitoring/data/readings?stationReference=3400TH&since={since.strftime('%Y-%m-%d')}&parameter=flow"
        except:
            return 'Invalid date format, use datetime'
    response = requests.get(url)
    data = response.json()
    # Create a dict of the data
    stream_dict = {}
    for i in data['items']:
        # in the form date: flow speed (cumecs)
        stream_dict[i['dateTime']] = i['value']

    return stream_dict


# Function to setup the boards variables used in the template
def template_data_boards(boards):
    red_locks = 0
    for lock in boards:
        # Count the number of red locks
        if 'red' in boards[lock].lower():
            red_locks += 1
        # Find the local lock
        if lock == 'Molesey Lock to Teddington Lock':
            board = boards[lock]
            # Set the text colour of the board
            if 'red' in board.lower():
                board_colour = 'color:red'
            elif 'yellow' in board.lower():
                board_colour = 'color:Gold'
            else:
                board_colour = 'color:green'
    # Get the percentage of locks that are red using number of red locks
    percentage_red = round((red_locks / len(boards) * 100), 1)
    # Set the text colour of the percentage
    if percentage_red > 70:
        percentage_colour = 'color:red'
    elif percentage_red > 30:
        percentage_colour = 'color:Gold'
    else:
        percentage_colour = 'color:green'
    
    return board, percentage_red, board_colour, percentage_colour
    
# Function to setup the stream variables used in the template
def template_data_stream(stream):
    total_flow = 0
    graph_data = []
    for time in stream:
        total_flow += stream[time]
        # Reformat the datetime into a list of integers. Take 1 from the month because it is 0 indexed in a JS date object
        graph_data.append([[int(time[0:4]), int(time[5:7])-1, int(time[8:10]), int(time[11:13]), int(time[14:16])], round(stream[time], 1)])
    # Get the average flow speed
    average_flow = round(total_flow / len(stream), 1)
    # Get the trend of the flow speed
    values = list(stream.values())
    trend = round(values[-1] - values[0], 1)
    if trend > 10:
        trend_colour = 'color:red'
        trend_direction = 'increasing'
    elif trend < -10:
        trend_colour = 'color:green'
        trend_direction = 'decreasing'
    else:
        trend_colour = 'color:Gold'
        trend_direction = 'staying around the same'
    if trend > 0:
        trend = f"+{trend}"
    # Get the latest flow speed
    latest_stream = [round(list(stream.values())[-1], 1), list(stream.keys())[-1][11:16]]
    # Currently saving all trends in order to figure out what is a high trend and what is low, etc.
    with open('trends.txt', 'a') as f:
        f.write(f"{trend}\n")
    return graph_data, average_flow, str(trend), trend_colour, trend_direction, latest_stream


# the function below was a bit pointless, the only useful bit was the change between first and last value which is easy to work out

# # Function to calculate a trend in data (basically the difference between each value)
# def get_trend(data):
#     change_list = []
#     total_change = 0
#     # Start at index 1 because we are comparing the current value to the previous value
#     for i in range(1, len(data)):
#         change = data[i] - data[i - 1]
#         change_list.append(change)
#         total_change += change
#     # Return both the total change from start to end, and a list of changes between each value
#     return total_change, change_list



# pprint(get_boards(), sort_dicts=False)

# boards = get_boards()
# for lock in boards:
#     print(lock)

#pprint(get_stream_kingston(datetime.datetime(2023,11,9,8,30), advanced=True), sort_dicts=False)

# data = [12, 34, 29, 38, 34, 51, 29, 34, 47, 34, 55, 94, 68, 81]
# print(get_trend(data))


#print(asyncio.run(get_stream('week')))

asyncio.run(update_cache(all=True))