# Created by Noah Kantrowitz on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.
from copy import copy

from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.web.api import IRequestFilter
from trac.web.chrome import add_script, add_script_data, ITemplateProvider
from trac.db.util import with_transaction
from pkg_resources import resource_filename

import db_default

class AchievementsProvider(Interface):
    """An extension point interface for exposing achievements."""

class AchievementsSystem(Component):
    """Core achievements processing."""

    implements(IEnvironmentSetupParticipant, IRequestFilter, ITemplateProvider)
    
    providers = ExtensionPoint(AchievementsProvider)
    
    def __init__(self):
        self.achievements = {}
        self.counters = {}
        for provider in self.providers:
            for achievement in provider.get_achievements():
                achievement['provider'] = provider
                self.achievements[achievement['name']] = achievement
                self.counters.setdefault(achievement['counter'], []).append(achievement)
        for achievements in self.counters.itervalues():
            achievements.sort(key=lambda a: a['value'])

    # Public methods
    def update(self, counter, username, value):
        @with_transaction(self.env)
        def txn(db):
            cursor = db.cursor()
            cursor.execute('UPDATE achievements_counters SET value=(SELECT value FROM achievements_counters WHERE username=%s AND counter=%s)+%s WHERE username=%s AND counter=%s',
                           (username, counter, value, username, counter))
            if not cursor.rowcount:
                cursor.execute('INSERT INTO achievements_counters (username, counter, value, notify) VALUES (%s, %s, %s, %s)',
                               (username, counter, value, self.counters[counter][0]['value']))

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
            
    def post_process_request(self, req, template, data, content_type):
        achieved = []
        @with_transaction(self.env)
        def txn(db):
            if req.authname == 'anonymous':
                return
            cursor = db.cursor()
            cursor.execute('SELECT counter, value, notify FROM achievements_counters WHERE username=%s AND value>=notify AND notify!=-1', (req.authname,))
            for counter, value, notify in cursor.fetchall():
                new_notify = -1
                current_ach = None
                for ach in self.counters[counter]:
                    if current_ach:
                        new_notify = ach['value']
                        break
                    if ach['value'] == notify:
                        current_ach = copy(ach)
                        del current_ach['provider']
                cursor.execute('UPDATE achievements_counters SET notify=%s WHERE username=%s AND counter=%s', (new_notify, req.authname, counter))
                cursor.execute('INSERT INTO achievements (username, achievement) VALUES (%s, %s)', (req.authname, current_ach['name']))
                achieved.append(current_ach)
        add_script_data(req, {'achievements': achieved})
        add_script(req, 'achievements/achievements.js')
        return template, data, content_type

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        yield 'achievements', resource_filename(__name__, 'htdocs')
            
    def get_templates_dirs(self):
        #yield resource_filename(__name__, 'templates')
        return []

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self.found_db_version = 0
        self.upgrade_environment(self.env.get_db_cnx())
        
    def environment_needs_upgrade(self, db):
        cursor = db.cursor()
        cursor.execute("SELECT value FROM system WHERE name=%s", (db_default.name,))
        value = cursor.fetchone()
        if not value:
            self.found_db_version = 0
            return True
        else:
            self.found_db_version = int(value[0])
            #self.log.debug('AchievementSystem: Found db version %s, current is %s' % (self.found_db_version, db_default.version))
            return self.found_db_version < db_default.version
            
    def upgrade_environment(self, db):
        # 0.10 compatibility hack (thanks Alec)
        try:
            from trac.db import DatabaseManager
            db_manager, _ = DatabaseManager(self.env)._get_connector()
        except ImportError:
                db_manager = db
                
        # Insert the default table
        old_data = {} # {table_name: (col_names, [row, ...]), ...}
        cursor = db.cursor()
        if not self.found_db_version:
            cursor.execute("INSERT INTO system (name, value) VALUES (%s, %s)",(db_default.name, db_default.version))
        else:
            cursor.execute("UPDATE system SET value=%s WHERE name=%s",(db_default.version, db_default.name))
            for tbl in db_default.tables:
                try:
                    cursor.execute('SELECT * FROM %s'%tbl.name)
                    old_data[tbl.name] = ([d[0] for d in cursor.description], cursor.fetchall())
                    cursor.execute('DROP TABLE %s'%tbl.name)
                except Exception, e:
                    if 'OperationalError' not in e.__class__.__name__:
                        raise e # If it is an OperationalError, just move on to the next table
                            
                
        for tbl in db_default.tables:
            for sql in db_manager.to_sql(tbl):
                cursor.execute(sql)
                    
            # Try to reinsert any old data
            if tbl.name in old_data:
                data = old_data[tbl.name]
                sql = 'INSERT INTO %s (%s) VALUES (%s)' % \
                      (tbl.name, ','.join(data[0]), ','.join(['%s'] * len(data[0])))
                for row in data[1]:
                    try:
                        cursor.execute(sql, row)
                    except Exception, e:
                        if 'OperationalError' not in e.__class__.__name__:
                            raise e