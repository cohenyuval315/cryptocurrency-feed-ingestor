import dataclasses
import enum
import json
from timeit import timeit

import pandas as pd
import os.path
import datetime
import pathlib

from client.backend.kafka_impl import KafkaFeedConsumer


class RestFileHandler:

    def __init__(self, file_type: str):
        super().__init__(file_type)

    def write_to_file(self, directory, filename, msg, increment=False, truncate=False):
        d = datetime.datetime.now()
        root = self.root + rf'\{directory}\\'
        is_exist = os.path.exists(root)
        if not is_exist:
            os.makedirs(root)

        if increment:
            i = 1
            while os.path.exists(root + filename + str(i) + self.DOT + self.file_type):
                i += 1
            root_file = pathlib.Path(root, filename + str(i) + self.DOT + self.file_type)
        else:
            root_file = pathlib.Path(root, filename + self.DOT + self.file_type)

        m = "a+"
        if truncate:
            m = "w"
        try:
            with get_file(root_file, mode=m) as file:
                file.write(msg)
                file.flush()
                os.fsync(file.fileno())
                print("file done")
                file.close()
        except Exception as e:
            print(e)

    def read_from_file(self, directory, filename):
        root = self.root + rf'\{directory}\\'
        is_exist = os.path.exists(root + filename + self.DOT + self.file_type)
        if not is_exist:
            return False
        root_file = pathlib.Path(root, filename + self.DOT + self.file_type)
        try:
            with get_file(root_file, mode="r") as f:
                all_data = f.read()
                f.flush()
                f.close()
                return all_data
        except Exception as e:
            print(e)

    def read_dir(self, directory, filename=None, increment=False):
        root = self.root + rf'\{directory}\\'
        data = []
        if increment:
            if not filename:
                raise Exception("if incremental need filename")
            i = 1
            is_exist = os.path.exists(root + filename + str(i) + self.DOT + self.file_type)
            while is_exist:
                d = self.read_from_file(directory, filename + str(i) + self.DOT + self.file_type)
                data.append(d)
                i += 1
                is_exist = os.path.exists(root + filename + str(i) + self.DOT + self.file_type)
            return data

        files = os.listdir(self.root + rf'\{directory}')
        for file in files:
            data.append(self.read_from_file(directory, file))
        return data


class FileHandler:
    DOT = "."
    data_dir = r"files\data\\"
    root = os.path.abspath(__file__).replace(os.path.basename(__file__), "") + data_dir
    cache = {}

    def __init__(self, filename, path=None, partition=False, partition_mg_size=None, real_time_write=False, index=True,
                 columns_names: list[str] = None):
        self.path = path
        self.filename = filename
        self.partition = partition
        self.partition_mg_size = partition_mg_size
        if not partition_mg_size:
            self.partition_mg_size = 100
        self.full_path = pathlib.Path(FileHandler.root, filename)
        if path:
            self.full_path = pathlib.Path(path, filename)
        self.real_time_write = real_time_write
        self.df = pd.DataFrame(columns=columns_names)
        FileHandler.cache['filename'] = self

    def write_parquet(self, msg):
        # with open('my_csv.csv', 'a') as f:
        #     df.to_csv(f, header=False)
        if self.real_time_write:
            pd.DataFrame.from_dict(msg)
            self.df.to_parquet(self.full_path, mode="a+", index=False, header=False)

    def _real_time(self):
        pass

    def write_hdf5(self, msg):
        pass

    def read_parquet(self):
        file = pd.read_parquet(self.filename)
        # root += rf'\{res_type}\{str(d.year)}\{str(d.month)}\{str(d.day)}\{str(d.hour)}\{str(d.minute)}\\'
        # root_file = pathlib.Path(root, filename)
        # is_exist = os.path.exists(root)
        # if not is_exist:
        #     os.makedirs(root)
        #
        # try:
        #     with get_file(root_file, 1) as file:
        #         file.write(msg)
        #         if self.real_time_write:
        #             file.flush()
        #             os.fsync(file.fileno())
        #             file.close()
        #             print("file done")
        #         else:
        #             file.close()
        # except Exception as e:
        #     print(e)


def fix_ownership(path):
    uid = os.environ.get('SUDO_UID')
    gid = os.environ.get('SUDO_GID')
    if uid is not None:
        os.chown(path, int(uid), int(gid))


def get_file(path, buffer=None, mode="a+"):
    open(path, 'a').close()
    fix_ownership(path)
    if buffer:
        return open(path, mode, buffering=buffer)
    return open(path, mode)


if __name__ == '__main__':
    t = os.fspath("test_f.csv")
    print(t)
    # ddf.repartition(partition_size="100MB").to_csv("data/csvs")
    # ddf = dd.read_csv("data/csvs/*.part", dtype=better_dtypes)
    # ddf.groupby("id1", dropna=False, observed=True).agg({"v1": "sum"}).compute()
    # df = pd.DataFrame.to_parquet()
    # ddf = dd.read_parquet("data/snappy-parquet", engine="pyarrow", columns=["id1", "v1"])
    # ddf.groupby("id1", dropna=False, observed=True).agg({"v1": "sum"}).compute()
    pass
    # msg = {'stream':
    #            'bnbusdt@kline_1m'
    #     , 'data':
    #            {'e': 'kline', 'E': 1646785974521, 's': 'BNBUSDT',
    #             'k': {'t': 1646785920000, 'T': 1646785979999, 's': 'BNBUSDT', 'i': '1m', 'f': 525829897, 'L': 525830066,
    #                   'o': '382.80000000', 'c': '382.70000000', 'h': '382.80000000', 'l': '382.50000000',
    #                   'v': '495.80000000',
    #                   'n': 170, 'x': False, 'q': '189717.45910000', 'V': '59.65700000', 'Q': '22830.68060000',
    #                   'B': '0'}}}
    # res_type = msg['data']['e']
    # data = msg['data']
    # msg.pop('data')
    # if res_type == "kline":
    #     k = data['k']
    #     data.pop('k')
    #     msg.update(data)
    #     msg.update(k)
    # m = msg
    # m = {key: [value] for key, value in m.items() if not isinstance(value, (list, dict))}
    # df = pd.DataFrame.from_dict(m)
    # root = FileHandler.root + rf'\test_dir\test_f.csv'
    # df.to_csv(root, mode="a+", encoding='utf-8')
    # df2 = pd.DataFrame.from_dict(m)
    # df2.to_csv(root, mode="a+", encoding='utf-8',header=False)
    #
    # t = RestFileHandler(file_type=FileType.CSV)
