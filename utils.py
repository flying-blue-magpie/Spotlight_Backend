from datetime import datetime

DATETIME_STR_FMT = '%Y/%m/%d %H:%M:%S'


def json_default_handler(obj):
    if isinstance(obj, datetime):
        return obj.strftime(DATETIME_STR_FMT)


def strftime_to_datetime(s):
    return datetime.strptime(s, DATETIME_STR_FMT)


class RecManager:
    def __init__(self, spot_rec_table):
        self._spot_rec_table = spot_rec_table
        self._rec_cache = dict()
        self._status = dict()

    def put(self, user_id, spot_ids, zones=None, keyword=None):
        self._rec_cache[user_id] = list(spot_ids)
        self._status[user_id] = {
            'zones': set(zones) if zones else None,
            'keyword': keyword,
        }

    def is_status_changed(self, user_id, zones=None, keyword=None):
        if user_id not in self._status:
            return True

        return (self._status[user_id]['zones'] != (set(zones) if zones else None)
                or self._status[user_id]['keyword'] != keyword)

    def is_cache_empty(self, user_id):
        if user_id not in self._status:
            return True

        return len(self._rec_cache[user_id]) == 0

    def pop(self, user_id, num):
        if self.is_cache_empty(user_id):
            return None

        result = []
        for _ in range(num):
            try:
                result.append(self._rec_cache[user_id].pop(0))
            except IndexError:
                break

        return result

    def update(self, user_id, like_spot_ids):
        if self.is_cache_empty(user_id):
            return
        if not like_spot_ids:
            return

        spot_ids = list(self._rec_cache[user_id])
        table = self._spot_rec_table

        ratings = []
        for i in spot_ids:
            ratings.append(
                sum(
                    [table.get((i, j), table.get((j, i), table['other'])) for j in like_spot_ids]
                )
            )

        _, spot_ids = zip(*(sorted(zip(ratings, spot_ids), reverse=True)))
        self._rec_cache[user_id] = list(spot_ids)
