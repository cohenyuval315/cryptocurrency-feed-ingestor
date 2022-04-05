import asyncio
import atexit
import json
import pandas as pd
import os.path
import time
import datetime
import pathlib
import aiofiles

from client.backend.kafka_impl import KafkaFeedConsumer

# TODO Change to enum file type
class FileHandler:
    TEXT = "txt"
    CSV = "csv"
    DOT = "."

    root = os.path.abspath(__file__).replace(os.path.basename(__file__), "") + r"files\data\\"

    def __init__(self, file_type: str = "txt"):
        self.file_type = file_type


class RestFileHandler(FileHandler):

    def __init__(self, file_type: str = "txt"):
        super().__init__(file_type)

    def write_to_file(self, directory, filename, msg, increment=False):
        d = datetime.datetime.now()
        root = self.root + rf'\{directory}\\'
        is_exist = os.path.exists(root)
        if not is_exist:
            os.makedirs(root)

        if increment:
            i = 1
            while os.path.exists(root + filename + str(i)):
                i += 1
            root_file = pathlib.Path(root, filename + str(i))
        else:
            root_file = pathlib.Path(root, filename)

        try:
            with get_file(root_file) as file:
                file.write(msg)
                file.flush()
                os.fsync(file.fileno())
                print("file done")
                file.close()
        except Exception as e:
            print(e)

    def read_from_file(self, directory, filename):
        root = self.root + rf'\{directory}\\'
        is_exist = os.path.exists(root + filename)
        if not is_exist:
            return False
        root_file = pathlib.Path(root, filename)
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
            is_exist = os.path.exists(root + filename + str(i))
            while is_exist:
                is_exist = os.path.exists(root + filename + str(i))
                d = self.read_from_file(directory, filename + str(i))
                if not d:
                    break
                data.append(d)
                i += 1
            return data
        files = os.listdir(self.root + rf'\{directory}')
        for file in files:
            data.append(self.read_from_file(directory, file))
        return data


class KafkaFileConsumer(FileHandler):

    def __init__(self, file_type: str, real_time_write=False):
        super().__init__(file_type)
        self.real_time_write = real_time_write
        self.consumer = KafkaFeedConsumer()

    async def start(self, topics: list = None):
        if topics:
            await self.consumer.subscribe_topics(topics)
        else:
            await self.consumer.subscribe_all()
        await self.consumer.read(self.consume_to_file)

    def process_msg(self, msg):
        res_type = msg['data']['e']
        data = msg['data']
        msg.pop('data')
        if res_type == "kline":
            k = data['k']
            data.pop('k')
            msg.update(k)
        msg.update(data)
        print(msg)
        if self.file_type == self.TEXT:
            m = json.dumps(msg)
            m += "\n"
            return m
        if self.file_type == self.CSV:
            df = pd.read_json(msg)
            df.to_string()
        return msg

    def consume_to_file(self, msg):
        res_type = msg['data']['e']
        filename = msg["topic"] + self.DOT + self.file_type
        d = datetime.datetime.now()
        msg = self.process_msg(msg)
        r = os.path.abspath(__file__)
        f = os.path.basename(__file__)
        root = r.replace(f, "")
        root += r"files\data\\"
        root += rf'\{res_type}\{str(d.year)}\{str(d.month)}\{str(d.day)}\{str(d.hour)}\{str(d.minute)}\\'
        root_file = pathlib.Path(root, filename)
        is_exist = os.path.exists(root)
        if not is_exist:
            os.makedirs(root)

        try:
            with get_file(root_file, 1) as file:
                file.write(msg)
                if self.real_time_write:
                    file.flush()
                    os.fsync(file.fileno())
                    file.close()
                    print("file done")
                else:
                    file.close()
        except Exception as e:
            print(e)


def fix_ownership(path):
    """Change the owner of the file to SUDO_UID"""
    uid = os.environ.get('SUDO_UID')
    gid = os.environ.get('SUDO_GID')
    if uid is not None:
        os.chown(path, int(uid), int(gid))


def get_file(path, buffer=None, mode="a+"):
    """Create a file if it does not exists, fix ownership and return it open"""
    open(path, 'a').close()
    fix_ownership(path)
    if buffer:
        return open(path, mode, buffering=buffer)
    return open(path, mode)


if __name__ == '__main__':
    t = os.listdir(RestFileHandler.root + rf'\name\2022-04-01')
    print(t)
