import util
import os

MANIFEST_NAME_NODE = '0x01010003'

def isElement(line):
    return line.strip()[:2] == 'E:'

def getElementName(line):
    return line.strip().split(' ')[1]

def isAttr(line):
    return line.strip()[:2] == 'A:'

def isNode(line):
    return line.strip()[:2] == 'N:'

def getAttrNameAndValue(line):
    temp = line.strip().split(' ')[1]
    pos = temp.find('=')
    name = temp[:pos]
    return name[name.find('(') + 1:name.find(')')], temp[pos + 1:]

def getDepth(line):
    return (len(line) - len(line.lstrip())) / 2

def parse_manifest(pkg):
    depth_nodes = []
    f = open('manifests/' + pkg + '.manifest')
    offset = 0
    for line in f:
        line = line.replace('"', '')
        if isNode(line):
            if getDepth(line) >= len(depth_nodes):
                offset += 1
            continue
        depth = getDepth(line) - offset
        if isElement(line):
            name = getElementName(line)
            cur_node = {}
            if len(depth_nodes) <= depth:
                depth_nodes.append(None)
            depth_nodes[depth] = cur_node
            if depth > 0:
                if name not in depth_nodes[depth - 1]:
                    depth_nodes[depth - 1][name] = []
                depth_nodes[depth - 1][name].append(depth_nodes[depth])
        elif isAttr(line):
            [name, value] = getAttrNameAndValue(line)
            ele = depth_nodes[depth - 1]
            ele[name] = value
    return depth_nodes[0]

def parseIntent(data):
    items = data.split(',')
    if len(items) < 4:
        return None
    return [items[1], items[2], items[3].split('/')[0], items[3].split('/')[1]]

def parse_icc(pkg):
    f = open('iccs/' + pkg + '.icc')
    sService = []
    sBroadcast = []
    cur_status = ''
    for l in f:
        line = l.strip()
        if line.startswith('Landroid'):
            cur_status = line
        elif line.startswith('L'):
            cur_status = ''
        elif line.startswith('{'):
            if cur_status == '':
                continue
            elif cur_status.endswith('startService') or cur_status.endswith('bindService'):
                intent = line[1:-2].split('|')[0]
                sService.append({'intent': parseIntent(intent)})
            elif cur_status.endswith('sendBroadcast'):
                items = line[1:-2].split('|')
                new_data = {'intent': parseIntent(items[0])}
                permission = None
                if len(items) > 1:
                    permission = items[1].split(',')[1]
                if permission == 'null' or permission == '':
                    permission = None
                new_data['permission'] = permission
                sBroadcast.append(new_data)
    return {'service': sService, 'broadcast': sBroadcast}

top_pkgs = util.readTopList(500)
pkg_map = {}
for pkg in top_pkgs:
    if os.path.getsize('manifests/' + pkg + '.manifest') == 0:
        continue
    manifest = parse_manifest(pkg)
    if 'application' in manifest:
        pkg_map[pkg] = (parse_icc(pkg), parse_manifest(pkg))

pkgs = pkg_map.keys()

def hasReceiver(manifest, action, permission):
    app = manifest['application'][0]
    if 'receiver' not in app:
        # print manifest['package'] + ' has not receivers'
        return False
    receivers = app['receiver']
    for recv in receivers:
        if 'intent-filter' not in recv:
            continue
        filters = recv['intent-filter']
        for filt in filters:
            if 'action' not in filt:
                continue
            actions = filt['action']
            for act in actions:
                act_str = act[MANIFEST_NAME_NODE]
                if act_str == action:
                    if permission == None:
                        return True
    return False
    
def hasService(manifest, service):
    app = manifest['application'][0]
    if 'service' not in app:
        return False
    services = app['service']
    for serc in services:
        if MANIFEST_NAME_NODE not in serc:
            continue
        name = serc[MANIFEST_NAME_NODE]
        if name == service:
            return True
    return False

def isPackageRelated(pkg1, pkg2):
    icc1 = pkg_map[pkg1][0]
    manifest1 = pkg_map[pkg1][1]
    icc2 = pkg_map[pkg2][0]
    manifest2 = pkg_map[pkg2][1]

    # Both use Leancloud Push SDK?
    leanCloudService = 'com.avos.avoscloud.PushService'
    if hasService(manifest1, leanCloudService) and hasService(manifest2, leanCloudService):
        return 'LeanCloud Push SDK'
    getuiService = 'com.igexin.sdk.PushService'
    if hasService(manifest1, getuiService) and hasService(manifest2, getuiService):
        return 'Getui Push SDK'

    for service in icc1['service']:
        intent = service['intent']
        if intent == None:
            continue
        package, activity = intent[2], intent[3]
        if pkg2 == package or activity.startswith(pkg2):
            return "startService or bindService"
    for broadcast in icc1['broadcast']:
        intent = broadcast['intent']
        if intent == None:
            continue
        action, package, activity = intent[0], intent[2], intent[3]
        permission = broadcast['permission']
        if pkg2 == package or activity.startswith(pkg2):
            return "Broadcast: " + action
        elif hasReceiver(manifest2, action, permission):
            return "Broadcast: " + action
    return None

count = 0
for pkg1 in pkgs:
    for pkg2 in pkgs:
        if pkg1 == pkg2:
            continue
        ret = isPackageRelated(pkg1, pkg2)
        if ret != None:
            print pkg1 + ' --> ' + pkg2
            print ret + '\n'
            count += 1

print count






