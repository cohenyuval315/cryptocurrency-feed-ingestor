import functools


def prep_api_request(request_size):
    def wrapper(coroutine):
        async def api_wrapped(args, *kwargs):
            print("prep_api    //  ", args, "   //   ", *kwargs)
            print(coroutine)
            con = await args.check_api_precondition(request_size)
            if not con:
                print("too much requests in this interval")
                return False
            res = await coroutine(args, kwargs)
            lst = list(args.api_limits.keys())
            args.api_limits[lst[0]] += request_size
            return res
        return api_wrapped
    return wrapper


def prep_order_request(coroutine):
    async def wrapped(args, *kwargs):
        print("prep_order    //  ", args,"   //   ", *kwargs)
        print(coroutine)
        con = await args.check_order_precondition()
        if not con:
            print("too much orders in this interval")
            return False
        #res = await coroutine(args, kwargs)
        for limit in args.order_limits.items():
            args.order_limits[limit] += 1
        #return res
        return coroutine(args, kwargs)
    return wrapped


if __name__ == '__main__':
    pass
