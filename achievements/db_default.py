# Created by  on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.db import Table, Column

name = 'achievements'
version = 2
tables = [
    Table('achievements', key=('username', 'achievement'))[
        Column('username'),
        Column('achievement'),
    ],
    Table('achievements_counters', key=('username', 'counter'))[
        Column('username'),
        Column('counter'),
        Column('value', type='int'),
        Column('notify', type='int'),
    ],
]