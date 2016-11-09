import re
import os
import sys
import json
import polib
import codecs
import fileinput


stats = {}
folder = "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr\\"



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
bracketx = re.compile(r"{[^{]*?}",re.MULTILINE|re.DOTALL)
bracket2x = re.compile(r"\\\\\$",re.MULTILINE|re.DOTALL)

spaced = []

def graphie_entry(graphies, filename, file_id, source, dest, id=None, ident=None):
##    bucks1 = source.count("$")
    bracketless = bracketx.sub("{...}", source);
    bracketless = bracket2x.sub("â‚¬", bracketless);
    bucks = bracketless.count("$")
##    if bracketless != source and bucks % 2 == 1 and bucks != bucks1:
##        print(source,"\n",bracketless)
##    return
    if bucks % 2 == 1:
        print("{}\t{}\t{}\t{}\t{}".format(file_id, id, ident, bucks, bracketless))

##        line = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}"
##        line = line.format(id, ident, file_id, path, desc, url, content_type, content_id, item_id, labeled, links, labels)
##        graphies.append(line)



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
##    for item in spaced:
##        print(item)
##    map(lambda x: print(x + "\n"), spaced)


def save_graphies(graphies):
    with open( "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr-graphies\\report.txt", 'w+', encoding='utf-8' ) as out_file:
        lines = map(lambda x: x + "\n", graphies)
        out_file.writelines( lines )


work_3()
