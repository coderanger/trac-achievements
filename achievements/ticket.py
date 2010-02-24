# Created by  on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.ticket.api import ITicketChangeListener
from trac.util.translation import _

from achievments.api import AchievementsProvider
from achievements.model import AchievementCounter

class TicketAchievementsProvider(Component):
    """An achievement provider for ticket-related achievements."""

    implements(ITicketChangeListener, AchievementsProvider)

    # ITicketChangeListener methods
    def ticket_created(self, tkt):
        pass

    def ticket_changed(self, tkt, comment, author, old_values):
        AchievementCounter.update(self.env, 'ticket.comments', author, 1)

    def ticket_deleted(self, tkt):
        pass

    # AchievementsProvider methods
    def get_achievements(self):
        yield {
            'name': 'ticket.comments_r1',
            'display': _('Comment on a ticket'),
            'counter': 'ticket.comments',
            'value': 1,
        }
