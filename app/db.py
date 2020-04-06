"""
Требования к нереляционным БД
2 - нереляционная БД
2 - красивая структура БД
2 - интерфейс позволяет класть, доставать, удалять данные (проводить операции CRUD - Create, Read, Update, Delete)
2 - два действия помимо CRUD (сортировка, группировка, агрегация, ...)
2 - зависит от БД:
    Redis - использование ключей, хешей, ...;
    Neo4j - нахождение путей не только к соседним вершинам, операции с графами;
    MongoDB, ElasticSearch - работа с текстами или географией;
    остальные БД - будем договариваться.
"""

import random
import typing as tp

import redis

random.seed(42)


class RedisDatabase:
    prefix = 'man:'

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, decode_responses=True) -> None:
        self.r = redis.StrictRedis(
            host=host, port=port, db=db, password=password, socket_timeout=socket_timeout,
            decode_responses=decode_responses)

    #################### CREATE
    def create_men(self, men: tp.List[tp.Dict[str, tp.Any]]):
        with self.r.pipeline() as pipe:
            for man in men:
                hash_ = hash(frozenset(man.items()))
                if not self.r.exists(f'{self.prefix}{hash_}'):
                    pipe.hmset(f'man:{hash_}', man)
            pipe.execute()

    #################### READ
    def read_ids(self):
        return list(self.r.scan_iter(f'{self.prefix}*'))

    def read_all_men(self):
        prefix_len = len(self.prefix)
        ids = [id_[prefix_len:] for id_ in self.read_ids()]
        return self.read_men(ids)

    def read_men(self, ids: tp.List[int]):
        return [dict(self.r.hgetall(f'{self.prefix}{id_}'), **{'id': id_}) for id_ in ids]

    def read_man_fields(self, id_: int, fields: tp.List[str]):
        return self.r.hmget(f'{self.prefix}{id_}', *fields)

    def read_keys(self):
        return self.r.keys()

    def add_connection(self, str_first_id: str, str_second_id: str):
        if not self.r.hexists(str_first_id, str_second_id):
            id_ = int(str_first_id[len(self.prefix):])
            self.update_man_fields(id_, [str_second_id], ['true'])
        if not self.r.hexists(str_second_id, str_first_id):
            id_ = int(str_second_id[len(self.prefix):])
            self.update_man_fields(id_, [str_first_id], ['true'])

    #################### UPDATE
    def update_men(self, ids: tp.List[int], men: tp.List[tp.Dict[str, tp.Any]]):
        with self.r.pipeline() as pipe:
            for id_, man in zip(ids, men):
                pipe.hmset(f'{self.prefix}{id_}', man)
            pipe.execute()

    def update_man_fields(self, id_: int, fields: tp.List[str], values: tp.List[tp.Any]):
        with self.r.pipeline() as pipe:
            for field, value in zip(fields, values):
                pipe.hset(f'{self.prefix}{id_}', field, value)
            pipe.execute()

    #################### DELETE
    def delete_men(self, ids: tp.List[int]):
        self.r.delete(*[f'{self.prefix}{id_}' for id_ in ids])

    def delete_man_fields(self, id_: int, fields: tp.List[str]):
        self.r.hdel(f'{self.prefix}{id_}', *fields)

    @staticmethod
    def string_to_score(string, ignore_case=False):
        if ignore_case:
            string = string.lower()
        pieces = list(map(ord, string[:6]))
        while len(pieces) < 6:
            pieces.append(-1)
        score = 0
        for piece in pieces:
            score = score * 257 + piece + 1
        return score * 2 + (len(string) > 6)

    #################### SORT
    def sort_men(self, fields: tp.List[str]):
        """
        (c) https://stackoverflow.com/a/10547734/8990391
        """
        sorted_set = 'men'
        for man in self.read_all_men():
            # NB: uncomment?
            score = self.string_to_score(man[fields[0]])
            # score = sum(len(man[field]) for field in fields)
            self.r.zadd(sorted_set, {man['id']: score})

        result_set = self.r.zrange(sorted_set, 0, -1)
        return self.read_men([int(elem) for elem in result_set])

    #################### GROUP
    def group_men(self):
        self.add_connection(*self.read_ids())
        keys = self.read_ids()
        dct = {}
        for key in keys:
            lst = []
            for inner_key in keys:
                if self.r.hexists(key, inner_key):
                    lst.append(inner_key)
            dct[key] = lst
        print(dct)
        return dct

    #################### FILTER
    def filter_men(self, field: str, value: str):
        if not value:
            return []
        men = self.read_all_men()
        results = [man for man in men if value in man[field].lower()]
        if results:
            return results[0]
        return []


if __name__ == '__main__':
    pass
