# Created by Noah Kantrowitz on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.env import IEnvironmentSetupParticipant

import db_default

class AchievementsProvider(Interface):
    """An extension point interface for exposing achievements."""

class AchieventmentsSystem(Component):
    """Core achievements processing."""

    implements(IEnvironmentSetupParticipant)
    
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