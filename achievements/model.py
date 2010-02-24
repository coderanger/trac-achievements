# Created by  on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.db.util import with_transaction

class AchievementCounter(object):
    """A model for a single achievement counter."""

    def __init__(self, env, name, username, db=None):
        self.env = env
        self.name = name
        self.username = username
        
        db = db or self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute('SELECT value FROM achievements_counters WHERE username=%s AND counter=%s', (self.username, self.name))
        row = cursor.fetchone()
        if row:
            self.value = int(row[0])
        else:
            self.value = 0
    
    def save(self, db=None):
        @with_transaction(self.env, db)
        def txn(db):
            cursor = db.cursor()
            cursor.execute('UPDATE achievements_counters SET value=%s WHERE username=%s AND counter=%s', (self.value, self.username, self.name))
            if not cursor.rowcount:
                cursor.execute('INSERT INTO achievements_counters (value, username, counter) VALUES (%s, %s, %s)', (self.value, self.username, self.name))


    @classmethod
    def update(cls, env, name, username, value):
        db = env.get_db_cnx()
        try:
            counter = cls(env, name, username, db)
            counter.value += value
            counter.save(db)
            db.commit()
        except:
            db.rollback()
            raise