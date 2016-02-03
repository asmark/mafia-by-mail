<%namespace name="footer" file="_footer.mako" />

<%
import ago
import datetime
%>

Night ${turn_number} has ended and it is now day.

% if not deaths:
Nobody was found dead.
% else:
The following players were found dead:

% for death in deaths:
* **${players[death]['name']}**, the **${players[death]['flavored_role']}**.
% endfor
% endif

<%footer:footer gh="${gh}" players="${players}">
You may now vote for a player to lynch via your role email thread with **vote _player_**. To retract a vote, you may use **retract**.

Lynch votes will be announced here. At the end of the day, the player with the most votes will be lynched.

**Day will end in ${ago.human(datetime.timedelta(seconds=gh.meta['day_duration']), past_tense='{}')}.**
</%footer:footer>
