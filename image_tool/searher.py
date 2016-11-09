import re
import os
import sys
import json
import polib
import codecs
import fileinput


stats = {}
folder = "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr\\"


def clean(filename):
    textToSearch = "DocumentProperties"
    textToReplace = ""

##    fileToSearch = "C:\\Users\\Igor\\Downloads\\who-is-jmw-turner.html"
##    fileToSave = "C:\\Users\\Igor\\Downloads\\who-is-jmw-turner.output.html"

    regex = re.compile(r"<\!--.*?-->",re.MULTILINE|re.DOTALL)

    tempFile = open( filename, 'r+', encoding='utf-8' )
    data = tempFile.read()
    tempFile.close()

    data = regex.sub
    ("", data)

    savefile = filename.replace("khan-sr", "khan-sr-cleaned")
    if not os.path.exists(os.path.dirname(savefile)):
        os.makedirs(os.path.dirname(savefile))
    outFile = open( savefile, 'w+', encoding='utf-8' )
    outFile.write( data )
    outFile.close()


def absolutes(filename, msgids):
    if ".po" in filename:
        absolutes_po(filename, msgids)
    elif ".html" in filename:
        absolutes_html(filename, msgids)


def absolutes_po(filename, msgids):
    po = polib.pofile(filename)
    for entry in po:
        if "www.khanacademy.org" in entry.msgid:
            msgids.append(entry.msgid + "\n")
            msgids.append("-----------\n")


def absolutes_html(filename, msgids):
    with open(filename, 'r+', encoding='utf-8') as infile:
        for line in infile:
            if "www.khanacademy.org" in line:
                msgids.append(line)
                msgids.append("-----------\n")


labelx = re.compile(r'\s*label\s*\(')

root = 'C:\\Workspace\\Khan\\Images\\'
with open(root + 'graphie_image_shas.json', 'r') as content:
    exercises = json.loads(content.read())
with open(root + 'graphie_image_shas_in_articles.json', 'r') as content:
    articles = json.loads(content.read())


def get_json_file(hash):
    path = 'C:\\Workspace\\Khan\\Images\\{}\\{}\\{}-data.json'
    filename = path.format('json', hash[0], hash)
    return filename if os.path.isfile(filename) else None

##    filename = path.format('article', hash[0], hash)
##    if os.path.isfile(filename):
##        return filename
##    filename = path.format('misc', hash[0], hash)
##    if os.path.isfile(filename):
##        return filename
##    return None


##def has_labels(hash):
##    filename = get_json_file(hash)
##    if not filename:
##        return 'no'

##    if not filename:
##        return '?'
##
##    with open(filename, 'r') as content:
##        for line in content.readlines():
##            if labelx.match(line):
##                return 'yes'
##
##    return 'no'


def get_content(hash):
    if hash in exercises:
        return ('exercise', exercises[hash]['exerciseSlug'], exercises[hash]['itemId'])
    elif hash in articles:
        return ('articles', articles[hash], '')
    else:
        return ('', '', '')


tokens = {'plus': {'(':'one', '{':'two', '[':'three'}, 'minus':{')':'one', '}':'two', ']':'three'}}
labelx = re.compile(r'^\s*label\s*\((.*?)\)\s*(?:;|\.css|$|,\s*$)', re.MULTILINE|re.DOTALL)
splitex = re.compile(r'\)\s*,\s*label\s*\(', re.MULTILINE|re.DOTALL)


##def get_labels(hash):
##    filename = "C:\\Workspace\\Khan\\Images\\all\\{}\\{}.js"
##    filename = filename.format(hash[0], hash)
##    if not os.path.isfile(filename):
##        return []
##
##    output = []
##
##    js = None
##    with open(filename, 'r') as content:
##        js = content.read()
##
##    matches = labelx.findall(js)
##    if not matches:
##        return None
##
##    for match in matches:
##        labels = splitex.split(match)
##        for label in labels:
##            cnt = {}
##            args = []
##            arg = ''
##            quote = False
##            for char in label:
##                if not quote and sum(cnt.values()) == 0 and char == ',':
##                    args.append(arg.strip())
##                    arg = ''
##                    continue
##                elif not quote and char in tokens['plus'].keys():
##                    group = tokens['plus'][char]
##                    if not group in cnt:
##                        cnt[group] = 1
##                    else:
##                        cnt[group] += 1
##                elif not quote and char in tokens['minus'].keys():
##                    group = tokens['minus'][char]
##                    cnt[group] -= 1
##                elif char == "\"":
##                    quote = not quote
##
##                arg += char
##
##            if arg.strip():
##                args.append(arg.strip())
##
##            if( len(args) < 2):
##                print("\tERROR: [", filename, "] Not enough arguments:", args)
##                continue
##
##            output.append(args[1])
##
##    return output


def get_labels_2(hash):
    filename = "C:\\Workspace\\Khan\\Images\\json\\{}\\{}-data.json"
    filename = filename.format(hash[0], hash)
    if not os.path.isfile(filename):
        return ('?', [])
    labels = []
    try:
        with open(filename, 'r') as fin:
            content = fin.read()[48:-2]
            data = json.loads(content)
            for item in data['labels']:
                if 'content' in item:
                    label = item['content']
                    if label:
                        labels.append(str(label))
    except Exception as err:
        print("\tERROR: Can't get labels from JSON file for:", filename, err, sys.exc_info()[0] )
    return ('yes' if labels else 'no', labels)



def graphie(filename, graphies):
##    test = "https://ka-perseus-graphie.s3.amazonaws.com/ddc022e22077e640bc5d028a2ca03ee4dd5177bb.png"
##    link = linkx.match(test);
##    print(link.groups())
##    test = "https://ka-perseus-graphie.s3.amazonaws.com/ddc022e22077e640bc5d028a2ca03ee4dd5177bb"
##    link = linkx.match(test);
##    print(link.groups())

    if not ".po" in filename:
        return

    po = polib.pofile(filename)

    for entry in po:
        graphie_entry(graphies, filename, None, entry.msgid, entry.msgstr)



def graphie_2(filename, graphies):
    folder = 'C:\\Users\\Igor\\Downloads\\Khan\\khan-xliff\\'
    filename = folder + filename
    with codecs.open(filename, 'r', 'utf-8') as fin:
        data = fin.read()
        xliff = json.loads(data)
    for file in xliff['xliff']['file']:
        units = file['body']['trans-unit']
        if isinstance(units, dict):
            units = [units]
        for unit in units:
            if 'source' not in unit or not unit['source']:
                continue
            if not isinstance(unit['source']['$'], str):
                continue
            try:
                graphie_entry(graphies, file['@original'], file['@id'], unit['source']['$'], unit['target']['$'], unit['@id'], unit['@identifier'])
            except Exception as e:
                print('\tERROR Something: ', unit, '\n', str(e))



regex = re.compile(r"\!\[(.*?)\]\((.+?)\)",re.MULTILINE|re.DOTALL)
linkx = re.compile(r"\s*(.*?)://(.*?)/([^\.\s]*)\.?([^\s]+)?",re.MULTILINE|re.DOTALL)

spaced = []

def graphie_entry(graphies, filename, file_id, source, dest, id=None, ident=None):
    if not "amazonaws.com" in source:
        return

    matches = regex.findall(source)
    if not matches:
##        print("ERROR: No matches\n", source)
##        return
        matches = [[source, source]]

    for match in matches:
        link = linkx.match(match[1]);

        if not link:
            print("ERROR: Link not parseable\n", source, match[1])
            continue
        if link.groups()[0] == "http":
            continue
        if "amazonaws.com" not in link.groups()[1]:
            continue
        hash = link.groups()[2]
        if len(hash) != 40:
            continue

        links = "\t".join([e if e else '' for e in link.groups()])
        desc = match[0].strip(' \t\n\r').replace("\n", "\\n").replace("\r", "")
        url = match[1].strip(' \t\n\r')
        if url != match[1]:
            print("WARNING: Link wrapped in spaces\n", source, match[1])

##        translated = 'yes' if dest else 'no'
##        changed = 'yes' if dest and url not in dest else 'no'
        path = filename.replace(folder, "")
        (content_type, content_id, item_id) = get_content(hash)

        if url != match[1]:
            spaced.append("{}\t{}\thttps://crowdin.com/translate/khanacademy/{}/enus-sr#{}\t{}".format(file_id, id, file_id, id, match[1]))

        (labeled, labels) = get_labels_2(hash)
        labels = "\t".join(labels) if labels else ''

        line = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}"
##        line = line.format(id, ident, file_id, path, desc, url, content_type, content_id, item_id, translated, changed, labeled, links, labels)
        line = line.format(id, ident, file_id, path, desc, url, content_type, content_id, item_id, labeled, links, labels)
        graphies.append(line)



##labeled = has_labels('1e121e48f6ca0ba9dbb642f3040032a4503dac44')
##get_labels_2('023dbe4c28f68c0aae7e7bea1899b05699362717')


def get_matches():
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            matches.append(os.path.join(root, filename))
    return matches


def work_3():
    graphies = []
    graphie_2('1_high_priority_platform.xliff.json', graphies)
    graphie_2('2_high_priority_content.xliff.json', graphies)
    graphie_2('3_medium_priority.xliff.json', graphies)
    graphie_2('4_low_priority.xliff.json', graphies)
##    save_graphies(graphies)
    print('===========================================')
    for item in spaced:
        print(item)
##    map(lambda x: print(x + "\n"), spaced)


def work_2():
    graphies = []
    for match in get_matches():
        print(match)
        graphie(match, graphies)
    save_graphies(graphies)


def work_1():
    msgids = []
    for match in get_matches():
        print(match)
        msgids.append("==============\n")
        msgids.append(match + "\n")
        msgids.append("==============\n")
        clean(match)
        absolutes(match, msgids)
    with open( "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr-absolutes\\report-po.txt", 'w+', encoding='utf-8' ) as out_file:
        out_file.writelines( msgids)
    ##print(msgids)


def save_graphies(graphies):
    with open( "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr-graphies\\report.txt", 'w+', encoding='utf-8' ) as out_file:
        lines = map(lambda x: x + "\n", graphies)
        out_file.writelines( lines )


work_3()
