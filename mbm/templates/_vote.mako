<%def name="summary(ballot)">
<%
summary = ballot.get_summary()
%>

% if not summary:
There are no votes.
% else:
The summary of votes is as follows:

% for voter, votee in ballot.get_summary().items():
* **${players[voter]['name']}** votes for **${players[votee]['name']}**.
% endfor
% endif
</%def>
