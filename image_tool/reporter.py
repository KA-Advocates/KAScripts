import re
import os
import sys
import json
import polib
import codecs
import fileinput


# folder where XLIFF files are located
folder = '.\\'


def graphie_xliff(filename, graphies):
    """ Go through all strings stored in given XLIFF file.
    Store report in graphies array.
    """
    filename = folder + filename
    with codecs.open(filename, 'r', 'utf-8') as fin:
        data = fin.read()
        xliff = json.loads(data)

    for file in xliff['xliff']['file']:
        units = file['body']['trans-unit']
        if isinstance(units, dict):
            units = [units]

        for unit in units:
            # ignore strange strings
            if 'source' not in unit or not unit['source']:
                continue
            if not isinstance(unit['source']['$'], str):
                continue

            try:
                # generate a single report line
                graphie_entry(graphies, file['@original'], file['@id'], unit['source']['$'], unit['target']['$'], unit['@id'], unit['@identifier'])
            except Exception as e:
                print('\tERROR Something: ', unit, '\n', str(e))


# regular expressions for detecting relevant patterns in strings
regex = re.compile(r"\!\[(.*?)\]\((.+?)\)",re.MULTILINE|re.DOTALL)
linkx = re.compile(r"\s*(.*?)://(.*?)/([^\.\s]*)\.?([^\s]+)?",re.MULTILINE|re.DOTALL)
bracket1x = re.compile(r"{[^{]*?}",re.MULTILINE|re.DOTALL)
bracket2x = re.compile(r"\\\\\$",re.MULTILINE|re.DOTALL)


def graphie_entry(graphies, filename, file_id, source, dest, id=None, ident=None):
    """ Generate a single report line if issue with odd number of bucks is found.
    """
    bracketless = bracket1x.sub("{...}", source);
    bracketless = bracket2x.sub("€", bracketless);

    # if there is and odd number of bucks, we have an issue!
    bucks = bracketless.count("$")
    if bucks % 2 == 1:
        line = "{}\t{}\t{}\t{}\t{}".format(file_id, id, ident, bucks, bracketless)
        graphies.append(line)
        print(line)


def work_bucks():
    """ Create a report with all issues with wrong usage of bucks.
    """
    graphies = []
    graphie_xliff('1_high_priority_platform.xliff.json', graphies)
##    graphie_xliff('2_high_priority_content.xliff.json', graphies)
    graphie_xliff('3_medium_priority.xliff.json', graphies)
##    graphie_xliff('4_low_priority.xliff.json', graphies)
    save_graphies(graphies)


def save_graphies(graphies):
    """ Save report.
    """
    with open( folder + "report.txt", 'w+', encoding='utf-8' ) as out_file:
        lines = map(lambda x: x + "\n", graphies)
        out_file.writelines( lines )


work_bucks()
