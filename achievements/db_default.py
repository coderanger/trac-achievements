# Created by  on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.db import Table, Column

name = 'achievements'
version = 1
tables = [
    Table('achievements_users', key=('username', 'achievement'))[
        Column('username'),
        Column('achievement'),
        Column('complete'),
        Column('displayed'),
    ],
    Table('achievements_counters', key=('username', 'counter'))[
        Column('username'),
        Column('counter'),
        Column('value', type='int'),
        Column('notify', type='int'),
    ],
]