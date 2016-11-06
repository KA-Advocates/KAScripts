#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2015-2016 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief srt file to some format
#
# Examples:
#
#    To text conversion (generate YouTube transcript file)
#         ./srtconv.py -i input.srt -o output.srt --outtype text
#
#    Concatenate subtitle lines (YouTube typically chops the subtitle lines by length)
#         ./srtconv.py -i input.srt -o output.srt --outtype srtcatline
#
#    Concatenate subtitle lines with remove the sutitle timing gap
#         ./srtconv.py -i input.srt -o output.srt --outtype srtcatline --timeline rm_gap
#
#
# Known issues
#    - The last line must have \n since the enmty line complete one
#      entry (otherwise list one will be removed.)
#    - The same as above, an empty line complete the one entry, so double empty lines casts an error.
#

import argparse, sys, re, codecs

class Srt2conv(object):
    """An srt file conversion tool"""

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict      = opt_dict
        self.__infile        = None
        self.__outfile       = None
        self.__cur_line      = 1
        self.__last_content  = None
        self.__re_int_num    = re.compile(r"\d+") # integer (\d is unicode digit)
        self.__re_blank_line = re.compile(r"^$")  # blank line
        #                                    00:00:05,490                 --> 00:00:05,640
        self.__re_timeline   = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)")


        self.__cur_line_num  = 0                  # current infile line number
        self.__cur_entry_num = 1                  # current subtitle entry number

        # current working subtitle entry list
        self.__cur_subtitle_entry = []

        # timeline operation buffer
        self.__time_second_entry = []
        # time difference tolerance
        self.__time_diff_tor = 0.02

        # parsed data is a list of each subtitle entry.
        #   [
        #     ['entry_num', 'time_info', ['subtitle_line1', ...]],
        #     ...
        #   ]
        #
        # Example:
        #   [
        #      ['1', '00:00:01,310 --> 00:00:05,490', ['line1', 'line2', ...]],
        #      ['2', '00:00:05,490 --> 00:00:05,640', ['line1', 'line2', ...]],
        #   ]
        self.__parsed_data = []


    def __out_raw(self):
        """output parsed raw data (for debug)
        """
        if (len(self.__parsed_data) == 0):
            raise RuntimeError('no parsed data. not raw output')

        for entry in self.__parsed_data:
            self.__outfile.write('{0}\n{1}\n'.format(entry[0], entry[1]))
            for sub in entry[2]:
                self.__outfile.write('{0}\n\n'.format(sub))


    def __out_as_text(self):
        """output text format for transcription
        """
        if (len(self.__parsed_data) == 0):
            raise RuntimeError('no parsed data. no text output')

        for entry in self.__parsed_data:
            for sub in entry[2]:
                self.__outfile.write('{0}\n\n'.format(sub))


    def __out_as_srt_catline(self):
        """output srt file with subtitle lines are concatenated.
        """
        if (len(self.__parsed_data) == 0):
            raise RuntimeError('no parsed data. no srt catline output')

        for entry in self.__parsed_data:
            self.__outfile.write('{0}\n'.format(entry[0]))
            self.__outfile.write('{0}\n'.format(entry[1]))
            for sub in entry[2]:
                self.__outfile.write('{0}'.format(sub))

            self.__outfile.write('\n\n')


    def __parse_entry_num(self, infile):
        """check the line match to the integer
        \param[in] infile current reading file object
        """

        raw_line = infile.readline()
        if (raw_line == ''):
            return False        # reach EOF

        self.__cur_line_num += 1
        line = raw_line.rstrip()
        mat = self.__re_int_num.fullmatch(line)
        # print('Entry #: {0}'.format(line))
        if (mat == None):
            raise RuntimeError('Unexpected line entry at line {0}. (non number/double empty lines)'.format(
                self.__cur_line_num))

        if (int(line) != self.__cur_entry_num):
            raise RuntimeError('Unexpected entry number. expected {0}, got {1}'.format(
                self.__cur_entry_num, line))

        self.__cur_subtitle_entry.append(self.__cur_entry_num)
        self.__cur_entry_num += 1

        return True


    def __parse_time_line(self, infile):
        """get the time line
        \param[in] infile current reading file object
        """
        raw_line = infile.readline()
        if (raw_line == ''):
            return False        # reach EOF

        self.__cur_line_num += 1
        line = raw_line.rstrip()
        self.__cur_subtitle_entry.append(line)
        # print('Timeline: {0}'.format(line))

        return True


    def __parse_subtitle_line(self, infile):
        """parse subtitle line. Ended with blank line
        \param[in] infile current reading file object
        """
        subtitle_lines = []

        while True:
            raw_line = infile.readline()
            if (raw_line == ''):
                return False        # reach EOF

            self.__cur_line_num += 1
            line = raw_line.rstrip()
            if (self.__re_blank_line.fullmatch(line)):
                self.__cur_subtitle_entry.append(subtitle_lines)
                return True

            subtitle_lines.append(line)


    def __parse_srt_file(self, infile):
        """parse srt file and keep the result on memory
        \param[in] infile current reading file object
        """

        self.__cur_line_num = 0
        while True:
            self.__cur_subtitle_entry = [] # clear current subtitle entry

            if (self.__parse_entry_num(infile) == False):
                break           # eof

            if (self.__parse_time_line(infile) == False):
                break           # eof

            if (self.__parse_subtitle_line(infile) == False):
                break           # eof

            self.__parsed_data.append(self.__cur_subtitle_entry)


        if (self.__opt_dict['verbose'] == True):
            print('verbose: processed {0} entries.'.format(len(self.__parsed_data)))


    def __get_timeline_to_seconds(self, timeline_str):
        """00:00:01,310 --> 00:00:05,490 to (start, end)
        """
        # timeline string to float second
        mat = self.__re_timeline.match(timeline_str)

        # print(timeline_str);
        if ((mat == None) or (mat.lastindex != 8)):
            raise RuntimeError('Fail to parse timeline string: {0}.'.format(timeline_str).encode('utf-8', 'ignore'))

        start_sec = float(mat.group(1)) * 3600.0 + float(mat.group(2)) * 60.0 + float(mat.group(3)) +\
                    float(mat.group(4)) / 1000.0
        end_sec   = float(mat.group(5)) * 3600.0 + float(mat.group(6)) * 60.0 + float(mat.group(7)) +\
                    float(mat.group(8)) / 1000.0
        return (start_sec, end_sec)

    def __get_second_to_timestr(self, sec):
        """153.974 to 00:02:33,974
        """
        h = float(int(sec/3600))
        sec -= 3600 * h
        m = float(int(sec/60))
        sec -= 60 * m
        s = float(int(sec))
        sec -= s
        sec_str = '{:02}:{:02}:{:02},{:03}'.format(int(h), int(m), int(s), int(sec * 1000))
        return sec_str

    def __operate_timeline_rm_gap(self):
        """operate timeline: rm_gap
        remove gap. remove the empty subtitle gap.
        """
        # convert time string to seconds
        self.__time_second_entry = []
        line = 1
        for entry in self.__parsed_data:
            # timeline string to float second
            (start_sec, end_sec) = self.__get_timeline_to_seconds(entry[1])
            # error check
            if (self.__opt_dict['verbose'] == True):
                print('verbose: parse time start: {0} -> end: {1}'.format(str(start_sec), str(end_sec)))
            if (start_sec > end_sec):
                raise RuntimeError('Inconsistent time at {0}: {1} > {2}'.format(line, str(start_sec), str(end_sec)))
            self.__time_second_entry.append([start_sec, end_sec])
            ++line

        # print(self.__time_second_entry)
        # remove gap
        for i in range(0, len(self.__time_second_entry) - 1):
            curr_end   = self.__time_second_entry[i][1]
            next_start = self.__time_second_entry[i+1][0]
            next_end   = self.__time_second_entry[i+1][1]
            # error check, try to fix when error
            if (curr_end > next_start):
                # found inconsistency. Try to fix it locally.
                if ((curr_end + self.__time_diff_tor) < next_end):
                    # Possible to fix it.
                    print('# Inconsistency detected, fixe it locally by shift to next_start {0} to {1}.'.\
                          format(str(next_start), format(curr_end + self.__time_diff_tor)))
                    next_start = curr_end + self.__time_diff_tor
                else:
                    raise RuntimeError('Inconsistent timeline at {0}: {1} -> {2}, but next end is {3}, cannot be fixed in tor: {4}.'.\
                                       format(i+1, str(curr_end), str(next_start), str(next_end), str(self.__time_diff_tor)))
            # fill more than the time tolerance
            if (curr_end < (next_start - self.__time_diff_tor)):
                # expand curent end to next start
                self.__time_second_entry[i][1] = self.__time_second_entry[i+1][0]
                if (self.__opt_dict['verbose'] == True):
                    print('verbose: fill the gap {0} to {1}'.format(curr_end, next_start))

        # get strings
        print('length {0}, {1}'.format(len(self.__time_second_entry), len(self.__time_second_entry)))
        for i in range(0, len(self.__time_second_entry)):
            start_str = self.__get_second_to_timestr(self.__time_second_entry[i][0])
            end_str   = self.__get_second_to_timestr(self.__time_second_entry[i][1])
            time_line = '{0} --> {1}'.format(start_str, end_str)
            self.__parsed_data[i][1] = time_line


    def __operate_timeline(self):
        """operate the timeline
        """
        timeline_str = self.__opt_dict['timeline']
        if (timeline_str == 'none'):
            # print('no timeline operation')
            return
        elif (timeline_str == 'rm_gap'):
            # print('rm_gap operation')
            self.__operate_timeline_rm_gap()
            return
        else:
            raise RuntimeError('Unknown timeline operation. {0}'.format(timeline_str))


    def __output(self):
        """output the lines
        """
        outtype_str = self.__opt_dict['outtype']
        if (outtype_str == 'raw'):
            self.__out_raw()

        elif (outtype_str == 'text'):
            self.__out_as_text()

        elif (outtype_str == 'srtcatline'):
            self.__out_as_srt_catline()

        else:
            raise RuntimeError('Unknown outtype. {0}'.format(outtype_str))



    def conv(self):
        """convert the file
        """
        self.__parsed_data = []
        with open(self.__opt_dict['infile'], encoding='utf-8', mode='r') as self.__infile:
            with open(self.__opt_dict['outfile'], encoding='utf-8', mode='w') as self.__outfile:
                self.__parse_srt_file(self.__infile)
                self.__operate_timeline()
                self.__output()


def main():
    """process a srt file."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="verbose mode on")

    parser.add_argument("-i", "--infile", type=str,
                        default='',
                        help="input srt filename.")

    parser.add_argument("-o", "--outfile", type=str,
                        default='',
                        help="output filename.")

    parser.add_argument("--outtype", type=str, choices=['raw', 'text', 'srtcatline'],
                        default='text',
                        help="output type. {raw, text, catline, }"+\
                        "raw:  output the parsed data as is (for debug). "
                        "text: output text only. Removed timing and entry number. "
                        "srtcatline: concatenate subtitle lines. ")

    parser.add_argument("--timeline", type=str, choices=['none', 'rm_gap', ],
                        default='none',
                        help="timeline operation. {none, rm_gap, }"+\
                        "rm_gap:  remove gap (empty time). ")


    args = parser.parse_args()
    # print("verbosity: {0}".format(args.verbosity))
    # print("infile:    {0}".format(args.infile))

    opt_dict = {
        'verbose': args.verbose,
        'infile':  args.infile,
        'outfile': args.outfile,
        'outtype': args.outtype,
        'timeline': args.timeline
    }

    if (args.infile == ''):
        raise RuntimeError('No input file. Use -i to specify the input file.')

    if (args.outfile == ''):
        raise RuntimeError('No output file. Use -o to specify the output file.')

    if (opt_dict['verbose'] == True):
        for opt in opt_dict:
            print('verbose: {0}: {1}'.format(opt, opt_dict[opt]))

    sc = Srt2conv(opt_dict)
    sc.conv()


if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))


