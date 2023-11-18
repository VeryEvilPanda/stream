from stream import update_cache
import asyncio
import datetime

async def repeated_task(task, interval):
    while True:
        time_start = datetime.datetime.now()
        await task()
        time_end = datetime.datetime.now()
        print(f'{time_end.strftime("[%Y-%m-%d %H:%M:%S]")} Task scheduler: Task {task} completed. Next scheduled in {interval} seconds.')
        # Correct the interval by subtracting the time taken to complete the task
        corrected_interval = interval - (time_end - time_start).total_seconds()
        await asyncio.sleep(corrected_interval)


