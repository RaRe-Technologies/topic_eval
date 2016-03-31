#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Jan Rygl <jimmy@rare-technologies.com>
# Copyright (C) 2016 RaRe Technologies

"""Evaluation functions. Work with annotations.
Used by HTTP server.
"""


import os
import json
import sys
import logging
import random
from collections import Counter, defaultdict
import subprocess
import itertools
import time

from smart_open import smart_open
from sqlitedict import SqliteDict

from config import relative_path, absolute_path


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def relative_annotation_db():
    """Get handler of sqlite object where relative annotations are stored.
    """
    logger.info('accessing relative db')
    return SqliteDict(relative_path, autocommit=False)


def absolute_annotation_db():
    """Get handler of sqlite object where absolute annotations are stored.
    """
    logger.info('accessing absolute db')
    return SqliteDict(absolute_path, autocommit=False)


def abs_to_rel():
    dbr = relative_annotation_db()
    dba = absolute_annotation_db()
    database = defaultdict(dict)
    query_dict = {}
    for key, job_listing_annotations in dba.iteritems():
        query = job_listing_annotations['id']
        qt = job_listing_annotations['title']
        qd = job_listing_annotations['description']
        query_dict[query] = (qt, qd)
        col_id = job_listing_annotations['collection_id']
        col_title = job_listing_annotations['collection_title']
        for annotation in job_listing_annotations['data']:
            user = annotation['username']
            answer = annotation['answer']
            if answer == 'skip' or answer == 'not_enough_information':
                continue
            database[query].setdefault(user, [])
            database[query][user].append((col_id, col_title, answer, annotation['algorithm']))

    def to_score(label1, label2):
        trans = {
            'specific&matching': 10,
            'general&matching': 5,
            'slightly_non-matching': 1,
            'non-matching': 0
            }
        sc1, sc2 = trans[label1], trans[label2]
        if sc1 > sc2:
            return 'left'
        elif sc1 < sc2:
            return 'right'
        elif sc1 == sc2 and sc1 == 10:
            return 'equal'
        else:
            return 'bad'

    for query, users in database.iteritems():
        for user, records in users.iteritems():
            if len(records) > 1:
                for (id1, t1, score1, a1), (id2, t2, score2, a2) in itertools.combinations(records, 2):
                    if id1 == id2:
                        continue
                    answer = to_score(score1, score2)
                    job_listing_annotations = dbr.get(query)
                    if job_listing_annotations:
                        present = False
                        answers = []
                        algorithms = (a1, a2)
                        for annotation in job_listing_annotations['data']:
                            if annotation['username']:
                                if annotation['left'][0] == id1 and annotation['right'][0] == id2:
                                    present = True
                                elif annotation['left'][0] == id2 and annotation['right'][0] == id1:
                                    present = True
                            if present:
                                if annotation['left'] == id2:
                                    if answer == 'left':
                                        answer = 'right'
                                    elif answer == 'right':
                                        answer = 'left'
                                answers.append(annotation['answer'])
                        if not present or answer not in answers:
                            new_rec = {
                                'username': user,
                                'left': (id1, t1),
                                'right': (id2, t2),
                                'time': time.strftime('%Y-%M-%d %H:%I:%S'),
                                'answer': answer,
                                'algorithms': algorithms,
                                'automatic': True
                                }
                            job_listing_annotations['data'].append(new_rec)
                            dbr[query] = job_listing_annotations
                            logger.info('new record', new_rec)
                            dbr.commit()
                    else:
                        job_listing_annotations = {}
                        job_listing_annotations['id'] = query
                        job_listing_annotations['title'] = query_dict[query][0]
                        job_listing_annotations['description'] = query_dict[query][1]
                        new_rec = {
                            'username': user,
                            'left': (id1, t1),
                            'right': (id2, t2),
                            'time': time.strftime('%Y-%M-%d %H:%I:%S'),
                            'answer': answer,
                            'algorithms': algorithms,
                            'automatic': True
                            }
                        job_listing_annotations['data'] = [new_rec]
                        dbr[query] = job_listing_annotations
                        logger.info('new query record', new_rec)
                        dbr.commit()


def obtain(output, json_file, remove_equal=True, allow_one_annotated=True):
    """Create export file using params.

    :param output: base path to file
    :param json_file: file with queries and labels
    :param remove_equal: True/False, is equal same as bad?
    :param allow_one_annotated: True/False, see annotations by one person
    """
    dbr = relative_annotation_db()
    result = '%s_%s_%s' % (
        output,
        'equal-is-bad' if remove_equal else 'equal-is-allowed',
        'allow-1annotated' if allow_one_annotated else '2more-agreement')

    with smart_open(json_file) as h:
        pred_raw = json.loads(h.read())
        jobs = pred_raw['job_titles']
        collections = pred_raw['collections']
        col_titles = dict([(col['id'], col['title']) for col in collections])
        predefined = dict()
        for job in jobs:
            record = {
                'collection_id': job['collection'],
                'collection_title': col_titles[job['collection']] if job['collection'] else ''
                }
            predefined[job['id']] = record

    hw = smart_open(result, 'w')
    for key, job_listing_annotations in dbr.iteritems():
        query = job_listing_annotations['id']
        if query not in predefined:
            continue
        label_collection = predefined[query]['collection_id']
        label_collection_title = predefined[query]['collection_title']

        decisions = []
        dec_labels = []
        for annotation in job_listing_annotations['data']:
            left = annotation['left'][0]
            right = annotation['right'][0]
            answer = annotation['answer']
            if label_collection not in [left, right]:
                continue
            elif (left == label_collection and answer == 'left') or (right == label_collection and answer == 'right'):
                decisions.append(True)
            elif left == label_collection and answer == 'right':
                decisions.append(right)
                dec_labels.append(annotation['right'][1])
            elif right == label_collection and answer == 'left':
                decisions.append(left)
                dec_labels.append(annotation['left'][1])
            elif answer in ('bad', 'equal'):
                decisions.append(answer)
        if len(decisions) == 0:
            continue
        elif len(decisions) == 1:
            answer = decisions[0]
            if allow_one_annotated:
                if answer is True:
                    pass
                elif isinstance(answer, int):
                    hw.write(
                        '%i\t%s\t%s\n' % (query, answer, 'one annotation, %s=>%s' % (
                            label_collection_title, dec_labels[0])))
                elif answer == 'bad':
                    hw.write(
                        '%i\t\t%s\n' % (query, 'one annotation, %s=>-' % label_collection_title))
                elif remove_equal and answer == 'equal':
                    hw.write('%i\t\t%s\n' % (
                        query, 'one annotation, equal is bad, %s=>-' % label_collection_title))
        else:
            stats = Counter(decisions)
            if max(stats.values()) == 1:
                continue
            else:
                goal = max(stats.values())
                for stat, freq in stats.iteritems():
                    if freq == goal:
                        answer = stat
                        if answer is True:
                            pass
                        elif isinstance(answer, int):
                            hw.write(
                                '%i\t%s\t%s\n' % (query, answer, '%i annotation, %s=>%s' % (
                                    freq, label_collection_title, dec_labels[0])))
                        elif answer == 'bad':
                            hw.write('%i\t\t%s\n' % (
                                query, '%i annotation, %s=>-' % (freq, label_collection_title)))
                        elif remove_equal and answer == 'equal':
                            hw.write('%i\t\t%s\n' % (
                                query, '%i annotation, equal is bad, %s=>-' % (freq, label_collection_title)))
                        break


if __name__ == '__main__':
    abs_to_rel()
    for eq in (True, False):
        for one in (True, False):
            obtain('./data/export', './data/data.json.gz', eq, one)
