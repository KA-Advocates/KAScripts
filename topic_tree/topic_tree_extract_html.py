#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief topic tree information extractor. For *my* html format.
#
# Usecase:
#
import argparse, sys, re, codecs, os, json
import topic_tree_extract_if

class TopicTreeExtractHTML(topic_tree_extract_if.TopicTreeExtractIF):
    """Khan academy topic tree information extractror from a topic tree JSON file.

    Output html format for my personal Khan academy web site until
    official Japanese page established.

    """

    def __init__(self, opt_dict):
        """constructor
        """
        super().__init__(opt_dict)

    def __get_one_li_element(self, topic_dict):
        """get one <li></li> element string
        """
        lstr = '''<li><!-- <span class="new_contents">(new date)</span> -->
  <a href=""
     name="Ja: {_en_video_title}">
        {_ja_video_title}</a>|
  <a href=""
     name="Ja: {_en_video_title}">
        {_ja_video_title_kana}</a>
  <a class="original_video_link"
     href="{_original_video_link_url}"
     name="En: {_en_video_title}">元のビデオ(英語) {_en_video_title}</a>
</li>

'''.format(_en_video_title=topic_dict['title'],
                _ja_video_title='JATITLE',
                _ja_video_title_kana='JATITLEKANA',
                _original_video_link_url=topic_dict['url'])

        return lstr


    def extract(self, json_str, sub_number):
        """extract the topic tree information as csv

        @param[in] json_str topic tree as a json string
        @param[in] sub_number sub topic number
        """
        topic_dict = json.loads(json_str)
        # print(topic_dict)

        if ('children' not in topic_dict):
            raise RuntimeError('topic tree json data has no children.')

        sub_topic_title = topic_dict['standalone_title']

        #  1. sub:      subject (math, physic)
        #  2. nb_main:  main topic number (addition/subtraction, fraction, ...)
        #  3. nb_sub:   sub topic number
        #  4. nb_video: video title number
        #  5. sub_topic_title:
        #  6. video_title:
        #  7. d1: text translation duration time
        #  8. d2: voice over, edit duration time
        #  9. d3: subtitle duration time
        # 10. d4: total duration time
        # 11. s1: start date
        # 12. s2: end date
        # 13. s3: elapsed date
        # 14. status:
        # 15. finished bool
        # 16. update bool
        # 17. new at 2017 bool
        # 18. video_url:
        # 19. id:

        video_idx=1
        retstr = '''
        <li>
          <div title="Sub topic">
             Subtopic Japanese
          </div>

          <ol start="">
        '''

        for i in topic_dict['children']:
            if (i['kind'] == 'Video'):
                retstr += self.__get_one_li_element(i)
                video_idx += 1
            else:
                verbose_mes = '# Skip kind [{kind}]: {title}'.format(
                    kind=i['kind'], title=i['title'])
                self.verbose_out(verbose_mes)

        retstr += '''
        </ol>
        </li>

'''

        return retstr


    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 1, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = TopicTreeExtractHTML.get_version_number()

        return '''TopicTreeExtractHTML {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-file", type=str,
                        help="Input JSON filename")

    parser.add_argument("--out-file", type=str,
                        help="Output filename")

    parser.add_argument("-v", "--verbose", type=int, action="store", default='0',
                        help="Verbose mode (0 ... off, 1 ... on")

    parser.add_argument("--force_override", action='store_true', default=False,
                        help="Even outfile is found, override the output file.")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of pogrep.py")

    args = parser.parse_args()
    assert(args.out_file is not None)

    opt_dict = {
        'verbose':        args.verbose,
    }

    if (args.version == True):
        sys.stderr.write(TopicTreeExtractHTML.get_version_string())
        sys.exit(1)

    # Switch stdout codecs to utf-8
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    # check output file exist
    if (args.force_override == False):
        if (os.path.isfile(args.out_file) == True):
            raise RuntimeError('File [{0}] already exists.'.format(args.out_file))

    # load, process, save a json string
    with open(args.in_file, encoding='utf-8', mode='r') as infile:
        in_str = infile.read()
        subtopic_number = 1
        tpe = TopicTreeExtractHTML(opt_dict)
        out_str = tpe.extract(in_str, subtopic_number)
        with open(args.out_file, encoding='utf-8', mode='w') as outfile:
            outfile.write(out_str)


if __name__ == "__main__":
    try:
        main()
        sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
