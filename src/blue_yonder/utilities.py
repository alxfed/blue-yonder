# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""


def read_long_list(fetcher, parameter):
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
        cursor = response.get('cursor', None)
        if not cursor:
            break

    return long_list


if __name__ == '__main__':
    def req(cursor=None):
        response = requests.get(
            url=self.records_url,
            params={
                'repo': actor if actor else self.did,
                'collection': collection,
                'limit': 50,
                'cursor': cursor}
        )
        response.raise_for_status()
        res = response.json()
        records.extend(res['records'])