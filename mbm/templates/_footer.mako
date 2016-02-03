<%def name="footer(gh, players)">
% if gh.state.is_over():
<%
fates = gh.state.get_faction_fates()
dead = set(gh.state.get_dead_players())
%>
The game is over. The players were:

% for player, player_spec in players.items():
* **${player_spec['name']}**, the **${player_spec['flavored_role']}**, ${'dead' if player in dead else 'alive'}, ${fates[player.get_faction()].name.lower()}
% endfor
% else:
${caller.body()}
% endif

</%def>
