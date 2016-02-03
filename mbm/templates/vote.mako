<%namespace name="vote" file="_vote.mako" />

% if votee is not None:
**${players[voter]['name']}** has cast their vote for **${players[votee]['name']}**.
% else:
**${player[voter]}** retracted their vote.
% endif

<%vote:summary ballot="${ballot}" />
