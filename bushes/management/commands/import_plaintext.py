from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.db import transaction
from bushes.models import Sentence
import os
import os.path
import json
import re

_alnum_regex = re.compile(r'[a-zA-Z0-9]')

def _is_interp(s):
    return _alnum_regex.search(s) == None

class Command(BaseCommand):
    args = _("[file ...]")
    help = _("Import sentences from a text file. Expects space-separated "
             "tokens, one line per sentence.")

    requires_model_validation = True

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(_("Expected at least one argument"))

        for fn in args:
            with open(fn) as f:
                for lineno, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    tokens = []
                    for token in line.split():
                        token = token.decode('utf8')
                        tokens.append({
                            'orth': token,
                            'no_space': False,
                            'interp': _is_interp(token),
                        })
                    identifier = '%s:%d' % (fn, lineno)
                    sentence, created = Sentence.objects.get_or_create(
                            identifier=identifier)
                    sentence.text = line
                    sentence.tokens_json = json.dumps(tokens)
                    sentence.save()
