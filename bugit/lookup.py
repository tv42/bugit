import os
import re

from bugit import storage

class TicketLookupError(Exception):
    """Ticket lookup error"""

    def __str__(self):
        l = [self.__doc__]
        l.extend(self.args)
        return ': '.join(l)

class TicketNotFoundError(TicketLookupError):
    """Ticket not found"""

class MatchesMultipleTicketsError(TicketLookupError):
    """Matches more than one ticket"""

def list_tickets(transaction):
    for (mode, type_, object, basename) in storage.git_ls_tree(
        path='',
        treeish=transaction.head,
        repo=transaction.repo,
        children=True,
        ):
        # TODO enforce filename sanity
        yield basename

def match_all(
    transaction,
    pattern,
    ):
    g = list_tickets(transaction=transaction)
    if pattern.startswith('#'):
        for ticket in g:
            number = transaction.get(os.path.join(ticket, 'number'))
            if number is not None:
                number = number.rstrip()
                if '#%s' % number == pattern:
                    yield ticket
    else:
        for ticket in g:
            if re.match('^[0-9a-f]{4,}$', pattern):
                # looks like an abbreviated sha
                if ticket.startswith(pattern):
                    yield ticket
            else:
                has_name = transaction.get(
                    path=os.path.join(ticket, 'name', pattern),
                    )
                if has_name is not None:
                    yield ticket

def exists(
    transaction,
    ticket,
    ):
    found = False
    for (mode, type_, object, basename) in storage.git_ls_tree(
        path=ticket,
        treeish=transaction.head,
        repo=transaction.repo,
        children=False,
        ):
        found = True
        break
    return found

def match(
    transaction,
    requested_ticket,
    ):
    if re.match('^[0-9a-f]{40}$', requested_ticket):
        # full sha, no need to look up, just check it's there
        if not exists(
            transaction=transaction,
            ticket=requested_ticket,
            ):
            raise TicketNotFoundError(requested_ticket)
        ticket = requested_ticket
    else:
        g = match_all(
            transaction=transaction,
            pattern=requested_ticket,
            )
        tickets = list(g)
        if not tickets:
            raise TicketNotFoundError(requested_ticket)
        if len(tickets) > 1:
            raise MatchesMultipleTicketsError(requested_ticket)
        (ticket,) = tickets

    return ticket
