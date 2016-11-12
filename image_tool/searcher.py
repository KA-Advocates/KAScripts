import re
import os
import sys
import json
import polib
import codecs
import fileinput


folder = "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr\\"


def word_errors(filename):
    """ Detect Word document polution.
    All of those sections should be removed from strings.
    """
    textToSearch = "DocumentProperties"
    textToReplace = ""

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


def absolute_errors(filename, msgids):
    """ Obtain all strings that use absolute URLs.
    Those should be replaced by relative URLs.
    """
    if ".po" in filename:
        absolutes_po(filename, msgids)
    elif ".html" in filename:
        absolutes_html(filename, msgids)


def absolutes_po(filename, msgids):
    """ Find absolute URLs in PO files
    """
    po = polib.pofile(filename)
    for entry in po:
        if "www.khanacademy.org" in entry.msgid:
            msgids.append(entry.msgid + "\n")
            msgids.append("-----------\n")


def absolutes_html(filename, msgids):
    """ Find absolute URLs in article HTMLs.
    """
    with open(filename, 'r+', encoding='utf-8') as infile:
        for line in infile:
            if "www.khanacademy.org" in line:
                msgids.append(line)
                msgids.append("-----------\n")


# load mapping data from image hash to content slug
root = 'C:\\Workspace\\Khan\\Images\\'
with open(root + 'graphie_image_shas.json', 'r') as content:
    exercises = json.loads(content.read())
with open(root + 'graphie_image_shas_in_articles.json', 'r') as content:
    articles = json.loads(content.read())


def get_json_file(hash):
    """ Generate path to JSON image data file for given hash.
    """
    path = 'C:\\Workspace\\Khan\\Images\\{}\\{}\\{}-data.json'
    filename = path.format('json', hash[0], hash)
    return filename if os.path.isfile(filename) else None


def get_metadata(hash):
    """ Obtain content metadata like slug and item id for given hash.
    """
    if hash in exercises:
        return ('exercise', exercises[hash]['exerciseSlug'], exercises[hash]['itemId'])
    elif hash in articles:
        return ('articles', articles[hash], '')
    else:
        return ('', '', '')


def get_labels(hash):
    """ Extract labels used for an image of a given hash.
    Data is located in JSON data files available for each image.
    """
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



def graphie_po(filename, graphies):
    """ Find image references in PO files.
    """
    if not ".po" in filename:
        return

    po = polib.pofile(filename)
    for entry in po:
        graphie_entry(graphies, filename, None, entry.msgid, entry.msgstr)



def graphie_xliff(filename, graphies):
    """ Find image references in XLIFF files.
    """
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



# regular expressions for detecting image markup and reading its parts
regex = re.compile(r"\!\[(.*?)\]\((.+?)\)",re.MULTILINE|re.DOTALL)
linkx = re.compile(r"\s*(.*?)://(.*?)/([^\.\s]*)\.?([^\s]+)?",re.MULTILINE|re.DOTALL)

# collect strings with erroneous image references, e.g. with spaces in markup
spaced = []


def graphie_entry(graphies, filename, file_id, source, dest, id=None, ident=None):
    """ Prepares one or more report items for given string.
    Match is made for images hosted on amazonaws.com domain
    and if image is referenced via ![]() markup.
    This does not cover 100% of images are some are on other domains
    and some do not used markup, but these should not exist (?).
    """
    if not "amazonaws.com" in source:
        return

    # find all image markups
    matches = regex.findall(source)
    if not matches:
        matches = [[source, source]]

    for match in matches:
        # extract parts from image markup
        link = linkx.match(match[1]);
        if not link:
            print("ERROR: Link not parseable\n", source, match[1])
            continue

        # ignore HTTP images as this should not happen
        if link.groups()[0] == "http":
            continue

        # only analyze images hosted on amazonaws.com
        if "amazonaws.com" not in link.groups()[1]:
            continue

        # ignore hashes that are not 40 in lenght
        hash = link.groups()[2]
        if len(hash) != 40:
            continue

        # start preparing content for report
        links = "\t".join([e if e else '' for e in link.groups()])
        desc = match[0].strip(' \t\n\r').replace("\n", "\\n").replace("\r", "")
        url = match[1].strip(' \t\n\r')
        if url != match[1]:
            print("WARNING: Link wrapped in spaces\n", source, match[1])

        # get content metadata, e.g. a slug
        path = filename.replace(folder, "")
        (content_type, content_id, item_id) = get_metadata(hash)

        # erroneous image reference found, track it
        if url != match[1]:
            spaced.append("{}\t{}\thttps://crowdin.com/translate/khanacademy/{}/enus-sr#{}\t{}".format(file_id, id, file_id, id, match[1]))

        # extract all labels used in an image script
        (labeled, labels) = get_labels(hash)
        labels = "\t".join(labels) if labels else ''

        # prepare tab separated report entry
        line = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}"
        line = line.format(id, ident, file_id, path, desc, url, content_type, content_id, item_id, labeled, links, labels)
        graphies.append(line)


def get_matches():
    """ Obtain a list of all PO files.
    """
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            matches.append(os.path.join(root, filename))
    return matches


def work_errors():
    """ Clean up PO files by removing excess Word content.
    Also, find all usages of absolute URLs and store them in a file.
    """
    msgids = []
    for match in get_matches():
        msgids.append("==============\n")
        msgids.append(match + "\n")
        msgids.append("==============\n")

        word_errors(match)
        absolute_errors(match, msgids)

    # write strings with abolute URLs to a file
    with open( "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr-absolutes\\report-po.txt", 'w+', encoding='utf-8' ) as out_file:
        out_file.writelines(msgids)


def work_pos():
    """ Generate report for PO files.
    """
    graphies = []
    for match in get_matches():
        print(match)
        graphie_po(match, graphies)
    save_graphies(graphies)


def work_xliffs():
    """ Generate report for XLIFF files.
    """
    graphies = []
    graphie_xliff('1_high_priority_platform.xliff.json', graphies)
    graphie_xliff('2_high_priority_content.xliff.json', graphies)
    graphie_xliff('3_medium_priority.xliff.json', graphies)
    graphie_xliff('4_low_priority.xliff.json', graphies)
    save_graphies(graphies)
    print('===========================================')
    for item in spaced:
        print(item)


def save_graphies(graphies):
    """ Save report to a file.
    """
    with open( "C:\\Users\\Igor\\Downloads\\Khan\\khan-sr-graphies\\report.txt", 'w+', encoding='utf-8' ) as out_file:
        lines = map(lambda x: x + "\n", graphies)
        out_file.writelines( lines )


work_xliffs()
