import argparse
from datetime import datetime
import logging
import os
import re
import sqlite3
import sys

"""
Export Things 3 database to TaskPaper files

Things 3 database is typically at ~/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application Support/Cultured Code/Things/Things.sqlite3

Database Structure:

- TMArea contains areas
- TMTasks contains Projects (type=1), Tasks (type=0) and "ActionGroups" (type=2)
- Tasks are sometimes goruped by actionGroup (i.e. headers)
- some tasks have checklists (which consit of TMChecklistitems)

"""

DEFAULT_TARGET = 'Things3 export'


def export(args):
    try:
        args.called_from_gui
    except:
        # log to file only if not called from guo
        logging.basicConfig(filename='export.log', level=logging.ERROR)

    if args.format not in [RowObject.FMT_ALL, RowObject.FMT_PROJECT, RowObject.FMT_AREA]:
        raise Exception("unknown format %s" % args.format)

    con = sqlite3.connect(args.database)

    con.row_factory = sqlite3.Row

    # reroute stdout
    if args.format == RowObject.FMT_ALL and not args.stdout:
        filename = args.target
        if not filename.endswith('.taskpaper'):
            filename = RowObject.FILE_TMPL % filename
        reroute_stdout(filename)
    c = con.cursor()
    no_area = Area(dict(uuid='NULL', title='no area'), con, args)
    no_area.export()
    for row in c.execute(Area.QUERY):
        a = Area(row, con, args)
        a.export()
    con.close()

    if args.format == RowObject.FMT_ALL and not args.stdout:
        sys.stdout = sys.__stdout__


def reroute_stdout(filename, path_prefix=''):
    print("rerouting standardout to", filename)
    if path_prefix:
        filename = filename.replace(r'/', '|')
        filename = os.path.join(path_prefix, filename)
    sys.stdout = open(filename, 'w')


class RowObject(object):
    PROJECT_TEMPLATE = "\n%(indent)s%(title)s:%(tags)s"
    FMT_ALL = 'all'
    FMT_PROJECT = 'project'
    FMT_AREA = 'area'

    def __init__(self, row, con, args, level=0):
        self.row = row
        self.con = con
        self.args = args
        self.level = level

    def __getattr__(self, name):
        return self.row[name]

    def __getitem__(self, name):
        return getattr(self, name)

    TEMPLATE = '%s%s'

    def indent_(self, level):
        return "\t" * level

    @property
    def indent(self):
        return self.indent_(self.level)

    @property
    def notes_indent(self):
        return self.indent_(self.level + 1)

    @property
    def tags(self):
        return ''  # tags are empty for some items

    URL = re.compile("\<a href=\"(?P<url>.*)?\"\>.*?\<\/a\>")

    def print_notes(self):
        notes = self.notes[27:-7]
        for line in notes.split("\n"):
            line = self.URL.sub(lambda m: m.group('url'), line)
            print('%s%s' % (self.notes_indent, line))

    def find_and_export_items(self, klass, query):
        c = self.con.cursor()
        for row in c.execute(query):
            item = klass(row, self.con, self.args, self.level + 1)
            item.export()

    FILE_TMPL = "%s.taskpaper"

    def reroute_stdout(self, path_prefix):
        filename = self.FILE_TMPL % self.title
        reroute_stdout(filename, path_prefix)

    def makedirs(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)


class RowObjectWithTags(RowObject):

    TAGS_QUERY = """
        SELECT tag.title AS title FROM TMTaskTag AS tt, TMTag AS tag
        WHERE tt.tasks = '%s'
        AND tt.tags = tag.uuid;
    """

    def __init__(self, row, con, args, level=0):
        super().__init__(row, con, args, level)
        self._tags = []

    @property
    def tags(self):
        if len(self._tags) == 0:
            return ''
        return ' ' + ' '.join(self._tags)

    def add_tag(self, tag):
        if tag not in self._tags:
            self._tags.append(tag)

    def load_tags_from_db(self):
        def make_tag(title):
            return '@' + title.replace(' ', '_').replace('-', '_')

        c = self.con.cursor()
        for row in c.execute(self.TAGS_QUERY % self.uuid):
            self.add_tag(make_tag(row['title']))


class TaskObjects(RowObjectWithTags):

    task_fields = """
        SELECT uuid, status, title, type, notes, area, dueDate, startDate, todayIndex, checklistItemsCount, stopDate
        FROM TMTask
    """

    def add_attributes(self):
        """Add all attributes (due date, start date, today, someday etc.) as tags."""
        if self.dueDate:
            self.add_tag('@due(%s)' % datetime.fromtimestamp(self.dueDate).strftime("%Y-%m-%d"))
        if self.todayIndex:
            if self.startDate:
                self.add_tag('@today')
            else:
                self.add_tag('@someday')
        elif self.startDate:
            self.add_tag('@startDate(%s)' % datetime.fromtimestamp(self.startDate).strftime("%Y-%m-%d"))
        if self.stopDate:
            self.add_tag('@done(%s)' % datetime.fromtimestamp(self.stopDate).strftime("%Y-%m-%d"))


class Area(RowObjectWithTags):
    QUERY = """
        SELECT uuid, title FROM TMArea ORDER BY "index";
    """

    TAGS_QUERY = """
        SELECT tag.title AS title FROM TMAreaTag AS at, TMTag AS tag
        WHERE at.areas = '%s'
        AND at.tags = tag.uuid;
    """

    def export(self):
        logging.debug("Area: %s (%s)", self.title, self.uuid)
        self.load_tags_from_db()
        if args.format == RowObject.FMT_ALL:
            next_level = 1
            print(self.PROJECT_TEMPLATE % self)
        elif args.format == RowObject.FMT_AREA:
            # reroute stdout to a file for this area
            self.path = self.args.target
            self.makedirs()
            self.reroute_stdout(self.args.target)
            next_level = 0
        else:
            # set path and make folder for area
            self.path = os.path.join(self.args.target, self.title)
            self.makedirs()
            next_level = 0

        c = self.con.cursor()

        if self.uuid == 'NULL':
            inbox = Project(dict(uuid='NULL', title='Inbox',
                                 dueDate=None, startDate=None, stopDate=None, todayIndex=None, notes=None),
                            self.con, self.args, self.level + 1, self)
            inbox.export()
            query = Project.PROJECTS_WITHOUT_AREA
        else:
            self.find_and_export_items(Task, Task.TASKS_IN_AREA_WITHOUT_PROJECT % self.uuid)
            query = Project.PROJECTS_IN_AREA % self.uuid

        for row in c.execute(query):
            p = Project(row, self.con, self.args, next_level, self)
            p.export()

        if args.format == RowObject.FMT_AREA:
            sys.stdout = sys.__stdout__


class Project(TaskObjects):
    PROJECTS_IN_AREA = TaskObjects.task_fields + """
        WHERE type=1
        AND area="%s"
        AND trashed = 0
        AND status < 2 -- not canceled
        ORDER BY "index";
    """
    PROJECTS_WITHOUT_AREA = TaskObjects.task_fields + """
        WHERE type=1
        AND area is NULL
        AND trashed = 0
        AND status < 2 -- not canceled
        ORDER BY "index";
    """

    def __init__(self, row, con, args, level, area):
        super().__init__(row, con, args, level)
        self.area = area

    def export(self):
        logging.debug("Project: %s (%s)", self.title, self.uuid)
        self.load_tags_from_db()
        self.add_attributes()
        if args.format == RowObject.FMT_PROJECT:
            self.reroute_stdout(self.area.path)
        else:
            print(self.PROJECT_TEMPLATE % self)

        if self.notes:
            self.print_notes()

        if self.uuid == 'NULL':
            self.find_and_export_items(Task, Task.TASKS_IN_INBOX)
        else:
            self.find_and_export_items(Task, Task.TASKS_IN_PROJECT % self.uuid)

        if args.format == RowObject.FMT_PROJECT:
            sys.stdout = sys.__stdout__


class Task(TaskObjects):

    TASKS_IN_PROJECT = TaskObjects.task_fields + """
        WHERE type != 1 -- find tasks and action groups
        AND project="%s"
        AND trashed = 0
        AND status < 2 -- whatever "1" means
        ORDER BY type, "index"; -- tasks without headers come first
    """
    TASKS_IN_AREA_WITHOUT_PROJECT = TaskObjects.task_fields + """
        WHERE type != 1 -- find tasks and action groups
        AND area="%s"
        AND project is NULL
        AND trashed = 0
        AND status < 2 -- whatever "1" means
        ORDER BY type, "index"; -- tasks without headers come first
    """
    TASKS_IN_INBOX = TaskObjects.task_fields + """
        WHERE type != 1 -- find tasks and action groups
        AND project IS NULL
        AND area IS NULL
        AND actionGroup IS NULL
        AND trashed = 0
        AND status < 2 -- whatever "1" means
        ORDER BY "index";
    """
    TASKS_IN_ACTION_GROUPS = TaskObjects.task_fields + """
        WHERE type = 0
        AND actionGroup="%s"
        AND trashed = 0
        AND status < 2 -- whatever "1" means
        ORDER BY "index";
    """
    ACTIONGROUP = 2
    TASK_TEMPLATE = '%(indent)s- %(title)s%(tags)s'
    ACTIONGROUP_TEMPLATE = '%(indent)s%(title)s:'

    def export(self):
        logging.debug("Task: %s (%s) Level: %s Status: %s Type: %s", self.title, self.uuid, self.level, self.status, self.type)
        self.load_tags_from_db()
        self.add_attributes()
        if self.type == self.ACTIONGROUP:
            # process action group (which have no notes!)
            print(self.ACTIONGROUP_TEMPLATE % self)
            self.find_and_export_items(Task, Task.TASKS_IN_ACTION_GROUPS % self.uuid)
        else:
            print(self.TASK_TEMPLATE % self)
            if self.notes:
                self.print_notes()

            if self.checkListItemsCount:
                self.find_and_export_items(CheckListItem, CheckListItem.items_of_task % self.uuid)


class CheckListItem(RowObject):
    items_of_task = """
        SELECT uuid, title, status
        FROM TMChecklistItem
        WHERE task = '%s'
        ORDER BY "index"
    """

    def export(self):
        print(Task.TASK_TEMPLATE % self)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Export tasks from Things3 database to TaskPaper.')
    parser.add_argument('--target', dest='target', action='store',
                        default=DEFAULT_TARGET,
                        help='output folder (default: export_data')
    parser.add_argument('--db', dest='database', action='store',
                        default='Things.sqlite3',
                        help='path to the Things3 database (default: Things.sqlite3)')
    parser.add_argument('--format', dest='format', action='store',
                        default='project',
                        help='Define output format(area|project|all): what will be exported into one taskpaper file (default: project')
    parser.add_argument('--stdout', dest='stdout', action='store_true',
                        default=False,
                        help='output to standard output instead of file (only works with format=all)')

    args = parser.parse_args()
    export(args)
