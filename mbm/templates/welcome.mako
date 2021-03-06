<%
import ago
import datetime
%>

Welcome to Mafia!

This thread will be used to announce deaths during the night and votes during the day. Please do not reply to this thread.

You should have received an email containing details about your role. You can reply to that thread to perform actions.

The players are:

% for player_spec in players.values():
* ${player_spec['name']}
% endfor

**Night will end in ${ago.human(datetime.timedelta(seconds=gh.meta['night_duration']), past_tense='{}')}.**
