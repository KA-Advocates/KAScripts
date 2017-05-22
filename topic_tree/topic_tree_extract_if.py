#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief extract information (reformat) tpic tree's one json string, interface.
#
#

class TopicTreeExtractIF(object):
    """Khan academy topic tree information extractror from a topic tree JSON file.
    Interface class.

    JSON format is very useful to deta conversion. But what kind of
    data format will be used is depends on the use case. Thus I made
    this as an interface. The user should implement the format
    converter accoring to the own usage.
    """

    def __init__(self, opt_dict):
        """constructor
        """
        self.__opt_dict   = opt_dict
        self.__is_verbose = opt_dict['verbose']


    def verbose_out(self, mes):
        """verbose output if self.__is_verbose is True
        """
        if (self.__is_verbose == True):
            print(mes)


    def extract(self, json_str, sub_number):
        """Extract string from an sub topic in json_str. This is an interface
        method, so it should not be called.

        @param[in] json_str topic tree as a json string
        @param[in] sub_number sub topic number
        @return extracted string

        """
        assert(False)
        return ''

