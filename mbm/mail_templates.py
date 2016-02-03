from . import mail


def send_private(mailer, gh, id, player_spec, text, reply=False):
    return mailer.send(
        player_spec['email'],
        mail.make_markdown_email(text, {
            'From': '"Mafia Game (Private)" <game-{id}-private@{domain}>'
                .format(id=id, domain=mailer.domain),
            'To': '{name} <{email}>'.format(**player_spec),
            'Subject': '{re}{name}, Your Mafia Role'.format(
                re='' if not reply else 'Re: ', **player_spec)
        }, extensions=['markdown.extensions.nl2br']))


def send_moderator(mailer, gh, id, text):
    return mailer.send(
        gh.meta['moderator_email'],
        mail.make_markdown_email(text, {
            'From': '"Mafia Game (Mod)" <game-{id}-mod@{domain}>'.format(
                id=id, domain=mailer.domain),
            'To': '{email}'.format(email=gh.meta['moderator_email']),
            'Subject': 'Mafia Moderator Log'
        }, extensions=['markdown.extensions.nl2br']))


def send_public(mailer, gh, id, text):
    return mailer.send(
        [player_spec['email'] for player_spec in gh.meta['players']],
        mail.make_markdown_email(text, {
            'From': '"Mafia Game (Public)" <game-{id}-public@{domain}>'
                .format(id=id, domain=mailer.domain),
            'To': ', '.join('{name} <{email}>'.format(**player_spec)
                            for player_spec in gh.meta['players']),
            'Subject': 'Welcome to Mafia'
        }, extensions=['markdown.extensions.nl2br']))
