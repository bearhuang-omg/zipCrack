import ZipCrack

if __name__ == '__main__':
    file_name = "/Users/huangbei/Desktop/未命名文件夹/test.7z"
    zipCrack = ZipCrack.ZipCracker(file_name,4,20,15)
    zipCrack.start()
