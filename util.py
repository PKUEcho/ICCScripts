import os
import subprocess

def run_cmd(cmd):
    ret = subprocess.call(cmd, shell=True)
    print 'Executing cmd: ' + cmd
    if ret != 0:
        print 'Exec cmd error: ' + cmd

def getFileSize(package):
    return os.path.getsize('apps/' + package + '.apk')

def readTopList(num):
    ret = []
    top_file = open('top_info.txt')
    for line in top_file:
        if len(ret) >= num:
            break
        items = line.strip().split(' ')
        package = items[0]
        size = float(items[-1])
        real_size = getFileSize(package)
        if real_size < 1024 or (size / real_size) > 2:
            # print 'File size not matched! Real size: ' + str(real_size / 1024) + 'K size: ' + str(size / 1024) + 'K'
            # print 'Skip ' + package
            continue
        ret.append(package)
    return ret
