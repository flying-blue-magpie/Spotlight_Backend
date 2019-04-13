import json
from collections import defaultdict

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import turicreate as tc

from models import Spot
from models import RecRecord
from config import db


class RecManager:
    def _get_record_from_db(self, user_id):
        record = RecRecord.query.filter_by(user_id=user_id).first()
        return record

    def should_be_put(self, user_id, zones=None, keyword=None):
        record = self._get_record_from_db(user_id)
        if not record:
            return True

        record_dict = record.to_dict()
        if set(record_dict['last_query_zones'] if record_dict['last_query_zones'] else list()) \
                != set(zones if zones else list()):
            return True
        if record_dict['last_query_keyword'] != keyword:
            return True
        if len(record_dict['rec_list']) == 0:
            return True

        return False

    def should_be_updated(self, user_id, selected_favorite_ids):
        record = self._get_record_from_db(user_id)
        if not record:
            return True

        record_dict = record.to_dict()
        if record_dict['last_favorite_list'] != selected_favorite_ids:
            return True

        return False

    def put(self, user_id, spot_ids, selected_favorite_ids, zones=None, keyword=None):
        record = RecRecord.query.filter_by(user_id=user_id).first()
        if record:
            record.set_rec_list(spot_ids)
            record.set_last_favorite_list(selected_favorite_ids)
            record.set_last_query_zones(zones)
            record.last_query_keyword = keyword
            db.session.commit()
        else:
            record = RecRecord(user_id, spot_ids, selected_favorite_ids, zones, keyword)
            db.session.add(record)
            db.session.commit()

    def _create_rec_table(self, like_spot_ids):
        query = Spot.query.filter(Spot.id.in_(like_spot_ids)) \
                          .with_entities(Spot.id, Spot.rec_table)

        table = {}
        for i, json_str in query:
            if json_str is None:
                continue
            for j, r in json.loads(json_str):
                if j != 'other':
                    table[(i, j)] = r
                else:
                    table['other'] = r
        return table

    def update(self, user_id, like_spot_ids):
        if not like_spot_ids:
            return

        record = self._get_record_from_db(user_id)
        if not record:
            return

        record_dict = record.to_dict()
        spot_ids = list(record_dict['rec_list'])

        table = self._create_rec_table(like_spot_ids)

        ratings = []
        for i in spot_ids:
            ratings.append(
                sum(
                    [table.get((i, j), table.get((j, i), table['other'])) for j in like_spot_ids]
                )
            )

        _, spot_ids = zip(*(sorted(zip(ratings, spot_ids), reverse=True)))

        record.set_rec_list(list(spot_ids))
        record.set_last_favorite_list(like_spot_ids)
        db.session.commit()

    def pop(self, user_id, num):
        record = RecRecord.query.filter_by(user_id=user_id).first()
        if not record:
            return list()

        record_dict = record.to_dict()
        rec_list = record_dict['rec_list']

        if len(rec_list) > num:
            record.set_rec_list(rec_list[num:])
            db.session.commit()
            result = rec_list[:num]
            del rec_list
            return result
        else:
            record.set_rec_list(list())
            db.session.commit()
            return rec_list


def get_tfidf_bow(field):
    corpus = []
    map_spot_ids = {}
    for i, spot in enumerate(Spot.query.all()):
        corpus.append(' '.join(jieba.cut(getattr(spot, field), cut_all=False)))
        map_spot_ids[i] = spot.id

    stop_words = [line.strip() for line in open('./data/stop_words.txt', 'r').readlines()]

    vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf = vectorizer.fit_transform(corpus)

    return tfidf, map_spot_ids


def _get_equivalent_key(key):
    return (key[1], key[0])


def get_similar_dict_and_factors(tfidf, map_spot_ids, k=10):
    cx = tfidf.tocoo()
    sf = tc.SFrame({'spot_id': [map_spot_ids[i] for i in cx.row], 'word_id': cx.col, 'r': cx.data})
    model = tc.ranking_factorization_recommender.create(sf, 'word_id', 'spot_id', target='r')

    # similar dict
    df_similar_spots = model.get_similar_items(k=k).to_dataframe()
    dict_similar_spots = dict()
    for i, row in df_similar_spots.iterrows():
        key = (int(row.spot_id), int(row.similar))
        equivalent_key = _get_equivalent_key(key)
        if equivalent_key not in dict_similar_spots:
            dict_similar_spots[key] = row.score

    min_rating = min(dict_similar_spots.values())
    dict_similar_spots['other'] = min_rating

    # factors
    df = model.coefficients['spot_id'].to_dataframe()
    factors = {row.spot_id: row.factors.tolist() for _, row in df.iterrows()}

    return dict_similar_spots, factors


def get_weighted_similar_dict(name_dict, describe_dict, ratio):
    key_set = set(list(name_dict.keys()) + list(describe_dict.keys()))
    equivalent_key_set = set(_get_equivalent_key(key) for key in key_set)
    key_set = key_set - equivalent_key_set

    weighted_similar_dict = {}
    for key in key_set:
        name_rating = name_dict.get(
            key, name_dict.get(_get_equivalent_key(key), name_dict['other'])
        )
        describe_rating = describe_dict.get(
            key, describe_dict.get(_get_equivalent_key(key), describe_dict['other'])
        )
        weighted_similar_dict[key] = (name_rating * ratio + describe_rating) / (ratio + 1)

    min_rating = min(weighted_similar_dict.values())
    weighted_similar_dict['other'] = min_rating

    return weighted_similar_dict


def get_weighted_factors(name_factors, describe_factors, ratio, factor_dim=32):
    key_set = set(list(name_factors.keys()) + list(describe_factors.keys()))

    weighted_factors = {}
    for key in key_set:
        fns = name_factors.get(key, [0.0 for _ in range(factor_dim)])
        fds = describe_factors.get(key, [0.0 for _ in range(factor_dim)])
        weighted_factors[key] = [(fn * ratio + fd) / (ratio + 1) for fn, fd in zip(fns, fds)]

    return weighted_factors


def insert_rec_table_to_db(similar_spots_dict, factors):
    pairs = defaultdict(set)
    for key in similar_spots_dict.keys():
        if key == 'other':
            continue
        i, j = key
        pairs[i].add(j)
        pairs[j].add(i)

    for spot in Spot.query.order_by(Spot.id).all():
        i = spot.id
        try:
            rec_table = []
            for j in pairs[i]:
                rec_table.append([
                    j,
                    similar_spots_dict.get((i, j), similar_spots_dict.get((j, i))),
                ])
            rec_table.append(['other', similar_spots_dict['other']])
            spot.rec_table = json.dumps(rec_table)

            spot.rec_factors = json.dumps(factors[i])

            db.session.commit()
        except:
            print('error on row {}'.format(i))

        print('finish {}'.format(i))


def main():
    tfidf_name, map_spot_ids_name = get_tfidf_bow(field='name')
    similar_spots_name_dict, name_factors = get_similar_dict_and_factors(
        tfidf_name, map_spot_ids_name, k=10)

    tfidf_describe, map_spot_ids_describe = get_tfidf_bow(field='describe')
    similar_spots_describe_dict, describe_factors = get_similar_dict_and_factors(
        tfidf_describe, map_spot_ids_describe, k=50)

    similar_spots_dict = get_weighted_similar_dict(similar_spots_name_dict,
                                                   similar_spots_describe_dict,
                                                   ratio=5)

    factors = get_weighted_factors(name_factors, describe_factors, ratio=5)

    s = sorted(similar_spots_dict.items(), key=lambda t: t[1], reverse=True)
    print('Head 100 items: ', {k: r for k, r in s[:100]})
    print('Number of dict items: ', len(similar_spots_dict))

    insert_rec_table_to_db(similar_spots_dict, factors)


if __name__ == '__main__':
    main()
