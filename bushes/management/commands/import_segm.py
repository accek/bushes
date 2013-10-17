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
    args = _("[folder]")
    help = _("Finds all *.segm files and adds the sentences to the database")

    requires_model_validation = True

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(_("Expected one argument"))

        base_path = args[0]
        os.chdir(base_path)

        for root, dirs, files in os.walk('.'):
            for fn in files:
                if not fn.endswith('.segm'):
                    continue
                path = os.path.join(root, fn)[2:]
                self.stdout.write(path);
                tokens = []
                text = ''
                with open(path) as f:
                    for line in f:
                        token, nospace = line.strip().rsplit(' ', 1)
                        token = token.decode('utf8')
                        nospace = bool(nospace == 'True')
                        if not nospace and text:
                            text += ' '
                        text += token
                        tokens.append({
                            'orth': token,
                            'no_space': nospace,
                            'interp': _is_interp(token),
                        })
                sentence, created = Sentence.objects.get_or_create(
                        identifier=path)
                sentence.text = text
                sentence.tokens_json = json.dumps(tokens)
                sentence.save()
