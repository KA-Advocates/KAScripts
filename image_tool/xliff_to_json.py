import json
import codecs
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring

def xliff_to_json(filename):
    folder = 'C:\\Users\\Igor\\Downloads\\Khan\\khan-xliff\\'
    filename = folder + filename
    with codecs.open(filename, 'r', 'utf-8') as fin:
        xliff = fin.read()
        jsonx = bf.data(fromstring(xliff))

    for file in jsonx['xliff']['file']:
        if 'group' in file['body']:
            file['body'].pop('group')
##        if len(file['body']) == 1:
##            if 'note' in file['body']['trans-unit']:
##                file['body']['trans-unit'].pop('note')
##            continue
        for unit in file['body']['trans-unit']:
            if 'note' in unit:
                try:
                    unit.pop('note')
                except Exception as e:
                    print("\tERROR: Unit is ", unit, "\n", str(e))
                    print(json.dumps(file, indent=2))
                    file['body']['trans-unit'].pop('note')
##                    print(file)
    with open(filename + '.2.json', 'w', encoding='utf8') as fout:
        json.dump(jsonx, fout, ensure_ascii=False)


##xliff_to_json('1_high_priority_platform.xliff')
##xliff_to_json('2_high_priority_content.xliff')
##xliff_to_json('3_medium_priority.xliff')
xliff_to_json('4_low_priority.xliff')
