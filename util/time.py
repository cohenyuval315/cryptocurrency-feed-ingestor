import asyncio
import time


def str_to_time(time_str):
    if time_str in "seconds":
        return 1
    if time_str in "minutes":
        return 60
    if time_str in "hours":
        return 60 * 60
    if time_str in "day":
        return 24 * 60 * 60
    if time_str in "week":
        return 24 * 60 * 60 * 7
    if time_str in "month":
        return 24 * 60 * 60 * 7 * 4
    return False


# todo check
def time_measure(coroutine):
    async def wrapped(args, *kwargs):
        start_time = time.time()
        try:
            asyncio.run(coroutine(args, *kwargs))
        except Exception as e:
            print(e)
            print("interrupt:")
            end_time_ex = time.time()
            run_time_ex = end_time_ex - start_time
            print(run_time_ex)
        finally:
            print("crash/end")
            end_time = time.time()
            run_time = end_time - start_time
            print(run_time)

    return wrapped
