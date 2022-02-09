from typing import List
from tqdm import tqdm
from itertools import chain
from zipfile import ZipFile
import py7zr
from concurrent.futures import ThreadPoolExecutor
import time, _thread


class ZipCracker:
    filePath = ""
    maxLength = 10
    minLength = 1
    __dictionaries = None
    __isCracked = False
    __lengths = None
    __pool = None
    __zfile = None
    __pwd = None

    def __init__(self, filePath: str, minLength=1, maxLength=10):
        self.filePath = filePath
        self.minLength = minLength
        self.maxLength = maxLength
        self.__lengths = range(minLength, maxLength + 1)
        # chr(97) -> 'a' 这个变量保存了密码包含的字符集
        self.__dictionaries = [chr(i) for i in
                               chain(
                                   range(97, 123),  # a - z
                                   range(65, 91),  # A - Z
                                   range(48, 58))]  # 0 - 9
        self.__pool = ThreadPoolExecutor()
        if filePath.endswith(".zip"):
            self.__zfile = ZipFile(self.filePath, 'r')  # 很像open
        self.__dictionaries.extend(
            ['.', '#', '$', '&', '@', '!', '*', '(', ')', '%', '^', '_', '-', '+', '/', '?', '~', ';'])

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

    def __crack(self, pwd: str):
        try:
            self.__zfile.extractall(path='.', pwd=pwd.encode('utf-8'))  # 密码输入错误的时候会报错
            self.__pwd = pwd
            self.__isCracked = True
            ThreadPoolExecutor.shutdown(False)
            return True
        except:
            # print(f"Password is not: {pwd}")
            return False

    def __crack7z(self, pwd: str):
        try:
            self.__zfile = py7zr.SevenZipFile(self.filePath, 'r', password=pwd)
            self.__zfile.extractall(path=".")
            self.__pwd = pwd
            self.__isCracked = True
            ThreadPoolExecutor.shutdown(False)
            return True
        except:
            # print(f"Password is not: {pwd}")
            return False

    def __time(self):
        print("开始计时。。。")
        start = time.time()
        num = 0
        while (self.__isCracked == False):
            num += 1
            time.sleep(1)
            print("等了",num,"秒了",flush=True)
            pass
        now = time.time()
        print("timeCost:", now - start)
        if self.__pwd is None:
            print("crack failed")
        else:
            print("crack success,pwd is ", self.__pwd)

    def start(self):
        # _thread.start_new_thread(self.__time, ())
        total = sum(len(self.__dictionaries) ** k for k in self.__lengths)  # 密码总数
        fun = None
        if self.filePath.endswith(".7z"):
            fun = self.__crack7z
        elif self.filePath.endswith(".zip"):
            fun = self.__crack
        range = tqdm(chain.from_iterable(self.__all_passwd(self.__dictionaries, maxlen) for maxlen in self.__lengths),
                     total=total)
        num = 0
        for pwd in range:
            # print(pwd)
            if self.__isCracked == False:
                num += 1
                if (num >= 10000):
                    num = 0
                    # print("休息一秒钟")
                    time.sleep(1)
                self.__pool.submit(fun, pwd)
            else:
                break
