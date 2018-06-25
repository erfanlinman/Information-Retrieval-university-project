#!/usr/bin/env python
# -*- encoding: utf8 -*-
"""parse xml file and convert them to json
    __author__ = "Erfan Rahnemoon"
    __version__ = "0.0.1"
    __maintainer__ = "Erfan Rahnemoon"
    __email__ = "erfan@rahnemoon.name"
"""
import json
import os
import re

from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import XMLParser


def read_data_files(path):
    """read xml file from path

    Arguments:
        path {string} -- path to file

    Returns:
        string -- content of file
    """

    with open(path, 'r+') as reader:
        return reader.read()


def write_json_file(path, json_data):
    """write content in json format

    Arguments:
        path {string} -- path to store json file
        json_data {dictionary} -- dictionary of data to write in json
    """

    with open(path+'.json', 'w+') as writer:
        json.dump(json_data, writer)
        writer.close()


def standardize_xml_files(file_content, recover_mode=True, encoding='utf-8'):
    """standardize Xml file for file haven't root tag

    Arguments:
        file_content {string} -- xml content has not root tag

    Keyword Arguments:
        recover_mode {bool} -- ignore error or not (default: {True})
        encoding {str} -- open file by write codec (default: {'utf-8'})

    Returns:
        string -- standard xml content
    """

    xml_tree = etree.fromstring('<root>' + file_content + '</root>',
                                parser=XMLParser(recover=recover_mode,
                                                 encoding=encoding)
                                )
    return etree.tostring(xml_tree)


def make_dic(doc_id=None, root=None, date=None,
             author=None, text=None, favorite=None):
    """make dictionary form argument and return dictionary

    Keyword Arguments:
        doc_id {int} -- documnet ID (default: {None})
        root {string} -- xml file name (default: {None})
        date {string} -- date of document (default: {None})
        author {string} -- author of document (default: {None})
        text {string} -- text of document (default: {None})
        favorite {string} -- favorite of document (default: {None})

    Returns:
        dictionary -- document  data in dictionary
    """

    return {
        'docID': doc_id,
        'root': root,
        'date': date,
        'author': author,
        'text': text,
        'favorite': favorite
    }


def make_soup(xml_tree):
    """make beautifulsoup object for interpret xml file

    Arguments:
        xml_tree {string} -- content of xml file

    Returns:
        (list,string,bool) -- return list of all doc and root name in xml file
        and check for exception files
    """

    soup = BeautifulSoup(xml_tree, 'lxml-xml')
    exception_file = False
    if soup.find('DATE') is None:
        exception_file = True
    return soup.find_all('DOC'), soup.find('DOCNO'), exception_file


def get_all_file_by_path(base_path):
    """get relative path to all XML files

    Arguments:
        base_path {string} -- base address to access to XML files

    Returns:
        dictionary -- key is directory and value is path to XML files in each
        directory
    """

    dic_file_path = {}
    for directory in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, directory)):
            dic_file_path[directory] = []
    for key in dic_file_path.iterkeys():
        path_to_files = base_path + '/' + key + '/'
        for _file in os.listdir(path_to_files):
            if os.path.isfile(os.path.join(path_to_files, _file)):
                dic_file_path[key].append(path_to_files+_file)

    return dic_file_path


def files_to_json(dic_file_path, path_store_json):
    """parse xml files to json files json files name is directory of xml files
    so all doc in one directory saved in one json file

    Arguments:
        dic_file_path {dictioanry} -- dictionary from all directory and file in
        dataset which directory is key
        path_store_json {string} -- directory to store json files
    """

    doc_id = 0
    for name_directory, list_of_path in dic_file_path.iteritems():
        list_dics_doc = []
        for path in list_of_path:
            content = read_data_files(path)
            # if for just one excepted file in dataset
            if 'DOCNO' not in content:
                pure_text = re.sub('(\\r\\n){3,5}', '', content)
                list_of_each_line = pure_text.splitlines()
                for line in list_of_each_line:
                    list_dics_doc.append(make_dic(doc_id=doc_id,
                                                  root=path.split('/')[-1],
                                                  text=line))
                    doc_id += 1
                continue

            content = standardize_xml_files(content, encoding='cp1252')
            list_docs, root_name, exception_file = make_soup(content)
            for doc in list_docs:
                # if file for excepted file in data-set
                if exception_file:
                    list_dics_doc.append(make_dic(doc_id=doc_id,
                                                  root=root_name.get_text(),
                                                  text=doc.get_text()))
                else:
                    list_dics_doc.append(make_dic(doc_id,
                                                  root_name.get_text(),
                                                  doc.DATE.get_text(),
                                                  doc.AUTHOR.get_text(),
                                                  doc.TEXT.get_text(),
                                                  doc.FAVORITE.get_text()))

                doc_id += 1
        write_json_file(path_store_json + '/' + str(name_directory),
                        list_dics_doc)


def parsing(base_source_path='data-files/cars',
            base_result_path='data-files/json_data/cars/parsed'):
    """get path to all file in data-set and run converter to json

    Keyword Arguments:
        base_source_path {str} -- path to xml files of data-set
        (default: {'data-files/cars'})
        base_result_path {str} -- path to store json files
        (default: {'data-files/json_data/cars'})
    """

    if not os.path.isdir(base_result_path):
        os.mkdir(base_result_path)
    dic_file = get_all_file_by_path(base_source_path)
    files_to_json(dic_file, base_result_path)

if __name__ == '__main__':
    parsing()
