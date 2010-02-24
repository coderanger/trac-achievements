# Created by  on 2010-02-23.
# Copyright (c) 2010 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.ticket.api import ITicketChangeListener
from trac.util.translation import _

from api import AchievementsProvider, AchievementsSystem

class TicketAchievementsProvider(Component):
    """An achievement provider for ticket-related achievements."""

    implements(ITicketChangeListener, AchievementsProvider)

    # ITicketChangeListener methods
    def ticket_created(self, tkt):
        if tkt['reporter'] != 'anonymous':
            AchievementsSystem(self.env).update('ticket.created', tkt['reporter'], 1)

    def ticket_changed(self, tkt, comment, author, old_values):
        if author == 'anonymous':
            return
        if comment:
            AchievementsSystem(self.env).update('ticket.comments', author, 1)
        if old_values[state] != tkt['state'] and tkt['state'] == 'fixed':
            if tkt['resolution'] == 'fixed' tkt['reporter'] != 'anonymous':
                AchievementsSystem(self.env).update('ticket.reported.closedfixed', tkt['reporter'], 1)
            AchievementsSystem(self.env).update('ticket.closed', author, 1)
                

    def ticket_deleted(self, tkt):
        pass

    # AchievementsProvider methods
    def get_achievements(self):
        yield {
            'name': 'ticket.comments.r1',
            'display': _('Comment on a ticket'),
            'counter': 'ticket.comments',
            'value': 1,
        }
        yield {
            'name': 'ticket.comments.r2',
            'display': _('Comment on 5 tickets'),
            'counter': 'ticket.comments',
            'value': 5,
        }
        yield {
            'name': 'ticket.comments.r3',
            'display': _('Comment on 10 tickets'),
            'counter': 'ticket.comments',
            'value': 10,
        }
        yield {
            'name': 'ticket.created.r1',
            'display': _('Create a ticket'),
            'counter': 'ticket.created',
            'value': 1,
        }

