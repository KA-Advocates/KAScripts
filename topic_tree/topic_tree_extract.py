#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief extract information tpic tree
#
# Usecase:
#
#
# Example:
#    Simple example
#      ./topic_tree_extract.py --verbose 1 --out-type ${OUTTYPE} --in-file ${INFILE} --out-file ${OUTFILE}
#
#
import argparse, sys, re, codecs, os, json
import topic_tree_extract_factory

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-file", type=str,
                        help="Input JSON filename")

    parser.add_argument("--out-file", type=str,
                        help="Output filename")

    known_out_type = topic_tree_extract_factory.get_known_topic_tree_extractor_name_list()
    parser.add_argument("--out-type", type=str,
                        choices=known_out_type, default="csv",
                        help="Output type")

    parser.add_argument("-v", "--verbose", type=int, action="store", default='0',
                        help="Verbose mode (0 ... off, 1 ... on")

    parser.add_argument("--force_override", action='store_true', default=False,
                        help="Even outfile is found, override the output file.")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of pogrep.py")

    args = parser.parse_args()

    if (args.out_type is None):
        RuntimeError('need to specify --out-type.')

    if (args.out_type not in known_out_type):
        RuntimeError('Unknown output type {0}.'.format(args.out_type))

    opt_dict = {
        'verbose':        args.verbose,
    }

    tpe = topic_tree_extract_factory.topic_tree_extract_factory(args.out_type, opt_dict)

    if (args.version == True):
        sys.stderr.write(tpe.get_version_string())
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
        out_str = tpe.extract(in_str, subtopic_number)
        with open(args.out_file, encoding='utf-8', mode='w') as outfile:
            outfile.write(out_str)


if __name__ == "__main__":
    try:
        main()
        sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
