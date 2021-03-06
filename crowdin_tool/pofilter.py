#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2015-2016 Hitoshi Yamauchi
#               2016      Uli Köhler
# New BSD License.
#******************************************************************************
# \file
# \brief Crowdin .po file filter
#
# Usecase:
#    Remove translated entries from the .po file
# Tool:
# --tool none
#        no filtering
# --tool id_to_str [DEFAULT]
#        copy msgid string to msgstr string if msgstr is empty.
# --tool same
#        Outout when msgid == mgsstr
# --tool differ
#        Outout when msgid != mgsstr
#
# Example:
#    Extract non-translated entries (keeps context)
#       ./pofilter.py sample.po -o sample.po.txt
#
#    Extract non-translated entries WITHOUT context line
#       ./pofilter.py --no-context sample.po sample.po.txt
#
import argparse, sys, re, codecs, os
import polib

def id_to_str(entry):
    """filter() function to determine if a given entry is untranslated"""
    return (not entry.msgstr and entry.msgid)


def same(entry):
    """filter() function to determine if a given msgid is the same as the msgstr"""
    return entry.msgid == entry.msgstr


def differ(entry):
    """filter() function to determine if a given msgid is different to the msgstr"""
    return entry.msgid != entry.msgstr


def replace_msgstr_by_msgid(entry):
    return polib.POEntry(**{
        "msgid": entry.msgid,
        "msgstr": entry.msgid,
        "comment": entry.tcomment, # Fix comment not being written to output file
    })


filter_tools = {
    "id_to_str": id_to_str,
    "same": same,
    "differ": differ,
    "none": lambda _: True
}


map_tools = {
    "id_to_str": replace_msgstr_by_msgid,
    "same": lambda a: a,
    "differ": lambda a: a,
    "none": lambda a: a
}


def remove_context_from_entry(entry):
    entry.comment = None
    entry.tcomment = None
    entry.occurrences = []
    return entry


def get_metadata_string(metadata_dict):
    """get metadata strings via POFile()
    """
    po = polib.POFile()
    po.metadata = metadata_dict
    metadata_str = po.__unicode__() + '\n\n'

    return metadata_str


def find_untranslated_entries(poentries, remove_context=False, tool="id_to_str"):
    """
    Read a PO file and find all untranslated entries.
    Note that polib's untranslated_entries() doesn't seem to work
    for Crowdin PO files.

    Returns a string containing the resulting PO entries
    """
    # Find untranslated strings
    untranslated = filter(filter_tools[tool], poentries)

    # Replace msgstr by msgid (because it would be empty otherwise due to POLib)
    export_entries = list(map(map_tools[tool], untranslated))

    # Remove context if enabled
    if remove_context:
        export_entries = list(map(remove_context_from_entry, export_entries))

    # Create a new PO with the entries
    result = polib.POFile()
    [result.append(entry) for entry in export_entries]

    # Generate PO string
    retstr = result.__unicode__()

    ret_lines = retstr.splitlines()

    # Removed metadata string. I could not find to remove metadata in the polib code.
    #  only metadata case ... return empty string
    if (len(ret_lines) <= 3):
        return ''
    #  non metadata found
    if ((ret_lines[0] == '#') and         (ret_lines[1] == 'msgid ""') and \
        (ret_lines[2] == 'msgstr ""') and (ret_lines[3] == '')):
        retstr = '\n'.join(ret_lines[4:])

    return retstr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str,
                        help="Input PO/POT file")

    parser.add_argument("outfile", type=str, default="-", nargs="?",
                        help="Output filename (- is stdout)")

    parser.add_argument("--metadata", choices=['always', 'add', 'off'], default="add",
                        help="Output metadata. If always, always output even body is empty. add will add when body is not empty.")

    parser.add_argument("--tool", choices=['id_to_str', 'same', 'differ', 'none'], default="id_to_str",
                        help="tools. id_to_str: copy msgid to msgstr. same: msgid == msgstr. differ: msgid != mgsstr")
    parser.add_argument("-n", "--no-context", action="store_true",
                        help="Remove context from all strings")

    parser.add_argument("--force_override", action='store_true',
                        help="Even outfile is found, override the output file.")

    args = parser.parse_args()

    # load pofile
    poentries = polib.pofile(args.infile, encoding='utf-8')

    body_str = find_untranslated_entries(poentries, args.no_context, args.tool)

    postr = ''
    if (args.metadata == 'always'):
        postr = get_metadata_string(poentries.metadata) + body_str
    elif (args.metadata == 'add'):
        if (len(body_str) > 0):
            postr = get_metadata_string(poentries.metadata) + body_str
        else:
            # no output since body_str is empty
            pass
    else:
        postr = body_str


    # Write or print to stdout
    if args.outfile == "-":
        print(postr)
    else:
        if (os.path.isfile(args.outfile) and (args.force_override == False)):
            raise RuntimeError('output file exists. If you want to force override, use --force_override option.')
        if (len(postr) > 0):
            with open(args.outfile, encoding='utf-8', mode='w') as outfile:
                outfile.write(postr)
        else:
            print('# empty result file, skip to output {0}'.format(args.outfile))

if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
