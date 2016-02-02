from mafia import actions


COMMANDS = {
    actions.Roleblock: 'roleblock $target',
    actions.Kill: 'kill $target',
    actions.Investigate: 'investigate $target',
    actions.Protect: 'protect $target',
    actions.Drive: 'drive $target_a with $target_b',
    actions.Suicide: 'commit suicide',
    actions.Autopsy: 'autopsy $target',
    actions.Commute: 'commute',
    actions.Watch: 'watch $target',
    actions.Track: 'track $target',
    actions.Bodyguard: 'bodyguard $target',
    actions.Recruit: 'recruit $target',
    actions.StealVote: 'steal vote from $target',
    actions.Redirect: 'redirect $target to $redirectee',
    actions.Deflect: 'deflect $target onto $deflectee',
    actions.Hide: 'hide behind $target',
    actions.Jail: 'jail $target',
}
