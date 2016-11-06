#! /usr/bin/env python3
#******************************************************************************
# Copyright (C) 2015-2-9(Mon) Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief generate srt file from YouTube transcript text

import argparse, sys, re

class Txt2srt(object):
    """check the shell's incoming test code"""

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict      = opt_dict
        self.__infile        = None
        self.__last_time_str = '0:00'
        self.__cur_line      = 1
        self.__last_content  = None

    def __get_srt_time_str(self, time_str):
        """output srt time format from YouTube transcript time format
        """
        [min, sec] = re.split(':', time_str)
        retstr = '00:%02d:%02d,000' % (int(min), int(sec))
        return retstr


    def __out_one_item(self, line_time, line_content):
        """output one item using current state
        """
        if self.__last_content == None:
            self.__last_content = line_content
            return

        # line
        print(self.__cur_line)
        self.__cur_line += 1

        # time
        print(self.__get_srt_time_str(self.__last_time_str) + ' --> ' +\
              self.__get_srt_time_str(line_time))
        self.__last_time_str = line_time

        # contents
        print(self.__last_content)
        print()
        self.__last_content = line_content



    def conv(self):
        """convert the file
        """
        # print('# open[' + self.__opt_dict['infile'] + ']')
        self.__infile  = open(self.__opt_dict['infile'], 'r')
        if self.__infile == None:
            raise StandardError('File not found')

        for line in self.__infile:
            mat = re.match('(^[0-9]+:[0-9][0-9])(.*)', line)
            (line_time, line_content) = mat_pair = mat.group(1,2)
            # print(line_time)
            # print(line_content)
            self.__out_one_item(line_time, line_content)

        # output the last contents
        self.__out_one_item('99:99', 'end')


def main():
    """process the YouTube's transcript to generate a srt file."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action='store_true',
                        help="increase output verbosity")

    parser.add_argument("-i", "--infile", type=str,
                        default='',
                        help="input transcript filename.")

    args = parser.parse_args()
    # print("verbosity: {0}".format(args.verbosity))
    # print("infile:    {0}".format(args.infile))

    opt_dict = {'infile': args.infile}

    sc = Txt2srt(opt_dict)
    sc.conv()


if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except:
        print('uncaught exception:' + str(sys.exc_info()))


