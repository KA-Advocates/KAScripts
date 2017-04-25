#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief apply diff in the key to the value of Crowdin .po files
#
# Usecase:
#
#
# Example:
#    Simple example
#       ./diffapply.py --in-old-file old.po --in-new-file new.po --out-file out.po
#
#
import argparse, sys, re, codecs, os, difflib
import polib

import tokensplit

class DiffApply(object):
    """Apply heuristics from the difference of sources (msgid) on to translations (msgstr)
    """

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict   = opt_dict
        self.__is_verbose = opt_dict['verbose']
        self.__ratio_threshold = 0.7

        # init for pofile old and new input
        self.__po_old_in = None
        self.__po_new_in = None

        # DELETEME print(self.__opt_dict)

        for key in ['out_new_file', 'out_old_file' ]:
            if ((self.__opt_dict[key] is None) or (self.__opt_dict[key] == '')):
                raise RuntimeError('invalid {0} option.'.format(key))
            # check exist when ! force override
            if (self.__opt_dict['force_override'] == False):
                if (os.path.isfile(self.__opt_dict[key]) == True):
                    raise RuntimeError('File [{0}] already exists.'.format(self.__opt_dict[key]))


        # Switch stdout codecs to utf-8
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

        # Use parse line splitter
        token_split_opt = {
            'verbose': self.__is_verbose,
        }
        self.__token_splitter = tokensplit.TokenSplit(token_split_opt)

        # some precompiled pattern
        self.__re_ws_comp = re.compile('[ \t\n]*')


    def __verbose_out(self, mes):
        """verbose output if self.__is_verbose is True
        """
        if (self.__is_verbose == True):
            print(mes)



    def __load_pofile(self):
        """Load pofiles
        Load an old pofile and an new pofile
        """
        # load pofile
        in_old_file_name = self.__opt_dict['in_old_file']
        self.__verbose_out('# Loading {0}'.format(in_old_file_name))
        self.__po_old_in = polib.pofile(in_old_file_name, encoding='utf-8')
        self.__verbose_out('# Done loading. # of entries: {0}'.format(len(self.__po_old_in)))

        in_new_file_name = self.__opt_dict['in_new_file']
        self.__verbose_out('# Loading {0}'.format(in_new_file_name))
        self.__po_new_in = polib.pofile(in_new_file_name, encoding='utf-8')
        self.__verbose_out('# Done loading. # of entries: {0}'.format(len(self.__po_new_in)))


    def __remove_entry_by_msgstr(self, update_pofile, is_remove_when_exist):
        """remove POFile entry depends on msgstr status

        @param[in,out] update_pofile updating pofile
        @param[in]     is_remove_when_exist when true, remove when translation exist,
                       otherwise remove when translation not exist
        """
        assert(update_pofile != None)
        assert(len(update_pofile) > 0)

        # process backwords due to del operation
        nb_original = len(update_pofile)
        for idx in range(len(update_pofile) - 1, -1, -1):
            if (update_pofile[idx].msgstr != '') == is_remove_when_exist:
                # print('deleting:\n' + '\tmagid:[' + update_pofile[idx].msgid + ']\n' +\
                #       '\tmagstr:['   + update_pofile[idx].msgstr + ']\n')
                del update_pofile[idx]

        self.__verbose_out('# Removed {0} entries which has {2} translation. Remaining entries: {1}'.format(
            nb_original - len(update_pofile), len(update_pofile), 'a' if is_remove_when_exist else 'no'))


    def __get_str_to_line_base(self, str):
        """get string with separated by lines
        Lines are separated white spaces, math equations.
        """
        pass



    def __gen_apply_to_msgstr(self, closest_ent, new_ent):
        """generate diff opecodes between closest_ent and new_ent and
        analyze and apply them to closest entry's msgdtr
        """
        pass


    def __print_opcodes(self, smat, old_str, new_str):
        """print SequenceMatcher object opecodes
        @param[in] smat sequence matcher object
        @param[in] old_str old string
        @param[in] new_str new string
        """
        for tag, i1, i2, j1, j2 in smat.get_opcodes():
            print('# {:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
                tag, i1, i2, j1, j2, old_str[i1:i2], new_str[j1:j2]))


    def __get_closest(self, ent_new, pofile, is_translation):
        """get the closest msgid entry

        @param[in] ent_new a new pofile entry
        @param[in] pofile  pofile for search
        @param[in] is_translation when True, only search with the translation in pofile entry
        @return    closest match, None when all are less than self.__ratio_threshold.
        """
        max_ent   = None
        max_ratio = 0.0
        for ent in pofile:
            if (is_translation == True):
                if (ent.msgstr == ''):
                    continue

            smat = difflib.SequenceMatcher(None, ent_new.msgid, ent.msgid)
            # print('# test:{2}\n# {0}\n# {1}'.format(ent_new.msgid, ent.msgid, s.quick_ratio()))

            if (smat.quick_ratio() > self.__ratio_threshold): # quick filter
                r = smat.ratio()
                if (r > self.__ratio_threshold): # real filter
                    if (max_ratio < r):
                        max_ratio = r
                        max_ent   = ent

        if (max_ent is not None):
            print('# closest r: {2}\n# old: {0}\n# new: {1}'.format(max_ent.msgid, ent_new.msgid, max_ratio))
        else:
            print('# src: {0}, no close match'.format(ent_new.msgid))

        return max_ent

    def __process_identical(self, ent_new, ent_closest):
        """Process the case identical old.msgid == new.msgid,
        The new one has no translation. The old one has a translation
        Update the ent_new.msgstr
        @return true when this is processed
        """
        if (ent_new.msgid == ent_closest.msgid):
            ent_new.msgstr = ent_closest.msgstr
            ent_new.msgstr = ent_closest.msgstr
            self.__verbose_out('# found identical msgid')
            return True
        return False


    def __is_sequence_match_ws_diff_only(self, smat, old_str, new_str):
        """check whether intrinsic white space change only
        """

        for tag, i1, i2, j1, j2 in smat.get_opcodes():
            # print('# {:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
            #     tag, i1, i2, j1, j2, old_str[i1:i2], new_str[j1:j2]))
            old_diff = old_str[i1:i2]
            new_diff = new_str[j1:j2]

            if (tag == 'equal'):
                # no change
                # print('# skip equal: {0}'.format(old_diff))
                continue
            elif ((tag == 'replace') or (tag == 'delete') or (tag == 'insert')):
                if ((self.__re_ws_comp.fullmatch(old_diff) is not None) and
                    (self.__re_ws_comp.fullmatch(new_diff) is not None)):
                    # print('# full match: [{0}] -> [{1}]'.format(old_diff, new_diff))
                    continue
                else:
                    # print('# not full match: [{0}] -> [{1}]'.format(old_diff, new_diff))
                    return False
            else:
                assert(False)

        # all ws
        # print('# complete full match')
        return True



    def __process_intrinsic_white_space(self, ent_new, ent_closest):
        """Process the case only intrinsic white space diff
        """
        is_ws = lambda x: x in " \t"
        smat = difflib.SequenceMatcher(isjunk=is_ws, a=ent_closest.msgid, b=ent_new.msgid)

        print(smat.ratio())

        self.__print_opcodes(smat, ent_closest.msgid, ent_new.msgid)

        if (self.__is_sequence_match_ws_diff_only(smat, ent_closest.msgid, ent_new.msgid) == True):
            # intrinsic white space change only. Just copy and do not care the change
            ent_new.msgstr    = ent_closest.msgstr
            if (ent_new.tcomment != ''):
                ent_new.tcomment += '\n'
            ent_new.tcomment += 'diffapply: intrinsic white space change only, use old translation.'
            self.__verbose_out('# intrinsic white space change only, use old translation.')
            return True

        self.__verbose_out('# not full match the diff with intrinsic white space.')
        return False



    def __diff_apply_each(self, ent_new):
        """for all the entries
        find diff and apply the diff
        """

        # find closest in old pofile
        is_translation = True
        closest_ent = self.__get_closest(ent_new, self.__po_old_in, is_translation)

        if closest_ent is None:
            return              # skip this entry

        # case identical
        if (self.__process_identical(ent_new, closest_ent) == True):
            return              # done

        # case intrinsic white space diff
        if (self.__process_intrinsic_white_space(ent_new, closest_ent) == True):
            pass



        # # analyse msgstr in old entry and replace it
        # # print(closest_ent)
        # new_msgid_list      = self.__token_splitter.split(ent_new.msgid)
        # closest_msgid_list  = self.__token_splitter.split(closest_ent.msgid)
        # closest_msgstr_list = self.__token_splitter.split(closest_ent.msgstr)



        # print('# DEBUG ==================================================')
        # for str in new_msgid_list:
        #     print(str)

        # print('# DEBUG ==================================================')
        # for str in closest_msgid_list:
        #     print(str)

        # print('# DEBUG ==================================================')
        # for str in closest_msgstr_list:
        #     print(str)

        # print('# DEBUG ==================================================')

        # analyse msgid diff and apply them to msgstr
        # self.__gen_apply_to_msgstr(closest_ent, ent_new)


    def __diff_apply_all(self):
        """for all the entries
        find diff and apply the diff
        """
        for ent_new in self.__po_new_in:
            self.__diff_apply_each(ent_new)



    def run(self):
        """run the diff and apply"""

        self.__load_pofile()
        self.__remove_entry_by_msgstr(self.__po_new_in, True)
        # self.__remove_entry_by_msgstr(self.__po_old_in, False)

        self.__diff_apply_all()

        if (self.__opt_dict['force_override'] == False):
            for key in ['out_new_file', 'out_old_file' ]:
                if (os.path.isfile(self.__opt_dict[key]) == True):
                    raise RuntimeError('File [{0}] exists, --force-override?'.format(self.__opt_dict[key]))

        self.__po_old_in.save(self.__opt_dict['out_old_file'])
        self.__po_new_in.save(self.__opt_dict['out_new_file'])


    @staticmethod
    def get_version_number():
        """get the version number list
        [major, minor, maintainance]
        """
        return [0, 1, 0]

    @staticmethod
    def get_version_string():
        """get version information as a string"""
        vl = DiffApply.get_version_number()

        return '''DiffApply.py {0}.{1}.{2}
New BSD License.
Copyright (C) 2017 Hitoshi Yamauchi
'''.format(vl[0], vl[1], vl[2])




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-old-file", type=str,
                        help="Input old (which has translation strings) po file")

    parser.add_argument("--in-new-file", type=str,
                        help="Input new (which doesn't have translation strings) po file")

    parser.add_argument("--out-old-file", type=str, default='up_old.po',
                        help="Output filename for updated old entries")

    parser.add_argument("--out-new-file", type=str, default='up_new.po',
                        help="Output filename for updated new entries")


    # parser.add_argument("--metadata", choices=['always', 'add', 'off'], default="add",
    #                     help="Output metadata. If always, always output even body is empty. add will add when body is not empty.")

    # parser.add_argument("--tool", choices=['id_to_str', 'same', 'differ', 'none'], default="id_to_str",
    #                     help="tools. id_to_str: copy msgid to msgstr. same: msgid == msgstr. differ: msgid != mgsstr")

    parser.add_argument("-v", "--verbose", type=int, action="store", default='0',
                        help="Verbose mode (0 ... off, 1 ... on")

    parser.add_argument("--force_override", action='store_true', default=False,
                        help="Even outfile is found, override the output file.")

    parser.add_argument("-V", "--version", action="store_true",
                        help="output the version number of pogrep.py")

    args = parser.parse_args()

    if (args.version == True):
        sys.stderr.write(DiffApply.get_version_string())
        sys.exit(1)

    opt_dict = {
        'in_old_file':    args.in_old_file,
        'in_new_file':    args.in_new_file,
        'out_old_file':   args.out_old_file,
        'out_new_file':   args.out_new_file,
        'verbose':        args.verbose,
        'force_override': args.force_override,
    }

    da = DiffApply(opt_dict)
    da.run()


if __name__ == "__main__":
    try:
        main()
        sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))
