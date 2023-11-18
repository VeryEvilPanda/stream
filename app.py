from quart import Quart, render_template, websocket, abort, request, redirect
from stream import get_boards, template_data_boards, template_data_stream, get_stream_kingston, update_cache, get_stream
import datetime
import asyncio
from tasks import repeated_task
from rainfall import get_rainfall, update_rainfall_cache

app = Quart(__name__)

# normal route (currently)
@app.route('/')
async def index():
    boards = get_boards()
    now = datetime.datetime.now()
    # Get the list of stream data
    stream = get_stream_kingston(since = now - datetime.timedelta(days=1), advanced = True)
    # Get the board and stream data formatted into variables
    boards_data = template_data_boards(boards)
    stream_data = template_data_stream(stream)
    # Return the template with the stream data
    return await render_template(
        'index.html', 
        board=boards_data[0], 
        percentage_red=boards_data[1], 
        board_colour=boards_data[2], 
        percentage_colour = boards_data[3],
        graph_data = stream_data[0],
        average_flow = stream_data[1],
        trend = stream_data[2],
        trend_colour = stream_data[3],
        trend_direction = stream_data[4],
        latest_stream = stream_data[5]
        )



@app.route('/new/<timeframe>')
async def new(timeframe):
    boards = get_boards()
    stream = await get_stream(timeframe)
    boards_data = template_data_boards(boards)
    stream_data = template_data_stream(stream)
    return await render_template(
        'index.html', 
        board=boards_data[0], 
        percentage_red=boards_data[1], 
        board_colour=boards_data[2], 
        percentage_colour = boards_data[3],
        graph_data = stream_data[0],
        average_flow = stream_data[1],
        trend = stream_data[2],
        trend_colour = stream_data[3],
        trend_direction = stream_data[4],
        latest_stream = stream_data[5]
        )

# route for static website, to be used in future
@app.route('/api/stream')
async def stream_api():
    boards = get_boards()
    stream = await get_stream('both')
    

# route for static website, to be used in future
@app.route('/api/stream/<timeframe>')
async def stream_timeframe_api(timeframe):
    boards = get_boards()
    stream = await get_stream(timeframe)
    # Format the data into variables for the website
    boards_data = template_data_boards(boards)
    stream_data = template_data_stream(stream)
    return {
        "board": boards_data[0], 
        "percentage_red": boards_data[1], 
        "board_colour": boards_data[2], 
        "percentage_colour": boards_data[3],
        "graph_data": stream_data[0],
        "average_flow": stream_data[1],
        "trend": stream_data[2],
        "trend_colour": stream_data[3],
        "trend_direction": stream_data[4],
        "latest_stream": stream_data[5]
    }

# route for static website, to be used in future
@app.route('/api/rainfall')
async def rainfall_api():
    return await get_rainfall()



@app.before_serving
async def start():
    app.update_task = asyncio.create_task(repeated_task(update_cache, 900))
    app.rainfall_task = asyncio.create_task(repeated_task(update_rainfall_cache, 900))


if __name__ == '__main__':
    app.run(port=8080, use_reloader=False)
