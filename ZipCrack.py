import time
from typing import List
from tqdm import tqdm
from itertools import chain
from zipfile import ZipFile
from concurrent.futures import ThreadPoolExecutor


class ZipCracker:
    filePath = ""
    maxLength = 10
    minLength = 1
    maxThread = 10
    dictionaries = None
    __isCracked = False
    __lengths = None
    pool = None

    def __init__(self, filePath, minLength=1, maxLength=10):
        self.filePath = filePath
        self.minLength = minLength
        self.maxLength = maxLength
        self.__lengths = range(minLength, maxLength + 1)
        # chr(97) -> 'a' 这个变量保存了密码包含的字符集
        self.dictionaries = [chr(i) for i in
                             chain(
                                 range(97, 123),  # a - z
                                 range(65, 91),  # A - Z
                                 range(48, 58))]  # 0 - 9
        self.pool = ThreadPoolExecutor(max_workers=self.maxThread)

    def __all_passwd(self, dictionaries: List[str], maxlen: int):
        # 返回由 dictionaries 中字符组成的所有长度为 maxlen 的字符串

        def helper(temp: list, start: int, n: int):
            # 辅助函数，是个生成器
            if start == n:  # 达到递归出口
                yield ''.join(temp)
                return
            for t in dictionaries:
                temp[start] = t  # 在每个位置
                yield from helper(temp, start + 1, n)

        yield from helper([0] * maxlen, 0, maxlen)

    def __extract(self, zfile: ZipFile, pwd: str) -> bool:
        # zfile: 一个ZipFile类, pwd: 密码
        try:
            zfile.extractall(path='.', pwd=pwd.encode('utf-8'))  # 密码输入错误的时候会报错
            print(f"Password is: {pwd}")  # 将正确的密码输出到控制台
            self.__isCracked = True
            return True
        except:
            return False

    def __crack(self, pwd: str):
        try:
            zfile = ZipFile(self.filePath, 'r')  # 很像open
            zfile.extractall(path='.', pwd=pwd.encode('utf-8'))  # 密码输入错误的时候会报错
            print(f"Password is: {pwd}")  # 将正确的密码输出到控制台
            self.__isCracked = True
            return True
        except:
            # print(f"Password is not : {pwd}")
            return False

    def start(self):
        start = time.time()
        total = sum(len(self.dictionaries) ** k for k in self.__lengths)  # 密码总数
        range = tqdm(chain.from_iterable(self.__all_passwd(self.dictionaries, maxlen) for maxlen in self.__lengths),total=total)
        for pwd in range:
            print(pwd)
            if self.__isCracked == False:  # 记得extract函数返回的是bool类型的哦
                self.pool.submit(self.__crack, pwd)
            else:
                now = time.time()
                print("timeCost:", now - start)
                break
