#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief line extractor for pofiles. This can be a template for each
#        msgid/msgstr processor.
#
# Description:
#    Extract lines from a po file
#
# Example:
#
#       ./poline.py --key-type msgid _other.po
#
#
import argparse, sys, re, codecs, os
import tokenizer
import polib

class Poline_line_extract(object):
    """Line extractor of poline processor
    """

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict = opt_dict

        self.__is_proc_msgid = True;

        assert ('key_type' in opt_dict)
        if (opt_dict['key_type'] == 'msgstr'):
            self.__is_proc_msgid = False;

        self.__tokenizer = tokenizer.Tokenizer(opt_dict)
        self.__re_line_end = re.compile(r'[\n.?]')


    def __ext_line(self, in_str):
        """extract lines.
        @param[in] in_str input string
        @return    result string
        """
        line_list = []
        line = ''
        token_list = self.__tokenizer.tokenize(in_str)
        for tkn in token_list:
            if   (tkn.type == 'NEWLINE_STR'):
                # add newline as is
                line += tkn.value
            elif (tkn.type == 'NOTSPACIAL'):
                if (self.__re_line_end.match(tkn.value)):
                    line += tkn.value
                    line_list.append(line)
                    line = ''
                else:
                    line += tkn.value
            else:
                line += tkn.value
        if (len(line) > 0):
            line_list.append(line)
            line = ''

        return line_list


    def process(self, poent):
        """extracting line list
        @return result string list
        """
        if (self.__is_proc_msgid == True):
            return self.__ext_line(poent.msgid)
        else:
            return self.__ext_line(poent.msgstr)


class Poline(object):
    """Po msgid/msgstr processor.
    This can be a template program of each msgid/msgstr processor.
    The each msgid/msgline is processed in the Poline_proc.
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

        # in_file
        self.__in_file = self.__opt_dict['in_file']
        if (self.__in_file == None):
            raise RuntimeError('No input file')

        self.__verbose_out('# in_file:  {0}'.format(self.__in_file))

        # out_file
        self.__out_file = self.__opt_dict['out_file']
        if (self.__out_file == None):
            raise RuntimeError('No output file')
        self.__out_file_obj = None

        self.__verbose_out('# out_file: {0}'.format(self.__out_file))

        self.__force_override = False

        # create processor
        self.__proc_obj = Poline_line_extract(opt_dict);


    def __verbose_out(self, mes):
        """verbose output if self.__is_verbose is True
        """
        if (self.__is_verbose == True):
            print(mes)

    def __out(self, out_str):
        """output out_str"""
        if (self.__out_file_obj != None):
            self.__out_file_obj.write(out_str)
        else:
            print(out_str)

    def __process_po_obj(self, po_in):
        """process one file
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
            line_list = self.__proc_obj.process(ent)
            for line in line_list:
                self.__out(line.strip() +'\n') # double newline


    def run(self):
        """run the po file grep"""

        self.__verbose_out('# Loading {0}'.format(self.__in_file))
        po_in = polib.pofile(self.__in_file, encoding='utf-8')
        self.__verbose_out('# loading done')

        if (self.__out_file != "-"):
            if (os.path.isfile(self.__out_file) and (self.__force_override == False)):
                raise RuntimeError('output file [{0}] exists.'.format(self.__out_file))
            with open(self.__out_file, encoding='utf-8', mode='w') as out_file:
                self.__out_file_obj = out_file
                self.__process_po_obj(po_in)
        else:
            self.__process_po_obj(po_in)


    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 1, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = Poline.get_version_number()

        return '''poline.py {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])



def poline_main():
    parser = argparse.ArgumentParser()

    parser.add_argument("in_file", type=str, nargs=1,
                        help="Input filenames.")

    parser.add_argument("out_file", type=str, default="-", nargs="?",
                        help="Output filename (- is stdout)")

    parser.add_argument("--key-type", type=str,
                        choices=['msgid', 'msgstr'], default='msgid',
                        help="grep this key type in a po file")

    parser.add_argument("--force_override", action='store', default='0',
                        help="Even outfile is found, override the output file.")

    parser.add_argument("--verbose", action="store_true",
                        help="increase output verbosity")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of poline.py")

    args = parser.parse_args()

    # Switch stdout codecs to utf-8
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    if (args.version == True):
        sys.stderr.write(Poline.get_version_string())
        sys.exit(1)

    opt_dict = {
        'in_file':        args.in_file[0], # nargs gives a list, but we need one
        'out_file':       args.out_file,
        'key_type':       args.key_type,
        'force_override': args.force_override,
        'verbose':        args.verbose,
    }

    poline = Poline(opt_dict)
    poline.run()


if __name__ == "__main__":
    try:
        poline_main()
        sys.exit(0)
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
        sys.exit(2)
