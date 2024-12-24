# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import time


def read_long_list(fetcher, parameter, max_results: int = 100, **kwargs):
    """ Iterative requests with queries

    :param requestor: function that makes queries
    :param parameter:
    :return:
    """
    long_list = []
    cursor = None
    while True:
        try:
            response = fetcher(cursor=cursor)
        except Exception as e:
            raise Exception(f"Error in reading paginated list,  {e}")
        long_list.extend(response[parameter])
        if len(long_list) >= max_results:
            break
        cursor = response.get('cursor', None)
        if not cursor:
            break

    return long_list


def _read_rate_limits(response):
    rh = response.headers
    rlp, rlpw = rh['RateLimit-Policy'].split(';')
    rlpw = rlpw.split('=')[-1]
    rate_limits = {
        'RateLimit': int(rh['RateLimit-Limit']),
        'RateLimitRemaining': int(rh['RateLimit-Remaining']),
        'RateLimitReset':int(rh['RateLimit-Reset']),
        'RateLimitPolicy':int(rlp),
        'RateLimitPolicyW':int(rlpw)
    }
    return rate_limits


def sleep_if_less_than(rate_limit_reset: int, less_than=10):
    current_time = time.time()  # Gets current Unix timestamp
    sleep_duration = rate_limit_reset - current_time

    # Only sleep if the reset time is in the future
    if sleep_duration > 0:
        time.sleep(sleep_duration)
    else:
        print("Reset time has already passed")


if __name__ == '__main__':
    pass