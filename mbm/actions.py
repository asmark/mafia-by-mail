from mafia import actions

from . import string

T = string.Template


COMMANDS = {
    actions.Roleblock: T('roleblock $target'),
    actions.Kill: T('kill $target'),
    actions.Investigate: T('investigate $target'),
    actions.Protect: T('protect $target'),
    actions.Drive: T('drive $target_a with $target_b'),
    actions.Suicide: T('commit suicide'),
    actions.Autopsy: T('autopsy $target'),
    actions.Commute: T('commute'),
    actions.Watch: T('watch $target'),
    actions.Track: T('track $target'),
    actions.Bodyguard: T('bodyguard $target'),
    actions.Recruit: T('recruit $target'),
    actions.StealVote: T('steal vote from $target'),
    actions.Redirect: T('redirect $target to $redirectee'),
    actions.Deflect: T('deflect $target onto $deflectee'),
    actions.Hide: T('hide behind $target'),
    actions.Jail: T('jail $target'),
}
