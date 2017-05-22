#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief topic tree extractor factory
#
#

import topic_tree_extract_cvs, topic_tree_extract_html

def get_known_topic_tree_extractor_name_list():
    """Returns known topic tree extractor names
    """
    known_name_list = [
        'cvs',
        'html',
    ]

    return known_name_list


def topic_tree_extract_factory(extractor_name, opt_dict):
    """Topic tree extractor factory

    @param[in] extractor_name extractor name
    @param[in] opt_dict       option dictionary for each extractor
    @return extractor instanece
    """

    known_name_list = get_known_topic_tree_extractor_name_list()

    if (extractor_name is None):
        raise RuntimeError('extractor_name is None.')

    if (extractor_name not in known_name_list):
        raise RuntimeError('Unknown topic tree extractor name: {0}'.format(extractor_name))

    tte = None
    if   (extractor_name == 'cvs'):
        tte = topic_tree_extract_cvs.TopicTreeExtractCVS(opt_dict)
    elif (extractor_name == 'html'):
        tte = topic_tree_extract_html.TopicTreeExtractHTML(opt_dict)
    else:
        raise RuntimeError('Cannot instanciate: {0}'.format(extractor_name))

    return tte
