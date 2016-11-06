#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2015-2016 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief Crowdin .po file filter
#
# Usecase:
#    Filter translated entries from the .po file
#
# Tool:
# --tool none
#        no filtering
# --tool id_to_str
#        copy msgid string to msgstr string if msgstr is empty.
# --tool same
#        Outout when msgid == mgsstr
# --tool differ
#        Outout when msgid != mgsstr
#
# Example:
#    Extract non-translated entries (--id_to_str when msgstr is "")
#       ./pofilter.py --tool id_to_str -i sample.po -o sample.po.txt
#
#    Extract non-translated entries with context line
#    (Note: context is always output, means translated lines still outputs the context.)
#       ./pofilter.py --keep_context -i sample.po -o sample.po.txt
#
#


import argparse, sys, re, codecs, os.path

class Pofilter(object):
    """Crowdin .po file filter"""

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict      = opt_dict
        self.__infile        = None
        self.__outfile       = None
        self.__cur_line      = 0
        self.__is_keep_context   = opt_dict['keep_context']
        self.__is_remove_header  = opt_dict['remove_header']
        self.__tool              = opt_dict['tool']
        self.__is_force_override = opt_dict['force_override']
        self.__parsing_kind  = None    # 'msgid' | 'msgstr' | None
        self.__proc_items    = 0       # processed items for header output
        self.__proc_context_line = [];

        self.__re_context    = re.compile(r"^#.*$") # context line
        self.__re_msgid      = re.compile(r"^msgid .*") # msgid line
        self.__re_msgstr     = re.compile(r"^msgstr .*") # msgid line
        self.__re_dequote    = re.compile(r'^".*') # double quote started line

        self.__re_empty      = re.compile(r"^$")   # empty line

    def __is_line_context(self, line):
        """Is the line context line?
        """
        mat = self.__re_context.fullmatch(line)
        # print('This is entry. {0}:'.format(line))
        if (mat != None):
            # print('context')
            return True
        else:
            # print('not context')
            return False


    def __get_msg(self, proc_lines, msg_re):
        """get msg{id,str} chank as a list
        \param[in] proc_lines all readed lines, has been processed for context
        \param[in] msg_re matching regex (msg{id,str})
        \return list of the msg{id,str}
        """
        # look for msg{id,str} from the current line
        nb_line = len(proc_lines)

        # find msg{id,str} line
        msg_cont_str = []
        while True:
            if (self.__cur_line >= nb_line):
                # reach to the end
                return msg_cont_str

            line = proc_lines[self.__cur_line].rstrip()
            # print('line:{0}: {1}'.format(self.__cur_line, line).encode('utf-8', 'ignore'))

            ma = msg_re.match(line)
            if (ma != None):
                # Note: ma.group(1) doesn't work when '\n' is in the string (mutiple lines)
                # print('found msgid/msgstr line:{0}'.format(self.__cur_line))
                msg_cont_str.append(line)
                # print('append line 1:{0}: {1}'.format(self.__cur_line, line).encode('utf-8', 'ignore'))
                self.__cur_line += 1
                break

            # print('not found msgid/msgstr line:{0}, lookup continue'.format(self.__cur_line))
            self.__cur_line += 1
            # when keep context, output this line
            if (self.__is_keep_context == True):
                self.__outfile.write(line + '\n')


        # continue the following msgid strings (continue as long as "" lines)
        while True:
            if (self.__cur_line >= nb_line):
                # reach to the end
                return msg_cont_str

            line = proc_lines[self.__cur_line].rstrip()
            # print('line:{0}: {1}'.format(self.__cur_line, line).encode('utf-8', 'ignore'))
            ma = self.__re_dequote.match(line)
            if (ma != None):
                # Note: ma.group(1) doesn't work when '\n' is in the string (mutiple lines)
                msg_cont_str.append(line)
                # print('append line 2:{0}: {1}'.format(self.__cur_line, line).encode('utf-8', 'ignore'))
                # print('double quote found at {0}'.format(self.__cur_line))
                self.__cur_line += 1
            else:
                # print('double quote not found at {0}'.format(self.__cur_line))
                break

        # print('finished chank process at {0}: {1}'.format(self.__cur_line, proc_lines[self.__cur_line]).encode('utf-8', 'replace'))
        return msg_cont_str


    def __comp_msg(self, msgid_str, msgstr_str):
        """value equality comparison between msgid_str and msgstr_str.
        Remove the tag msg{id,str} and compare the rest.
        \return True when equal, False otherwise
        """
        msgid_list_len  = len(msgid_str)
        msgstr_list_len = len(msgstr_str)
        # print('msgid_list_len {0}, msgstr_list_len {1}', msgid_list_len, msgstr_list_len)

        if (msgid_list_len == 0):
            raise RuntimeError('empty msgid_str.')

        if (msgstr_list_len == 0):
            raise RuntimeError('empty msgstr_str.')

        if (msgid_list_len != msgstr_list_len):
            return False        # there is a difference

        assert(msgid_str[0][0:6]  == "msgid ")
        assert(msgstr_str[0][0:7] == "msgstr ")

        # first line has the tag, msg{id,str}
        assert(msgid_str[0][0:6]  == "msgid ")
        assert(msgstr_str[0][0:7] == "msgstr ")
        if (msgid_str[0][6:]  != msgstr_str[0][7:]):
            return False

        for i in range(1, len(msgid_str)):
            if (msgid_str[i] != msgstr_str[i]):
                return False

        # all equal
        return True


    def __write_list(self, str_list, outfile):
        """write a list to the outfile
        """
        for line in str_list:
            outfile.write(line +'\n')


    def __is_msgstr_empty(self, msgstr_str):
        """The new untranslated style, deetect msgstr emptycase"""

        assert(msgstr_str[0][0:7] == "msgstr ") # we process msgstr line

        if  (msgstr_str[0][7:] != '\"\"'):
            # msgstr "something" case
            # print('msgstr something case: {0}'.format(msgstr_str[0][8:]).encode('utf-8', 'ignore'))
            return False

        for i in range(1, len(msgstr_str)):
            if (msgstr_str[i] != '\"\"'):
                # "something" case
                # print('something case: {0}'.format(msgstr_str).encode('utf-8', 'ignore'))
                return False

        # All of the followings are "" case
        # print("double quote only case.")
        return True


    def __id_to_str_is_output_pair(self, msgid_str, msgstr_str):
        """output the pair or not"""

        # New style (msgstr "")
        if (self.__is_msgstr_empty(msgstr_str) == True):
            return True

        # Old style (the same string contained in the msgid_str and msgstr_str)
        if (self.__comp_msg(msgid_str, msgstr_str) == True):
            return True

        return False

    def __id_to_str_output_strings(self, msgid_str, msgstr_str):
        """output msgid and msgstr"""

        if (self.__proc_items > 0):
            # output msgid as is
            self.__write_list(msgid_str,  self.__outfile)
            # Output msgstr by coping msgid string if msgstr input is ""
            #   1. deep copy msgid
            deep_copied_msgid = msgid_str[:]
            #   2. s/msgid /msgstr /
            #   print('|{0}|'.format(deep_copied_msgid[0][6:]))
            deep_copied_msgid[0] = 'msgstr ' + deep_copied_msgid[0][6:]
            self.__write_list(deep_copied_msgid,  self.__outfile)
            self.__outfile.write('\n')

        else:
            # Output the meta data
            #   Output by coping the input
            self.__write_list(msgid_str,  self.__outfile)
            self.__write_list(msgstr_str, self.__outfile)
            self.__outfile.write('\n')


    def __id_to_str_output(self, proc_context_line):
        """Tool id_to_str output.
        msgid is copied to msgstr when msgstr is empty.
        """
        # process pair of (msgid, msgstr)
        nb_lines = len(proc_context_line)
        self.__cur_line = 0
        self.__proc_items = 0
        while (self.__cur_line < nb_lines):
            msgid_str  = []
            msgstr_str = []
            msgid_str   = self.__get_msg(proc_context_line, self.__re_msgid)
            msgstr_str  = self.__get_msg(proc_context_line, self.__re_msgstr)
            # print('msgid: {0}'.format(msgid_str).encode('utf-8', 'ignore'))
            # print('msgstr:{0}'.format(msgstr_str).encode('utf-8', 'ignore'))

            if (len(msgid_str) == 0):
                # print('no more msgid')
                return

            if (self.__id_to_str_is_output_pair(msgid_str, msgstr_str) == True):
                self.__id_to_str_output_strings(msgid_str, msgstr_str)

            # Record processed msgid & msgstr items
            self.__proc_items += 1


    def __same_differ_output_strings(self, msgid_str, msgstr_str):
        """Tool msdid and msgstr are same/differ string output.
        The strings are output as is.
        """
        # Output as is
        self.__write_list(msgid_str,  self.__outfile)
        self.__write_list(msgstr_str, self.__outfile)
        self.__outfile.write('\n')


    def __same_differ_output(self, proc_context_line, is_same):
        """Tool same output.
        Output when msgid and msgstr are the same when is_same == True,
        Output when msgid and msgstr differs when is_same == False

        """
        # process pair of (msgid, msgstr)
        nb_lines = len(proc_context_line)
        self.__cur_line = 0
        self.__proc_items = 0
        while (self.__cur_line < nb_lines):
            msgid_str  = []
            msgstr_str = []
            msgid_str   = self.__get_msg(proc_context_line, self.__re_msgid)
            msgstr_str  = self.__get_msg(proc_context_line, self.__re_msgstr)
            # print('msgid: {0}'.format(msgid_str).encode('utf-8', 'ignore'))
            # print('msgstr:{0}'.format(msgstr_str).encode('utf-8', 'ignore'))

            if (len(msgid_str) == 0):
                # print('no more msgid')
                return

            # msgid == msgstr || (header out)
            # if (self.__comp_msg(msgid_str, msgstr_str) == True) or \
            #    ((self.__proc_items == 0) and (self.__is_remove_header == False)):
            #     # print(msgid_str)
            #     self.__write_list(msgid_str,  self.__outfile)
            #     self.__write_list(msgstr_str, self.__outfile)
            #     self.__outfile.write('\n')

            if (self.__comp_msg(msgid_str, msgstr_str) == is_same):
                self.__same_differ_output_strings(msgid_str, msgstr_str)

            self.__proc_items += 1

    def __header_handling(self):
        """po file header handling.
        Remove the header from proc_context_line. If the header is needed, output them.
        """
        # header output handling
        num_msgid = 0
        header_line = 0
        for line in self.__proc_context_line:
            ma = self.__re_msgid.match(line)
            if (ma != None):
                num_msgid += 1
            if (num_msgid >= 2):
                # header has ended.
                break
            if (self.__is_remove_header == False):
                # if header is needed, output
                self.__outfile.write(line)
            header_line += 1

        # print('Number of header lines: {0}'.format(header_line))
        # Remove the header lines from the list
        if (header_line > 0):
            del self.__proc_context_line[0: header_line]


    def __apply_filter(self):
        """apply the filter function for the po file.
        """
        assert(self.__infile  != None)
        assert(self.__outfile != None)

        self.__is_parsing_str = None # init to msgid
        msgid_str  = []
        msgstr_str = []

        # read all lines
        all_lines = self.__infile.readlines()

        # handle context
        self.__proc_context_line = []
        if (self.__is_keep_context == True):
            # print('keep context')
            self.__proc_context_line = all_lines
        else:
            # print('remove context')
            for raw_line in all_lines:
                # check the context
                line = raw_line.rstrip()
                if (self.__is_line_context(line) == False):
                    self.__proc_context_line.append(raw_line)

        # for line in proc_context_line:
        #     self.__outfile.write(line)

        # process header. Work on self.__proc_context_line directry inside the method.
        # since if it is arg, passing by value, thus, copied.
        self.__header_handling()

        # for i in self.__proc_context_line:
        #     print('after:{0}'.format(i).encode('utf-8', 'ignore'))

        # process body. pass self.__proc_context_line in the argument.
        if (self.__tool == 'id_to_str'):
            self.__id_to_str_output(self.__proc_context_line)
        elif (self.__tool == 'same'):
            is_same = True
            self.__same_differ_output(self.__proc_context_line, is_same)
        elif (self.__tool == 'differ'):
            is_same = False
            self.__same_differ_output(self.__proc_context_line, is_same)
        else:
            raise RuntimeError('No such tool {0}.'.format(self.__tool))


    def filter(self):
        """perform filter action
        """
        if (os.path.isfile(self.__opt_dict['outfile']) and (self.__is_force_override == False)):
            raise RuntimeError('output file exists.')

        with open(self.__opt_dict['infile'], encoding='utf-8', mode='r') as self.__infile:
            with open(self.__opt_dict['outfile'], encoding='utf-8', mode='w') as self.__outfile:
                self.__apply_filter()


def main():
    """process a srt file."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="verbose output.")

    parser.add_argument("-i", "--infile", type=str,
                        default='',
                        help="input srt filename.")

    parser.add_argument("-o", "--outfile", type=str,
                        default='',
                        help="output filename.")

    parser.add_argument("--keep_context", action='store_true',
                        help="keep the context line.")

    parser.add_argument("--remove_header", action='store_true',
                        help="remove the header lines.")

    parser.add_argument("--tool", choices=['id_to_str', 'same', 'differ'],
                        help="tools. id_to_str: copy msgid to msgstr. same: msgid == msgstr. differ: msgid != mgsstr")

    parser.add_argument("--force_override", action='store_true',
                        help="Even outfile is found, override the output file.")

    args = parser.parse_args()

    opt_dict = {
        'infile':         args.infile,
        'outfile':        args.outfile,
        'keep_context':   args.keep_context,
        'remove_header':  args.remove_header,
        'tool':           args.tool,
        'force_override': args.force_override,
        'verbose':        args.verbose
    }

    if (args.verbose == True):
        for opt in opt_dict:
            print('verb: {0}: {1}'.format(opt, opt_dict[opt]))

    if (args.infile == ''):
        raise RuntimeError('No input file. Use -i to specify the input file.')

    if (args.outfile == ''):
        raise RuntimeError('No output file. Use -o to specify the output file.')

    if (args.tool == ''):
        raise RuntimeError('No tool specified. Please set the tool option.')

    pf = Pofilter(opt_dict)
    pf.filter()


if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
