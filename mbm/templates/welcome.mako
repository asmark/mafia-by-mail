Welcome, ${player_spec['name']}.

You are the **${player_spec['flavored_role']}**. _${player_spec['flavor_text']}_

**Players**
Your fellow players are:

% for other_player_spec in player_specs:
* ${other_player_spec['name']}
% endfor
% if faction_friends:

**Faction Friends**
You know the following people in your faction:

% for friend in faction_friends:
* ${friend}
% endfor
% endif

**Night Actions**
You may reply to this email with the actions you would like to perform, using the syntax specified in **bold** below:

% for action in actions:
* **${action['placeholder']}**
  ${action['description']}
% endfor

**Night will end in ${human_night_duration}.**
