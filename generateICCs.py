import os
import util

pkgs = util.readTopList(500)

for pkg in pkgs:
    cmd = 'java -jar ICCSniffer.jar apps/%s.apk > iccs/%s.icc' % (pkg, pkg)
    util.run_cmd(cmd)
