from datetime import datetime
from client.util.time import  Interval


# only work for binance
def limit_num_api(request_size, is_order=False):
    def wrapper(coroutine):
        async def wrapped(self, **kwargs):
            # can get current num of requests for api at all time
            # orders can only get current requests number after an order
            info = self.client.response.headers
            cur_request_num = info['X-MBX-USED-WEIGHT-1M']
            if int(cur_request_num) + request_size > self.api_limits.limit:
                return False
            if is_order:
                # orders per sec limit
                ol1 = self.order_limits[0]

                interval = Interval(ol1.interval, ol1.interval_num)
                total_time = await interval.interval_to_sec()  # sec interval

                day_orders = self.limit_order_num[1]  # number of current sec orders
                order_limit_timeframe = (
                        datetime.now() - self.date_time_for_sec_limits).total_seconds()  # time passed since last order
                if order_limit_timeframe > total_time:  # if sec interval passed -> reset current num of sec orders , keep day orders,reset time delta
                    self.limit_order_num = (0, day_orders)
                    self.date_time_for_sec_limits = datetime.now()

                if self.limit_order_num[0] + request_size >= self.order_limits[0].limit:  # current sec orders > limit
                    return False
                # order per day limit
                # UTC 00:00:00 day reset
                ol2 = self.order_limits[1]

                interval = Interval(ol2.interval, ol2.interval_num)
                total_time = await interval.interval_to_sec()  # day interval in seconds

                order_limit_sec = self.limit_order_num[0]  # number of current day orders
                order_limit_timeframe = (
                        datetime.now() - self.date_time_for_day_limits).total_seconds()  # time passed since last order
                if order_limit_timeframe > total_time:  # if day interval passed -> reset current num of day orders, keep sec orders , reset time delta
                    self.limit_order_num = (order_limit_sec, 0)
                    self.date_time_for_day_limits = datetime.now()
                if self.limit_order_num[1] + request_size >= self.order_limits[1].limit:  # current day orders > limit
                    return False

            # passed preconditions
            res = await coroutine(self, **kwargs)
            if is_order:
                info = self.client.response.headers
                order_limit_sec = info["X-MBX-ORDER-COUNT-10s"]
                order_limit_day = info["X-MBX-ORDER-COUNT-1d"]
                self.limit_order_num = (int(order_limit_sec), int(order_limit_day))

            return res

        return wrapped

    return wrapper



if __name__ == '__main__':
    pass
