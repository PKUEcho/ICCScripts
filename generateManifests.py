import os
import util

def main():
    pkgs = util.readTopList(3000)

    for pkg in pkgs:
        manifest = 'manifests/' + pkg + '.manifest'
        if os.path.exists(manifest):
            continue
        cmd = '~/tools/aapt dump xmltree apps/%s.apk AndroidManifest.xml > manifests/%s.manifest' % (pkg, pkg)
        util.run_cmd(cmd)

if __name__ == '__main__':
    main()
