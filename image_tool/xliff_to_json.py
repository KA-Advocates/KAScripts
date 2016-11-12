import json
import codecs
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring

# folder containing XLIFF files
folder = '.\\'

def xliff_to_json(filename):
    """ Converts a single XLIFF file to a JSON equivalent.
    Removes some excess data such as notes (context).
    Requires a lot of memory to complete as files are large.
    """
    filename = folder + filename
    with codecs.open(filename, 'r', 'utf-8') as fin:
        xliff = fin.read()
        jsonx = bf.data(fromstring(xliff))

    for file in jsonx['xliff']['file']:
        # do some cleanup
        if 'group' in file['body']:
            file['body'].pop('group')
        # go through all strings...
        for unit in file['body']['trans-unit']:
            # ... and remove notes to reduce file size
            if 'note' in unit:
                try:
                    unit.pop('note')
                except Exception as e:
                    print("\tERROR: Unit is ", unit, "\n", str(e))
                    print(json.dumps(file, indent=2))
                    file['body']['trans-unit'].pop('note')

    # save new content as JSON file
    with open(filename + '.2.json', 'w', encoding='utf8') as fout:
        json.dump(jsonx, fout, ensure_ascii=False)


# previously downloaded XLIFF files from Crowdin
# remove xmlns="urn:oasis:names:tc:xliff:document:1.2" from files
xliff_to_json('1_high_priority_platform.xliff')
xliff_to_json('2_high_priority_content.xliff')
xliff_to_json('3_medium_priority.xliff')
xliff_to_json('4_low_priority.xliff')
