<%namespace name="footer" file="_footer.mako" />
<%namespace name="vote" file="_vote.mako" />

<%
import ago
import datetime
%>

Day ${turn_number} has ended and it is now night.

<%vote:summary ballot="${ballot}" />

The following players are up for lynching:
% for candidate in ballot.get_candidates():
* ${players[candidate]['name']}
% endfor

<%
lynchee = ballot.get_lynchee()
%>

**${players[lynchee]['name']}**, the **${players[lynchee]['flavored_role']}**, was lynched.
% endif

<%footer:footer gh="${gh}" players="${players}">
**Night will end in ${ago.human(datetime.timedelta(seconds=gh.meta['night_duration']), past_tense='{}')}.**
</%footer:footer>
