# Created by  on 2010-02-24.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.web.api import IRequestHandler

from api import AchievementsSystem

class AchievementsModule(Component):
    """A web interface to display available achievements."""

    implements(IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/achievements')

    def process_request(self, req):
        if req.authname == 'anonymous':
            raise TracError, 'Achievements not available for unauthenticated users'
        data = {}
        data['achievements'] = AchievementsSystem(self.env).get_user_achievements(req.authname)
        
        # Temporary hack to display counters for debugging
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute('SELECT counter, value, notify FROM achievements_counters WHERE username=%s', (req.authname,))
        data['counters'] = cursor.fetchall()
        
        return 'achievements.html', data, 'text/html'
