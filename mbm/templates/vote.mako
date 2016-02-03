<%namespace name="vote" file="_vote.mako" />

% if votee is not None:
**${player_spec['name']}** has cast their vote for **${players[votee]['name']}**.
% else:
**${player_spec['name']}** retracted their vote.
% endif

<%vote:summary ballot="${ballot}" />
