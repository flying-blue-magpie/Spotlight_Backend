import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

from models import Spot


def get_tfidf_bow():
    corpus = []
    for spot in Spot.query.all():
        corpus.append(' '.join(jieba.cut(spot.name, cut_all=False)))

    stop_words = [line.strip() for line in open('./data/stop_words.txt', 'r').readlines()]

    vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf = vectorizer.fit_transform(corpus)

    return vectorizer, tfidf


def main():
    vectorizer, tfidf = get_tfidf_bow()


if __name__ == '__main__':
    main()
