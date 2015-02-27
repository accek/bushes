from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.db import transaction
from django.db.models import Min
from bushes.models import Sentence, Tree
import os
import os.path
import json
import re
import traceback

_alnum_regex = re.compile(r'[a-zA-Z0-9]')

def _is_interp(s):
    return _alnum_regex.search(s) == None

class Command(BaseCommand):
    args = _("[folder_with_segm]")
    help = _("Finds all *.segm files and adds the sentences to the database")

    requires_model_validation = True

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(_("Expected one argument"))

        base_path = args[0]
        os.chdir(base_path)

        trees = Tree.objects \
                .filter(state='ACCEPTED') \
                .values('assignment__sentence__identifier',
                    'assignment__sentence__tokens_json') \
                .annotate(min_tree=Min('tree_json'))

        for tree in trees:
            identifier = tree['assignment__sentence__identifier']
            self.stdout.write(identifier)
            try:
                tokens = json.loads(tree['assignment__sentence__tokens_json'])
                parents = json.loads(tree['min_tree'])
                for parent in parents:
                    if parent is not None and (parent < 0 or parent >=
                            len(parents)):
                        self.stdout.write(" * Invalid tree.")
                        break
                else:
                    basename = os.path.splitext(identifier)[0]
                    with open(basename + '.tree', 'w') as f:
                        for i, (token, parent) in enumerate(zip(tokens, parents)):
                            if parent is None:
                                parent = -1
                            out = (i + 1, token['orth'].encode('utf8'), '_', '_', '_', '_',
                                parent + 1, '_', '_', '_')
                            f.write('\t'.join(map(str, out)) + '\n')
            except Exception:
                traceback.print_exc()
