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
from six.moves import zip
from collections import Counter, defaultdict
import subprocess
import itertools

from smart_open import smart_open
from sqlitedict import SqliteDict


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class AnnotationInterface(object):
    """Access to stored annotations.
    """
    def __init__(self, source_data, db):
        """

        """
        # process current records in db
        self.db = SqliteDict(db, autocommit=True)

        # process csv file
        with smart_open(source_data) as h:
            self.data = []
            fields = h.readline().strip().split(',')
            required_fields = ['task_id', 'model_id', 'topic_no', 'task', 'answer']
            if fields != required_fields:
                raise ValueError('invalid csv file: %s does not match %s' % (fields, required_fields))
            for line in h.readlines():
                record = dict(zip(fields, line.strip().split(',')))
                self.data.append(record)

    @staticmethod
    def key(record):
        return '-'.join([record['task_id'], record['model_id'], record['topic_no'], record['user']])

    def agreement(self):
        stats = defaultdict(list)
        users_agree = defaultdict(int)
        users_disagree = defaultdict(int)
        users_skip = defaultdict(int)
        for key, value in self.db.iteritems():
            task_id, model_id, topic_no, user = key.split('-')
            stats[(task_id, model_id, topic_no)].append((user, value['annotation']))

        for recs in stats.values():
            c = Counter([a for u, a in recs if '?' not in a and '!' not in a])
            for user, answer in recs:
                freq = c.get(answer, 0)
                if freq == 0:
                    users_skip[user] += 1
                elif freq == 1:
                    users_disagree[user] += 1
                else:
                    users_agree[user] += 1
        all_users = set(users_agree.keys()).union(users_disagree.keys()).union(users_skip.keys())
        results = {}
        for user in all_users:
            results[user] = (users_agree.get(user, 0), users_disagree.get(user, 0), users_skip.get(user, 0))
        return results

    def score(self):
        stats = defaultdict(list)
        for key, value in self.db.iteritems():
            task_id, model_id, topic_no, user = key.split('-')
            stats[(task_id, model_id, topic_no)].append(value['answer'] == value['annotation'])
        ok, fail = 0, 0
        for recs in stats.values():
            if Counter(recs).get(True, 0) > 1:
                ok += 1
            else:
                fail += 1

        return ok, fail

    def export(self):
        stats = defaultdict(list)
        for key, value in self.db.iteritems():
            task_id, model_id, topic_no, user = key.split('-')
            stats[(task_id, model_id, topic_no)].append(value)
        results = []
        for recs in stats.values():
            head = recs[0]
            print(head)
            results.append((
                head['task_id'],
                head['model_id'],
                head['topic_no'],
                head['task'],
                head['answer'],
                [r['annotation'] for r in recs]))

        return results

    def save(self, data, user_name):
        no_underscore = [key for key in data if not key.startswith('_')][0]
        record = {
            'task_id': data['_task_id'],
            'model_id': data['_model_id'],
            'topic_no': data['_topic_no'],
            'answer': data['_answer'],
            'user': user_name,
            'task': data['_task'],
            'annotation': no_underscore.replace('!', 'There is no answer!').replace('?', 'I don\'t know?')
        }
        self.db[self.key(record)] = record
        logger.info('saved %s', record)

    def get_stats(self, user_name):
        impossible, skipped, done = 0, 0, 0
        for key, value in self.db.iteritems():
            task_id, model_id, topic_no, user = key.split('-')
            if user == user_name:
                if '?' in value['annotation']:
                    skipped += 1
                elif '!' in value['annotation']:
                    impossible += 1
                else:
                    done += 1
        return {'skipped': skipped, 'done': impossible + done}

    def get(self, user_name):
        user_stats = defaultdict(list)
        answer_stats = defaultdict(list)
        for key, value in self.db.iteritems():
            task_id, model_id, topic_no, user = key.split('-')
            user_stats[(task_id, model_id, topic_no)].append(user)
            answer_stats[(task_id, model_id, topic_no)].append(value['annotation'])

        selected = None
        for data in self.data:
            users = user_stats.get((data['task_id'], data['model_id'], data['topic_no']), [])
            done = answer_stats.get((data['task_id'], data['model_id'], data['topic_no']), [])
            if user_name not in users and len(done) == len(set(done)):
                selected = data
                break
        return selected

