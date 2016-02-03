<%
from mbm import infos

messages = list(gh.state.turn.get_messages_for_player(player))
%>

% if not messages:
You don't have any night action results. If you did perform night actions that have results, they may have been blocked.
% else:
You received the following information:

% for message in messages:
* ${infos.show(message.info, players)}
% endfor
% endif

% if not player.is_dead():
You may now vote for a player to lynch via your role email thread with **vote _player_**. To retract a vote, you may use **retract**.
% else:
You are dead. You may no longer participate in the game, but you will receive updates until the game ends.
% endif
