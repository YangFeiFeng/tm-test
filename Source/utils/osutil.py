import os
import stat
import shutil


def remove_file_or_folder(path):
    if not path:
        return

    def clear_readonly(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if os.path.exists(path):
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path, onerror=clear_readonly)


def copyfolder(src, dst):
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.makedirs(dst)

    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            copyfolder(srcname, dstname)

        else:
            if os.path.isfile(dstname):
                os.remove(dstname)
            elif os.path.isdir(dstname):
                shutil.rmtree(dstname)
            shutil.copy2(srcname, dstname)
