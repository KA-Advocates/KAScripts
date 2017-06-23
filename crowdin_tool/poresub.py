#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief Crowdin .po file re.sub() on entry
#
# Usecase:
#   Batch translation helper for .po file
#
# Example:
#       ./poresub.py --key-type msgstr --pattern 'The answer' --replace 'Die Antwort' sample_in.po [sample_out.po]
#
#
import argparse, sys, re, codecs, os
import polib

class Poresub(object):
    """re.sub() on pofile.
    """

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict   = opt_dict
        self.__is_verbose = self.__opt_dict['verbose']

        # key type
        self.__key_type   = self.__opt_dict['key_type']
        if (self.__key_type == None):
            raise RuntimeError('No key type specified')
        valid_key_type = ['msgid', 'msgstr']
        if (self.__key_type not in valid_key_type):
            raise RuntimeError('Invalid key_type')
        self.__verbose_out('# key_type: {0}'.format(self.__key_type))

        # regex: pattern
        self.__pattern_list = self.__opt_dict['pattern_list']
        if (self.__pattern_list == None):
            raise RuntimeError('No regexp patteren_dict (pattern, replace) specified')

        for i in self.__pattern_list:
            assert(len(i) == 2) # must have two strings
            self.__verbose_out('# ' + i[0] + ": " + i[1])

        # in_file
        self.__in_file = self.__opt_dict['in_file']
        if (self.__in_file == None):
            raise RuntimeError('No input file')

        self.__verbose_out('# in_file: {0}'.format(self.__in_file))

        # out_file
        self.__out_file = self.__opt_dict['out_file']
        if (self.__out_file == None):
            raise RuntimeError('No output file')

        self.__force_override = False


    def __verbose_out(self, mes):
        """verbose output if self.__is_verbose is True
        """
        if (self.__is_verbose == True):
            print(mes)

    def __get_metadata_string(self, metadata_dict):
        """get metadata strings via new POFile()
        """
        po = polib.POFile()
        po.metadata = metadata_dict
        metadata_str = po.__unicode__() + '\n\n'

        return metadata_str

    def __apply_sub(self, str_content):
        """apply re.sub() to str_content"""

        for i in self.__pattern_list:
            # print('# in: {0}'.format(str_content))
            # instr = str_content
            assert(len(i) == 2)
            str_content = re.sub(i[0], i[1], str_content, re.MULTILINE)
            # if (instr != str_content):
            #    print('# (pat,repl) = ({0},{1}), result: {2})'.format(i[0], i[1], str_content))

        return str_content


    def __process_po_in(self, po_in):
        """process one po object
        """

        # Entry members (see the polib documentation, actually source
        # code of POEntry)
        #
        #  comment:     string, the entry comment.
        #  tcomment:    string, the entry translator comment.
        #  occurrences: list, the entry occurrences.
        #  flags:       list, the entry flags.
        #  previous_msgctxt:      string, the entry previous context.
        #  previous_msgid:        string, the entry previous msgid.
        #  previous_msgid_plural: string, the entry previous msgid_plural.
        #  linenum:               integer, the line number of the entry
        #
        # Then, msgid, msgstr, (msgcxt)
        for ent in po_in:
            if (self.__key_type == 'msgid'):
                res = self.__apply_sub(ent.megid)
                ent.megid = res
            elif (self.__key_type == 'msgstr'):
                res = self.__apply_sub(ent.msgstr)
                ent.msgstr = res
            else:
                raise RuntimeError('Unknown key_type.')


    def run(self):
        """run the po file grep"""

        # open po file
        self.__verbose_out('# Loading {0}'.format(self.__in_file))
        po_in = polib.pofile(self.__in_file, encoding='utf-8')
        self.__verbose_out('# loading done')

        # process po object
        self.__process_po_in(po_in)

        po_out = ''

        # Add metadata header
        po_out = self.__get_metadata_string(po_in.metadata)

        for ent in po_in:
            po_out += (str(ent) + '\n')

        # Write to file/stdout
        if (self.__out_file == "-"):
            print(po_out + '\n')
        else:
            if (os.path.isfile(self.__out_file) and (self.__force_override == False)):
                # raise RuntimeError('output file exists. If you want to force override, use --force_override option.')
                raise RuntimeError('output file [{0}] exists.'.format(self.__out_file))

            if (len(po_out) > 0):
                with open(self.__out_file, encoding='utf-8', mode='w') as outfile:
                    outfile.write(po_out + '\n')
            else:
                print('# empty result file, skip to output {0}'.format(self.__out_file))



    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 2, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = Poresub.get_version_number()

        return '''poresub.py {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])


def poresub_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file", type=str, nargs=1,
                        help="Input PO/POT file")

    parser.add_argument("out_file", type=str, default="-", nargs="?",
                        help="Output filename (- is stdout)")

    parser.add_argument("-k", "--key-type", choices=['msgid', 'msgstr'], default='msgstr',
                        help="key type to apply the regex.")

    parser.add_argument("-p", "--pattern", type=str, default='',
                        help="patter of re.sub(pattern, replace, string).")

    parser.add_argument("-r", "--replace", type=str, default='',
                        help="replace of re.sub(pattern, replace, string).")

    parser.add_argument("--pattern-list-file", type=str, default='',
                        help="pattern list file {pattern, replace} of re.sub(pattern, replace, string) dict file. "
                        "When --pattern and --replace are specified, added (override) that pair.")

    parser.add_argument("-w", "--wrapwidth", type=int, default=78,
                        help="text wrap width to the polib.")

    parser.add_argument("--verbose", action="store_true",
                        help="increase output verbosity")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of poresub.py")

    args = parser.parse_args()

    if (args.version == True):
        sys.stderr.write(Poresub.get_version_string())
        sys.exit(1)

    # Switch stdout codecs to utf-8
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    pattern_list = []
    if (args.pattern_list_file != ''):
        with open(args.pattern_list_file, encoding='utf-8', mode='r') as list_file:
            list_file_str = list_file.read()
            # print(list_file_str)
            pattern_list = eval(list_file_str)

    if ((args.pattern != '') and (args.replace != '')):
        # FIXME Find the pattern and replace
        for i in range(0, len(pattern_list) - 1):
            if (pattern_list[i][0] == args.pattern):
                print('# Override [{0}, {1}]'.format(pattern_list[i][0], pattern_list[i][1]))
                pattern_list[i][1] = args.replace
                print('# Override [{0}, {1}]'.format(pattern_list[i][0], pattern_list[i][1]))
                break

    opt_dict = {
        'in_file':        args.in_file[0],  # nargs gives a list, but we need only one
        'out_file':       args.out_file,
        'key_type':       args.key_type,
        'pattern_list':   pattern_list,
        'wrapwidth':      args.wrapwidth,
        # 'force_override': args.force_override,
        'verbose':        args.verbose,
    }


    poresub = Poresub(opt_dict)
    poresub.run()


if __name__ == "__main__":
    try:
        poresub_main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
