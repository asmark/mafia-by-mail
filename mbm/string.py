import re
import string


class Template(string.Template):
    def __init__(self, template):
        super().__init__(template)
        self.vars = tuple(self._extract_vars())

    def _extract_vars(self):
        for match in self.pattern.finditer(self.template):
            if match.group('invalid') is not None:
                self._invalid(m)

            if match.group('escaped'):
                continue

            yield match.group('braced') or match.group('named')

    def substitute_with_name(self, lookup=lambda name: name):
        return self.substitute(**{v: lookup(v) for v in self.vars})



def reformat_lines(s):
    return re.sub(r'\n+', lambda m: '\n' if len(m.group(0)) > 1 else ' ', s)
