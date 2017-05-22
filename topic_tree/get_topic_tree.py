#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief get tpic tree json file from the KA site
#
# Usecase:
#
#
# Example:
#    Simple example
#       ./get_topic_tree.py --out-file ka_topic.json
#
#
import argparse, sys, re, codecs, os, json
import urllib.request
import topic_tree_extract_factory

class GetTopicTree(object):
    """Get Khan academy topic tree as a JSON file

    https://www.khanacademy.org/api/v1/topic/${node_slug}
    node_slug: root, topictree, math, arithmetic, arith-review-negative-numbers
    arith-review-negative-numbers, fraction-arithmetic


    """

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict   = opt_dict
        assert('top_node_slug' in self.__opt_dict)
        # print('# top_node_slug: ' + self.__opt_dict['top_node_slug'])
        self.__is_verbose = opt_dict['verbose']


    def __verbose_out(self, mes):
        """verbose output if self.__is_verbose is True
        """
        if (self.__is_verbose == True):
            print(mes)

    def __get_node_slug_url(self, node_slug_str):
        """get Khan academy topic tree node URL with node_slug_str

        @param[in] node_slug_str node slug string
        @return khan academy topic tree API url
        """
        return 'https://www.khanacademy.org/api/v1/topic/' + node_slug_str


    def __get_and_process_leaf(self, leaf_node_slug, subtopic_idx):
        """
        Get the topic tree leaf node json file and process it

        @param[in] leaf_node_slug leaf node slug
        @param[in] subtopic_idx   current tsubtopic index
        """
        leaf_url = self.__get_node_slug_url(leaf_node_slug)
        self.__verbose_out('# accessing the leaf node: {0}'.format(leaf_url))

        with urllib.request.urlopen(leaf_url) as leaf_response:
            self.__verbose_out('# accessing: {0}'.format(leaf_url))
            leaf_json_str = leaf_response.read().decode('utf-8')

            ext_opt_dict = {
                'verbose': self.__opt_dict['verbose']
            }
            # FIXME HITOSHI html
            assert('out_type' in self.__opt_dict)
            assert(self.__opt_dict['out_type'] is not None)
            tpe = topic_tree_extract_factory.topic_tree_extract_factory(self.__opt_dict['out_type'], ext_opt_dict)
            out_str = tpe.extract(leaf_json_str, subtopic_idx)
            return out_str


    def get_topic_tree(self):
        """get the topic tree"""

        top_url = self.__get_node_slug_url(self.__opt_dict['top_node_slug'])
        assert(top_url is not None)
        self.__verbose_out('# accessing the top node: {0}'.format(top_url))
        with urllib.request.urlopen(top_url) as top_response:
            # Needed decode(). read() returns binary because urlopen doesn't know the encoding.
            top_json_str = top_response.read().decode('utf-8')
            # self.__verbose_out('# top level json: {0}'.format(top_json_str))

            top_dict = json.loads(str(top_json_str))
            if ('children' not in top_dict):
                raise RuntimeError('topic tree json data has no children.')

            subtopic_idx = 1
            result_str = ''
            for item in top_dict['children']:
                if (item['kind'] != 'Topic'):
                    raise RuntimeError('The (assumed) leaf level is not a Topic.')

                leaf_node_slug = item['node_slug']
                self.__verbose_out('# Look up the leaf. node_slug: {0}'.format(leaf_node_slug))
                result_str += self.__get_and_process_leaf(leaf_node_slug, subtopic_idx)
                subtopic_idx += 1

            # self.__verbose_out('# result: {0}'.format(result_str))
            return result_str


    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 1, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = GetTopicTree.get_version_number()

        return '''GetTopicTree.py {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])




def main():
    """This is test code. The tool's main is topic_tree_extract.py"""
    parser = argparse.ArgumentParser()

    parser.add_argument("--top-node-slug", type=str,
                        help="Specify the top node slug of the topic. "
                        "This node slug should be the subtopic level. e.g., fraction-arithmetic.")

    parser.add_argument("--out-file", type=str,
                        help="Output filename")


    known_out_type = topic_tree_extract_factory.get_known_topic_tree_extractor_name_list()
    parser.add_argument("--out-type", type=str,
                        choices=known_out_type, default="csv",
                        help="Output file type (extractor type)")

    parser.add_argument("-v", "--verbose", type=int, action="store", default='0',
                        help="Verbose mode (0 ... off, 1 ... on")

    parser.add_argument("--force_override", action='store_true', default=False,
                        help="Even outfile is found, override the output file.")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of pogrep.py")

    args = parser.parse_args()

    if (args.version == True):
        sys.stderr.write(GetTopicTree.get_version_string())
        sys.exit(1)

    opt_dict = {
        'top_node_slug':  args.top_node_slug,
        'out_type':       args.out_type,
        'verbose':        args.verbose,
    }

    # check output file exist
    if (args.force_override == False):
        if (os.path.isfile(args.out_file) == True):
            raise RuntimeError('File [{0}] already exists.'.format(args.out_file))

    # Switch stdout codecs to utf-8
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    gtp     = GetTopicTree(opt_dict)
    ret_str = gtp.get_topic_tree()

    with open(args.out_file, encoding='utf-8', mode='w') as outfile:
        outfile.write(ret_str)



if __name__ == "__main__":
    try:
        main()
        sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))


