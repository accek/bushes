# coding: utf-8

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import condition, require_POST
from django.db.models import Max, Count
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import login
from bushes.models import Assignment, Tree, Sentence
import re
import random
import json
import datetime

TEXT = "Natenczas Wojski chwycił na taśmie przypięty swój róg bawoli, " \
    "długi, cętkowany, kręty jak wąż boa, oburącz do ust go przycisnął, " \
    "wzdął policzki jak banie, w oczach krwią zabłysnął i zagrał."

class Token(object):
    def __init__(self, num, orth, no_space=False, interp=False):
        self.num = num
        self.orth = orth
        self.no_space = no_space
        self.interp = interp

def text_to_tokens(text):
    tokens = []
    num = 0
    for token in text.split():
        extra_token = None
        if token[-1] in ['.', ',']:
            extra_token = token[-1]
            token = token[:-1]
        tokens.append(Token(num, token))
        num += 1
        if extra_token:
            tokens.append(Token(num, extra_token, True, True))
            num += 1
    return tokens

def remaining_assignments(user):
    return Assignment.objects.filter(user=user,
            latest_tree__isnull=True)

def index_view(request):
    if not request.user.is_authenticated():
        return login(request)
    context = {
        'assignments': remaining_assignments(request.user),
    }
    return TemplateResponse(request, 'index.html', context)

def assignment_last_modified(request, id):
    return Assignment.objects.get(id=id).creation_date

#@condition(last_modified_func=assignment_last_modified)
@cache_control(must_revalidate=False, max_age=3600)
def assignment_view(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    if not (request.user.is_superuser or request.user == assignment.user):
        raise PermissionDenied

    context = {
        'assignment': assignment,
        'ready': assignment.latest_tree is not None,
    }
    return TemplateResponse(request, 'assignment.html', context)

@login_required
def clone_view(request, tree_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    tree = get_object_or_404(Tree, id=tree_id)
    assignment = Assignment(user=request.user,
            sentence=tree.assignment.sentence,
            tree_json=tree.tree_json)
    assignment.save()
    return redirect('assignment', id=assignment.id)

@login_required
def sentence_view(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied

    sentence = get_object_or_404(Sentence, id=id)
    assignments = sentence.assignments.filter(latest_tree_id__isnull=False) \
            .select_related()
    trees = [a.latest_tree for a in assignments]

    context = {
        'sentence': sentence,
        'trees': trees,
    }
    return TemplateResponse(request, 'sentence.html', context)

#@cache_control(must_revalidate=False, max_age=5)
def manifest_view(request):
    if not request.user.is_authenticated():
        raise Http404
    context = {
        'assignments': remaining_assignments(request.user),
    }
    return TemplateResponse(request, 'manifest.appcache', context,
            content_type='text/cache-manifest')

@require_POST
@csrf_exempt
def upload_view(request):
    if not request.is_ajax():
        raise PermissionDenied
    data = json.loads(request.body)
    try:
        assignment = Assignment.objects.get(id=data['id'])
        tree = Tree(assignment=assignment,
                tree_json=json.dumps(data['parents']))
        tree.save()
        assignment.tree_json = tree.tree_json
        assignment.latest_tree = tree
        assignment.completion_date = datetime.datetime.now()
        assignment.save()
    except Assignment.DoesNotExist:
        pass
    return HttpResponse('OK', content_type='text/plain')

@login_required
def more_view(request):
    sentences = Sentence.objects.annotate(num_a=Count('assignments')) \
            .order_by('num_a', 'id')[:settings.ASSIGNMENT_SIZE]
    for s in sentences:
        a = Assignment(sentence=s, user=request.user)
        a.save()
    return redirect('index')

@login_required
def return_view(request):
    Assignment.objects.filter(user=request.user,
            latest_tree__isnull=True).delete()
    return redirect('index')
