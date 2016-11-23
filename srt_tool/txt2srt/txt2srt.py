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
        # Assume the last subtitle string has 5 seconds duration
        self.__last_subtitle_str_duration = 5


    def __get_second_from_time_str(self, time_str):
        """get a second (an integer) from time_str
        \param[in] time_str time string. E.g., '10:15'
        \return second in integer E.g., 615 for '10:15'
        """
        [min, sec] = re.split(':', time_str)
        return 60 * int(min) + int(sec)

    def __get_time_str_from_second(self, sec):
        """get a time string (e.g., '10:15') from a seconds
        \param[in] sec integer second. E.g., 615
        \return time string E.g., '10:15' for 615
        """
        min_part = int(sec / 60)
        sec_part = sec - (min_part * 60)
        retstr = '%02d:%02d' % (min_part, sec_part)
        return retstr


    def __get_srt_time_str(self, time_str):
        """output srt time format from YouTube transcript time format
        """
        [min, sec] = re.split(':', time_str)
        retstr = '00:%02d:%02d,000' % (int(min), int(sec))
        return retstr


    def __out_one_item(self, line_time, line_content):
        """output one item using current state
        \param[in] line_time    current time
        \param[in] line_content current line contents
        """
        # DELETEME print('line_time: {0}, line_content: {1}'.format(line_time, line_content))

        # For the first time. We don't know the end time yet.
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

        # output the last contents. Assume
        # self.__last_subtitle_str_duration seconds for the last subtitle string
        last_sec = self.__get_second_from_time_str(self.__last_time_str) +\
                   self.__last_subtitle_str_duration
        self.__out_one_item(self.__get_time_str_from_second(last_sec), 'end')


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


