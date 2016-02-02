Welcome, ${player_spec['name']}.

You are the **${player_spec['flavored_role']}**. _${player_spec['flavor_text']}_

% if faction_friends is not None:

**Faction Friends**
% if faction_friends:
You know the following people in your faction:

% for friend in faction_friends:
* ${friend}
% endfor
% else:
There is nobody you know in your faction.
% endif
% endif

**Night Actions**
You may reply to this email with the actions you would like to perform, using the syntax specified in **bold** below:

% for action in actions:
* **${action['placeholder']}**
  ${action['description']}
% endfor

**Night will end in ${human_night_duration}.**
