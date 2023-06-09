# from configobj import ConfigObj
import os
import stat
import argparse
import configparser
import sys


class MyConfigParser(configparser.ConfigParser):
    """
    set ConfigParser options for case sensitive.
    """

    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


def main():
    # 解析参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', type=str,
                        help="start up cmd --cmd='xxxxx'", required=True)
    parser.add_argument('--Del', action="store_true",
                        help="Whether the cmd type is Del")
    args = parser.parse_args()
    if args.cmd[-1] != '&':
        args.cmd += ' &'
    # rc-local.service

    #servicePath = "/home/zeyu/src/PythonProject/lib/rc-local.sevice"
    servicePath = "/lib/systemd/system/rc-local.service"

    #serviceLink = "/home/zeyu/src/PythonProject/etc/rc-local.sevice"
    serviceLink = "/etc/systemd/system/rc-local.service"

    # rc.local 文件路径
    #rcLocalPath = "/home/zeyu/src/PythonProject/etc/rc.local"
    rcLocalPath = "/etc/rc.local"

    # 1、修改 rc-local.service 文件的权限
    os.chmod(servicePath, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)

    # 2、添加关键字段
    conf = MyConfigParser()

    conf.read(servicePath, encoding="utf-8")

    if not conf.has_section("Install"):
        conf.add_section("Install")

    if not conf.has_option("Install", "WantedBy"):
        conf.set("Install", "WantedBy", "multi-user.target")
    else:
        msg = conf.get("Install", "WantedBy")
        print(msg)
        print(msg == "multi-user.target")
        if not msg == "multi-user.target":
            conf.set('Install', "WantedBy", "multi-user.target")

    if not conf.has_option("Install", "Alias"):
        conf.set("Install", "Alias", "multi-user.target")
    else:
        msg = conf.get("Install", "Alias")
        print(msg)
        print(msg == "rc-local.service")
        if not msg == "rc-local.service":

            conf.set('Install', "Alias", "rc-local.service")

    conf.write(open(servicePath, "w", encoding="utf-8"))

    # 3、创建软链接
    if os.path.exists(serviceLink):
        tmpPath = os.path.realpath(serviceLink)
        if not tmpPath == servicePath:
            os.remove(serviceLink)
            os.symlink(servicePath, serviceLink)
    else:
        os.symlink(servicePath, serviceLink)

    # 4、 修改/etc/rc.local
    if not os.path.exists(rcLocalPath):
        with open(rcLocalPath, "w") as f:
            f.write("#!/bin/sh\n")

    # 读取全部内容
    buf = ""
    with open(rcLocalPath, "r+") as f:
        buf = f.read()

    if not args.Del:

        pos = buf.find(args.cmd)
        if pos == -1:
            if buf[-1] != '\n':
                buf += '\n'
            buf += args.cmd
    else:
        buf = buf.replace(args.cmd, "")

    with open(rcLocalPath, "w") as f:
        f.write(buf)

    os.chmod(rcLocalPath, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(-1)
    sys.exit(0)
