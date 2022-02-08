import ZipCrack

if __name__ == '__main__':
    print("hello world!")
    file_name = "/Users/huangbei/Desktop/未命名文件夹/test.zip"
    zipCrack = ZipCrack.ZipCracker(file_name,4,4)
    zipCrack.start()