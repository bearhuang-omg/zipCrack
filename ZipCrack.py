from typing import List
from itertools import chain
import py7zr
import time, _thread


class ZipCracker:
    filePath = ""
    maxLength = 10
    minLength = 1
    __dictionaries = None
    __isCracked = False
    __lengths = None
    __zfile = None
    __pwd = None
    __iter = None
    __total = None
    __current = 0
    __lock = None
    __threads = 5

    def __init__(self, filePath: str, minLength=1, maxLength=10,threads = 5):
        self.filePath = filePath
        self.minLength = minLength
        self.maxLength = maxLength
        self.__lengths = range(minLength, maxLength + 1)
        # chr(97) -> 'a' 这个变量保存了密码包含的字符集
        self.__dictionaries = [chr(i) for i in
                               chain(
                                   range(97, 123),  # a - z
                                   range(65, 91),  # A - Z
                                   range(48, 58)
                               )
                               ]  # 0 - 9
        # if filePath.endswith(".zip"):
        #     self.__zfile = ZipFile(self.filePath, 'r')  # 很像open
        self.__dictionaries.extend(
            ['.', '#', '$', '&', '@', '!', '*', '(', ')', '%', '^', '_', '-', '+', '/', '?', '~', ';'])
        self.__lock = _thread.allocate_lock()

        self.__total = sum(len(self.__dictionaries) ** k for k in self.__lengths)  # 密码总数
        self.__iter = chain.from_iterable(self.__all_passwd(self.__dictionaries, maxlen) for maxlen in self.__lengths)
        self.__threads = threads

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

    def __crack7z(self, pwd: str):
        try:
            self.__zfile = py7zr.SevenZipFile(self.filePath, 'r', password=pwd)
            self.__zfile.password_protected
            self.__zfile.extractall(path=".")
            self.__pwd = pwd
            self.__isCracked = True
            return True
        except:
            # print('\r', "pwd is wrong：{:s}".format(pwd), end='', flush=True)
            return False

    def __crack(self):
        while (True):
            list = self.__getPass()
            findPwd = False
            for pwd in list:
                if (self.__crack7z(pwd)):
                    findPwd = True
                    print(f"Password is: {pwd}")
                    break
            if (findPwd):
                break

    def __time(self):
        print("开始计时。。。")
        start = time.time()
        num = 0
        while (self.__isCracked == False):
            num += 1
            time.sleep(1)
            percent = self.__current * 100 / self.__total
            print('\r', "Total:{:d}, current:{:d}, 完成度：{:f}%,耗时:{:d}秒".format(self.__total, self.__current, percent,num), end='',
                  flush=True)
        now = time.time()
        print("timeCost:", now - start)
        if self.__pwd is None:
            print("crack failed")
        else:
            print("crack success,pwd is ", self.__pwd)

    def __getPass(self):
        list = []
        try:
            self.__lock.acquire(timeout=2)
            num = 0
            for i in self.__iter:
                num += 1
                if (num > 20):
                    break
                list.append(i)
            self.__current += list.__len__()
        finally:
            self.__lock.release()
        return list

    def start(self):
        _thread.start_new_thread(self.__time, ())
        for i in range(0, self.__threads+1):
            _thread.start_new_thread(self.__crack, ())

        while (True):
            if (self.__isCracked):
                print("main 结束")
                break
