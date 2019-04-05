import pickle

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import turicreate as tc

from models import Spot
import config


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

def get_similar_dict(tfidf, map_spot_ids, k=10):
    cx = tfidf.tocoo()
    sf = tc.SFrame({'user_id': [map_spot_ids[i] for i in cx.row], 'word_id': cx.col, 'r': cx.data})
    model = tc.recommender.create(sf, 'word_id', 'user_id', target='r')
    df_similar_spots = model.get_similar_items(k=k).to_dataframe()
    dict_similar_spots = dict()
    for i, row in df_similar_spots.iterrows():
        key = (int(row.user_id), int(row.similar))
        equivalent_key = _get_equivalent_key(key)
        if equivalent_key not in dict_similar_spots:
            dict_similar_spots[key] = row.score

    min_rating = min(dict_similar_spots.values())
    dict_similar_spots['other'] = min_rating

    return dict_similar_spots


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


def main():
    tfidf_name, map_spot_ids_name = get_tfidf_bow(field='name')
    similar_spots_name_dict = get_similar_dict(tfidf_name, map_spot_ids_name, k=10)
    tfidf_describe, map_spot_ids_describe = get_tfidf_bow(field='describe')
    similar_spots_describe_dict = get_similar_dict(tfidf_describe, map_spot_ids_describe, k=30)
    similar_spots_dict = get_weighted_similar_dict(similar_spots_name_dict,
                                                   similar_spots_describe_dict,
                                                   ratio=5)

    s = sorted(similar_spots_dict.items(), key=lambda t: t[1], reverse=True)
    print('Head 100 items: ', {k: r for k, r in s[:100]})
    print('Number of dict items: ', len(similar_spots_dict))

    with open(config.REC_TABLE_PATH, 'wb') as fw:
        pickle.dump(similar_spots_dict, fw)


if __name__ == '__main__':
    main()
