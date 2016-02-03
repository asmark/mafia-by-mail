<%
from mbm import infos
%>

% if not messages:
You don't have any night action results. If you did perform night actions that have results, they may have been blocked.
% else:
You received the following information:

% for message in messages:
* ${infos.show(message.info, players)}
% endfor
% endif
