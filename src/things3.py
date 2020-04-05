#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simple read-only API for Things 3."""

from __future__ import print_function

__author__ = "Alexander Willner"
__copyright__ = "2020 Alexander Willner"
__credits__ = ["Alexander Willner"]
__license__ = "Apache"
__version__ = "2.0.0"
__maintainer__ = "Alexander Willner"
__email__ = "alex@willner.ws"
__status__ = "Development"

import sqlite3
from os.path import expanduser
from os import environ


class Things3():
    """Simple read-only API for Things 3."""
    # Variables
    database = None
    cursor = None
    json = False
    tag_waiting = "Waiting" if not environ.get('TAG_WAITING') \
        else environ.get('TAG_WAITING')
    tag_mit = "MIT" if not environ.get('TAG_MIT') \
        else environ.get('TAG_MIT')

    # Database info
    FILE_SQLITE = '~/Library/Containers/'\
                  'com.culturedcode.ThingsMac.beta/Data/Library/'\
                  'Application Support/Cultured Code/Things/Things.sqlite3'\
        if not environ.get('THINGSDB') else environ.get('THINGSDB')
    TASKTABLE = "TMTask"
    AREATABLE = "TMArea"
    TAGTABLE = "TMTag"
    TASKTAGTABLE = "TMTaskTag"
    ISNOTTRASHED = "TASK.trashed = 0"
    ISTRASHED = "TASK.trashed = 1"
    ISOPEN = "TASK.status = 0"
    ISNOTSTARTED = "TASK.start = 0"
    ISCANCELLED = "TASK.status = 2"
    ISCOMPLETED = "TASK.status = 3"
    ISSTARTED = "TASK.start = 1"
    ISPOSTPONED = "TASK.start = 2"
    ISTASK = "TASK.type = 0"
    ISPROJECT = "TASK.type = 1"
    ISHEADING = "TASK.type = 2"
    ISOPENTASK = ISTASK + " AND " + ISNOTTRASHED + " AND " + ISOPEN

    # Query Index
    I_UUID = 0
    I_TITLE = 1
    I_CONTEXT = 2
    I_CONTEXT_UUID = 3
    I_DUE = 4

    def __init__(self,
                 database=FILE_SQLITE,
                 tag_waiting='Waiting',
                 tag_mit='MIT',
                 json=False):
        self.database = expanduser(database)
        self.tag_mit = tag_mit
        self.tag_waiting = tag_waiting
        self.cursor = sqlite3.connect(self.database).cursor()
        self.json = json

    def get_inbox(self):
        """Get all tasks from the inbox."""
        query = self.ISOPENTASK + " AND " + self.ISNOTSTARTED + \
            " ORDER BY TASK.duedate DESC , TASK.todayIndex"
        return self.get_rows(query)

    def get_today(self):
        """Get all tasks from the today list."""
        query = self.ISOPENTASK + " AND " + self.ISSTARTED + \
            " AND TASK.startdate is NOT NULL" + \
            " ORDER BY TASK.duedate DESC , TASK.todayIndex"
        return self.get_rows(query)

    def get_someday(self):
        """Get someday tasks."""
        query = self.ISOPENTASK + " AND " + self.ISPOSTPONED + \
            " AND TASK.startdate IS NULL AND TASK.recurrenceRule IS NULL" + \
            " ORDER BY TASK.duedate DESC, TASK.creationdate DESC"
        return self.get_rows(query)

    def get_upcoming(self):
        """Get upcoming tasks."""
        query = self.ISOPENTASK + " AND " + self.ISPOSTPONED + \
            " AND (TASK.startDate NOT NULL " + \
            "      OR TASK.recurrenceRule NOT NULL)" + \
            " ORDER BY TASK.startdate, TASK.todayIndex"
        return self.get_rows(query)

    def get_waiting(self):
        """Get waiting tasks."""
        query = self.ISOPENTASK + \
            " AND TAGS.tags=(SELECT uuid FROM " + self.TAGTABLE + \
            " WHERE title='" + self.tag_waiting + "')" + \
            " ORDER BY TASK.duedate DESC , TASK.todayIndex"
        return self.get_rows(query)

    def get_mit(self):
        """Get most important tasks."""
        query = self.ISOPENTASK + " AND " + self.ISSTARTED + \
            " AND PROJECT.status = 0 " \
            " AND TAGS.tags=(SELECT uuid FROM " + self.TAGTABLE + \
            " WHERE title='" + self.tag_mit + "')" + \
            " ORDER BY TASK.duedate DESC , TASK.todayIndex"
        return self.get_rows(query)

    def get_anytime(self):
        """Get anytime tasks."""
        query = self.ISOPENTASK + " AND " + self.ISSTARTED + \
            " AND TASK.startdate is NULL" + \
            " AND (TASK.area NOT NULL OR TASK.project in " + \
            "(SELECT uuid FROM " + self.TASKTABLE + \
            " WHERE uuid=TASK.project AND start=1" + \
            " AND trashed=0))" + \
            " ORDER BY TASK.duedate DESC , TASK.todayIndex"
        return self.get_rows(query)

    @staticmethod
    def get_not_implemented():
        """Not implemented warning."""
        return [["0", "not implemented", "no context", "0", "0"]]

    def get_rows(self, sql):
        """Query Things database."""

        sql = """
            SELECT DISTINCT
                TASK.uuid,
                TASK.title,
                CASE
                    WHEN AREA.title IS NOT NULL THEN AREA.title
                    WHEN PROJECT.title IS NOT NULL THEN PROJECT.title
                    WHEN HEADING.title IS NOT NULL THEN HEADING.title
                END,
                CASE
                    WHEN AREA.uuid IS NOT NULL THEN AREA.uuid
                    WHEN PROJECT.uuid IS NOT NULL THEN PROJECT.uuid
                END,
                CASE
                    WHEN TASK.recurrenceRule IS NULL
                    THEN date(TASK.dueDate,"unixepoch")
                ELSE NULL
                END
            FROM
                TMTask AS TASK
            LEFT JOIN
                TMTaskTag TAGS ON TAGS.tasks = TASK.uuid
            LEFT OUTER JOIN
                TMTask PROJECT ON TASK.project = PROJECT.uuid
            LEFT OUTER JOIN
                TMArea AREA ON TASK.area = AREA.uuid
            LEFT OUTER JOIN
                TMTask HEADING ON TASK.actionGroup = HEADING.uuid
            WHERE """ + sql
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def convert_task_to_model(self, task):
        """Convert task to model."""
        model = {'uuid': task[self.I_UUID],
                 'title': task[self.I_TITLE],
                 'context': task[self.I_CONTEXT],
                 'context_uuid': task[self.I_CONTEXT_UUID],
                 'due': task[self.I_DUE],
                 }
        return model

    def convert_tasks_to_model(self, tasks):
        """Convert tasks to model."""
        model = []
        for task in tasks:
            model.append(self.convert_task_to_model(task))
        return model
