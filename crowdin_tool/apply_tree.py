#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2015-2016 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
"""Get all msgid == msgstr under a directory"""

import os, sys, argparse, subprocess

class Extract_same(object):
    """Get all msgid == msgstr under a directory"""

    def __init__(self, opt_dict):
        """constructor
        Options:

        """
        self.__opt_dict = opt_dict;
        self.__src_dir  = opt_dict['src_dir']
        self.__dst_dir  = opt_dict['dst_dir']
        assert(self.__src_dir != None)
        assert(self.__dst_dir != None)
        self.__is_dry_run = False
        if (self.__opt_dict['dry_run'] == 'on'):
            self.__is_dry_run = True
        self.__pofilter_path = "/home/hitoshi/data/project/ka/ka-advocates/KAScripts/crowdin_tool/pofilter.py"


    def __split_all_directory(self, path):
        dir_list = []
        while (True):
            (base, tail) = os.path.split(path)
            if (base == path):   # absolute path
                dir_list.append(base)
                break
            elif (tail == path): # relative path
                dir_list.append(tail)
                break
            else:
                path = base
                dir_list.append(tail)

        dir_list.reverse()
        return dir_list


    def __join_all_directory(self, path_list):
        """Join all dir list. If [], ''.
        """

        if (path_list == None):
            raise RuntimeError('path_list is None.')

        if (len(path_list) == 0):
            return ''

        return os.path.join(*path_list)


    def __remove_top_dir(self, cur_dir):
        """Remove the top most directory
        """
        dir_list = self.__split_all_directory(cur_dir)
        if (len(dir_list) > 0):
            del dir_list[0]

        top_del_dir = self.__join_all_directory(dir_list)

        return top_del_dir


    def __is_po_file(self, pofile_cand_path):
        """check the pofile_cand_path is a po file or not."""

        # Is this a regular file?
        if (not os.path.isfile(pofile_cand_path)):
            return False

        # po file?
        (basedir, ext) = os.path.splitext(pofile_cand_path)
        if (ext != '.po'):
            return False

        return True


    def __process_file(self, src_dir, src_file, dst_dir, dst_file):
        """process one file
        """

        src_fpath = os.path.join(src_dir, src_file)
        dst_fpath = os.path.join(dst_dir, dst_file)

        if (not self.__is_po_file(src_fpath)):
            print('# skip file: {0}'.format(src_fpath))
            return

        try:
            com_list = [self.__pofilter_path,
                        '-n',
                        '--tool', 'same',
                        src_fpath,
                        dst_fpath]

            print('# {0}'.format(' '.join(com_list)))
            if (self.__is_dry_run == True):
                return

            res_str = subprocess.check_output(com_list)
        except subprocess.CalledProcessError:
            print('run failed. You should not see this message.')


    def __process_dir(self, dir):
        """process a directory
        """
        if (os.path.isdir(dir) == False):
            print('# makedirs {0}'.format(dir))
            if (self.__is_dry_run == False):
                os.makedirs(dir)
        else:
            print('# makedirs {0} already exists.'.format(dir))

    def process_tree(self):
        """check the line ending of each file."""
        topdown = True

        # First scan for mkdir
        gen = os.walk(self.__src_dir, topdown)
        for (cur_dir, dir_list, file_list) in gen:
            # print(cur_dir, dir_list, file_list)
            for dir in dir_list:
                rel_dir = self.__remove_top_dir(cur_dir)
                # print('# relative dir: {0}'.format(rel_dir))
                dst_dir = os.path.join(*[self.__dst_dir, rel_dir, dir])
                self.__process_dir(dst_dir)

        # Second scan for process
        gen = os.walk(self.__src_dir, topdown)
        for (cur_dir, dir_list, file_list) in gen:
            for f in file_list:
                dir_list = self.__split_all_directory(cur_dir)
                # print(dir_list)
                assert(len(dir_list) > 0)
                del dir_list[0]

                rel_dir_path = ''
                if (len(dir_list) > 0):
                    rel_dir_path = os.path.join(*dir_list)
                src_dir = os.path.join(self.__src_dir, rel_dir_path)
                dst_dir = os.path.join(self.__dst_dir, rel_dir_path)
                self.__process_file(src_dir, f, dst_dir, f)


def main():
    """check the shell's incomde test code."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--src_dir", type=str, default='',
                        help="Source pofiles top directry")

    parser.add_argument("--dst_dir", type=str, default='',
                        help="Destination top directory")

    parser.add_argument("--dry_run", choices=['on', 'off'], default="off",
                        help="when on, not process the file, but show the command.")

    # parser.add_argument("--tool", choices=['id_to_str', 'same', 'differ', 'none'], default="id_to_str",
    #                     help="tools. id_to_str: copy msgid to msgstr. same: msgid == msgstr. differ: msgid != mgsstr")
    # parser.add_argument("-n", "--no-context", action="store_true",
    #                     help="Remove context from all strings")

    # parser.add_argument("--force_override", action='store_true',
    #                     help="Even outfile is found, override the output file.")

    args = parser.parse_args()

    if (args.src_dir == ''):
        raise RuntimeError('missing option --src_dir.')
    if (args.dst_dir == ''):
        raise RuntimeError('missing option --dst_dir.')

    opt_dict = {
        'src_dir': args.src_dir,
        'dst_dir': args.dst_dir,
        'dry_run': args.dry_run
    }

    for opt in opt_dict:
        print('# {0}: {1}'.format(opt, opt_dict[opt]))

    es = Extract_same(opt_dict)
    es.process_tree()






if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except:
        print('uncaught exception: {0} {1}'.format(sys.exc_type, sys.exc_value))

