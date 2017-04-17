#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief grep for pofiles
#
# Description:
#    Get specific pattern entries in the po file. You can search
#    depends on the key.
#
# Example:
#    Grep on msgid with keywords 'this' for file _other_.po
#       ./pogrep.py --key-type msgid -e this _other_.po
#
#
import argparse, sys, re, codecs, os
import polib

class Pogrep(object):
    """grep on pofile.
    Search depends on keytype: msgid, msgstr
    Output matching entry
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

        # regexp
        restr = self.__opt_dict['regexp']
        if (restr == None):
            raise RuntimeError('No regexp specified')
        ignore_case_str = ''
        if (self.__opt_dict['ignore_case'] == True):
            self.__recomp = re.compile(restr, flags=re.IGNORECASE)
            ignore_case_str = 'with ignore case'
        else:
            self.__recomp = re.compile(restr)
        self.__verbose_out('# regexp:   {0} {1}'.format(restr, ignore_case_str))

        # inevert match
        self.__match_true = not self.__opt_dict['invert_match']
        self.__verbose_out('# match true (!invert_match): {0}'.format(self.__match_true))

        # in_file
        self.__in_file_list = self.__opt_dict['in_file']
        if (self.__in_file_list == None):
            raise RuntimeError('No input file')

        self.__verbose_out('# in_file:  {0}'.format(' '.join(self.__in_file_list)))

        # Switch stdout codecs to utf-8
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


    def __verbose_out(self, mes):
        """verbose output if self.__is_verbose is True
        """
        if (self.__is_verbose == True):
            print(mes)

    def __is_match(self, ent):
        """Check the entry matches the current condition.
        """
        check_str = None
        if (self.__key_type == 'msgid'):
            check_str = ent.msgid
        elif (self.__key_type == 'msgstr'):
            check_str = ent.msgstr
        else:
            raise RuntimeError('Unknown key_type')

        assert(check_str != None)
        # print('# check_str: '+ check_str)
        # Here must be search(). If match it only compare at the top of the line.
        is_found = self.__recomp.search(check_str) != None

        return self.__match_true == is_found

    def __process_one_file(self, infile):
        """process one file
        """
        self.__verbose_out('# Loading {0}'.format(infile))
        po_in = polib.pofile(infile, encoding='utf-8')
        self.__verbose_out('# loading done')

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
            if (self.__is_match(ent) == True):
                print(ent)
            else:
                # print('# no match')
                pass

    def run(self):
        """run the po file grep"""

        for f in self.__in_file_list:
            self.__process_one_file(f)


    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 1, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = Pogrep.get_version_number()

        return '''pogrep.py {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--key-type", type=str,
                        choices=['msgid', 'msgstr'], default='msgid',
                        help="grep this key type in a po file")

    # nargs tells how many args should be consumed, this is needed when
    # the regex start with '-'. Note: this gives the args in a list.
    parser.add_argument("-e", "--regexp", type=str, nargs=1,
                        help="Use regrep pattern for search. "
                        "If you need the pattern starts with '-', "
                        "use = option like -e='-pattern'.")

    parser.add_argument("-v", "--invert-match", action="store_true",
                        help="Invert the sense of matching. "
                        "This selects non-matching entries.")

    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Ignore the case in both the regexp match string "
                        "and the input file.")

    parser.add_argument("in_file", type=str, nargs='*',
                        help="Input filenames.")

    parser.add_argument("--out-file", type=str, default="-",
                        help="Output filename. The default is '-'. '-' is stdout")

    parser.add_argument("--force_override", action='store', default='0',
                        help="Even outfile is found, override the output file.")

    parser.add_argument("--verbose", action="store_true",
                        help="increase output verbosity")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of pogrep.py")

    args = parser.parse_args()

    if (args.version == True):
        sys.stderr.write(Pogrep.get_version_string())
        sys.exit(1)

    if (args.regexp == None):
        raise RuntimeError('-e/--regexp option was not specified.')

    opt_dict = {
        'key_type':       args.key_type,
        'regexp':         args.regexp[0], # nargs gives a list, but we need one
        'invert_match':   args.invert_match,
        'ignore_case':    args.ignore_case,
        'in_file':        args.in_file,
        'out_file':       args.out_file,
        'force_override': args.force_override,
        'verbose':        args.verbose,
    }

    pogrep = Pogrep(opt_dict)
    pogrep.run()


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
        sys.exit(2)
