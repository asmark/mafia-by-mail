<%
import itertools
from mbm import actions

player_acts = [act for act in plan.get_queued_actions().values() if act.source is player]
%>

% for i, (command, result) in enumerate(itertools.zip_longest(commands, results, fillvalue=None)):
${i}. **${command or '(not specified)'}:** ${result}
% endfor

% if not player_acts:
You have no actions planned.
% else:
You have the following actions planned:

% for act in player_acts:
<%
template = actions.COMMANDS[act.action.__class__]
%>
* ${actions.COMMANDS[act.action.__class__].substitute(**dict(zip(act.action.TARGET_SELECTORS, (players[target]['name'] for target in act.targets))))}
% endfor
% endif
