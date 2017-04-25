#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief extension of split strings with tokenizeing. Math, white spaces.
#
#
# Use case:
#
# Example:
#    Simple example
#       ./tokensplit.py
#
#
import argparse, sys, re, codecs, os, collections


class TokenSplit(object):
    """Extension of split strings by a tokenizer
    """

    def __init__(self, opt):
        """constructor
        """
        self.__opt = opt;
        self.__token = collections.namedtuple('Token', ['type', 'value'])

        self.__keywords = [
            'ISO_NUMBER', 'TEX_SPACE', 'WHITESPACE', 'MATH_INOUT', 'NEWLINE_STR',
            'WORD', 'NOTSPACIAL', 'ESC_DOLLAR',
        ]
        self.__token_specification = [
            ('ISO_NUMBER',     r'\d+(\.\d*)?'), # ISO integer or decimal number
            ('TEX_SPACE',      r'\\\\'),        # '\\'
            ('WHITESPACE',     r'[ \t\n]'),     # white space (\S might be better?)
            ('MATH_INOUT',     r'\$'),          # math mode in/out '$'
            ('NEWLINE_STR',    r'\\n'),         # line endings string '\n'
            ('WORD',           r'[A-Za-z]+'),   # word like string
            ('NOTSPACIAL',     r'.'),           # Any other character
        ]
        self.__tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.__token_specification)
        # print('# token regexp: 'self.__tok_regex)
        self.__re_comp   = re.compile(self.__tok_regex)


    def __tokenize(self, str):
        """tokenize string
        Assumption: Crowdin string is relatively short.
        Othewise this should be a generator.
        """
        ret_str_list  = []
        cur_str       = ''
        last_keyword  = 'NOTSPACIAL'

        token_list = []
        for mo in self.__re_comp.finditer(str):
            kind  = mo.lastgroup
            value = mo.group(kind)
            token_list.append(self.__token(kind, value))

        # merge \\$
        merged_token_list = []
        nb_token = len(token_list)
        idx = 0
        while (idx < nb_token):
            if ((token_list[idx].type == 'TEX_SPACE') and
                (idx + 1 < nb_token)                  and
                (token_list[idx + 1].type == 'MATH_INOUT')):
                # \\$ found
                merged_token_list.append(self.__token('ESC_DOLLAR',
                                                      token_list[idx].value + token_list[idx + 1].value))
                idx += 1
            else:
                merged_token_list.append(token_list[idx])

            idx += 1

        return merged_token_list


    def split(self, str):
        """get splitted string in an array

        @param[in] str_list string list
        @return    splitted new list
        """
        token_list = self.__tokenize(str)

        nb_token = len(token_list)
        idx = 0
        split_str = []
        cur_line  = ''
        is_math_mode_in = False
        while (idx < nb_token):
            # print('### ' + token_list[idx].__str__())
            if (token_list[idx].type == 'MATH_INOUT'):
                if (idx == 0):
                    cur_line += token_list[idx].value
                else:
                    if (is_math_mode_in == False):
                        # out -> in, first output the last, then the new line starts with $
                        split_str.append(cur_line)
                        cur_line = token_list[idx].value
                    else:
                        # in -> out, first close the $, then make an empty new line
                        cur_line += token_list[idx].value
                        split_str.append(cur_line)
                        cur_line = ''
                # update in/out
                is_math_mode_in = not is_math_mode_in
            else:
                cur_line += token_list[idx].value
            # update the index
            idx += 1
            # print('{0}:{1}'.format(idx, cur_line))

        if (is_math_mode_in == True):
            print('# Could not find closing $')

        split_str.append(cur_line)
        cur_line = ''

        return split_str



    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 1, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = TokenSplit.get_version_number()

        return '''TokenSplit {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])



def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--in-file", type=str,
    #                     help="Input file")

    parser.add_argument("-v", "--verbose", type=int, action="store", default='0',
                        help="Verbose mode (0 ... off, 1 ... on")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of pogrep.py")

    args = parser.parse_args()

    if (args.version == True):
        sys.stderr.write(TokenSplit.get_version_string())
        sys.exit(1)

    opt_dict = {
        'verbose':         args.verbose,
    }

    ts = TokenSplit(opt_dict)

    src_list = [r'Two math expressions $\\sqrt{2}$\\\\\\\n\n\nand the other is $how is daller sign\\$?$. Also \\$. That is all.',
                r'$\\sqrt{2} \\\\\n\n \\frac{1}{2}$ \\\\\\\n\n\n $foo$ \\$\n\n']
    for src_str in src_list:
        print('# in [{0}]'.format(src_str))
        split_list = ts.split(src_str)
        for split_str in split_list:
            print('#[{0}]'.format(split_str))



if __name__ == "__main__":
    try:
        main()
        sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
