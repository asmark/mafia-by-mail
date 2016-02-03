<%
import inspect

from mbm import actions
from mbm import string
%>

Welcome, ${player_spec['name']}.

You are the **${player_spec['flavored_role']}**. _${player_spec['flavor_text']}_

<%
faction_friends = player.get_faction().get_friends(gh.state)
%>
% if faction_friends is not None:

**Faction Friends**
% if faction_friends:
You know the following people in your faction:

% for friend in faction_friends:
% if friend is not player:
* ${players[friend]['name']}
% endif
% endfor
% else:
There is nobody you know in your faction.
% endif
% endif

**Night Actions**
You may reply to this email with the actions you would like to perform, using the syntax specified in **bold** below, one per line. You must specify all actions in the order below. If you do not wish to take an action, you may use the word **ignore**.

% for i, action in enumerate(player.actions):
${i}. **${actions.COMMANDS[action.__class__].substitute_with_name(lambda name: '_' + name + '_')}**
  ${string.reformat_lines(inspect.getdoc(action))}
% if action.compelled:
    * You are compelled to perform this action; random targets will be selected if you do not choose to perform it.
% endif
% if action.ninja:
    * This action is invisible to all investigatory roles.
% endif
% if action.num_shots != float('inf'):
    * This action may only be used ${action.num_shots} time(s).
% endif
% endfor

Alternatively, you may also use **cancel** to cancel all your night actions.
