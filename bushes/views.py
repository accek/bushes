# coding: utf-8

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import condition, require_POST
from django.db.models import Max, Count, Q, F
from django.db import transaction
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

def superannotate_refresh_view(request):
    if not request.user.is_staff:
        raise PermissionDenied

    sentences = Sentence.objects \
            .exclude(state__in=('REVIEWED', 'AUTOACCEPTED')) \
            .annotate(num_assignments=Count('assignments__latest_tree')) \
            .filter(num_assignments__gte=2) \
            .annotate(
                    distinct_trees=Count('assignments__latest_tree__tree_json',
                        distinct=True))
    #print sentences.query

    # Autoaccept
    print "Autoaccepting..."
    autoaccept_sentences = sentences.filter(distinct_trees=1)
    Tree.objects.filter(assignment__latest_tree_id=F('id'),
                assignment__sentence__in=autoaccept_sentences) \
            .update(state='ACCEPTED')
    ids = autoaccept_sentences.values_list('id', flat=True)
    Sentence.objects.filter(id__in=ids).update(state='AUTOACCEPTED')

    # Remove assignments for accepted sentences
    print "Removing extra assignments..."
    ids = Assignment.objects.filter(sentence__state__in=('REVIEWED',
        'AUTOACCEPTED'), latest_tree__isnull=True).values_list('id', flat=True)
    Assignment.objects.filter(id__in=ids).delete()

    # For manual review
    print "Marking sentences..."
    ids = sentences.filter(distinct_trees__gt=1).values_list('id', flat=True)
    Sentence.objects.filter(id__in=ids).update(state='FOR_REVIEW')

    return redirect('superannotate')

def _new_sentences_for_superannotation(request, count):
    if not count:
        return Sentence.objects.none()
    queryset = Sentence.objects \
            .filter(state='FOR_REVIEW', superannotator__isnull=True) \
            .exclude(assignments__user=request.user) \
            .select_for_update()
    return queryset[:count]

def _sentences_for_superannotation(request):
    return Sentence.objects \
            .filter(state='FOR_REVIEW', superannotator=request.user) \
            .order_by('id')

def superannotate_view(request):
    if not request.user.is_staff:
        raise PermissionDenied
    max_count = 10
    sentences = list(_sentences_for_superannotation(request)[:max_count])
    new_sentences = _new_sentences_for_superannotation(
            request, max_count - len(sentences))
    sentences += list(new_sentences)
    new_ids = new_sentences.values_list('id', flat=True)
    Sentence.objects.filter(id__in=new_ids).update(superannotator=request.user)
    num_extra = Sentence.objects.filter(state='FOR_REVIEW',
            superannotator__isnull=True).count()
    context = {
        'num_extra': num_extra,
        'max': len(sentences) == max_count,
        'sentences': sentences,
    }
    return TemplateResponse(request, 'superannotate.html', context)

def superannotate_cancel_view(request):
    if not request.user.is_staff:
        raise PermissionDenied
    Sentence.objects.filter(state='FOR_REVIEW', superannotator=request.user) \
            .update(superannotator=None)
    return redirect('index')

def superannotate_next_view(request):
    if not request.user.is_staff:
        raise PermissionDenied
    sentences = _sentences_for_superannotation(request)[:1]
    if not sentences:
        return redirect('superannotate')
    return redirect('sentence', id=sentences[0].id)

def my_errors_view(request):
    sentences = Sentence.objects \
            .filter(state__in=('REVIEWED', 'AUTOACCEPTED'),
                    assignments__user=request.user,
                    assignments__latest_tree__state='REJECTED') \
            .annotate(latest_assignment=Max('assignments__completion_date')) \
            .order_by('-latest_assignment') \
            [:200]
    context = {
        'sentences': sentences,
    }
    return TemplateResponse(request, 'my-errors.html', context)

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
    if not request.user.is_staff and not request.user.is_superuser:
        raise PermissionDenied

    tree = get_object_or_404(Tree, id=tree_id)
    assignment = Assignment(user=request.user,
            sentence=tree.assignment.sentence,
            tree_json=tree.tree_json)
    assignment.save()
    return redirect('assignment', id=assignment.id)

@login_required
def accept_view(request, tree_id):
    if not request.user.is_staff and not request.user.is_superuser:
        raise PermissionDenied

    tree = get_object_or_404(Tree, id=tree_id)
    good_tree_json = tree.tree_json
    sentence = tree.assignment.sentence

    trees_for_sentence = \
            Tree.objects.filter(assignment__sentence=sentence)
    trees_for_sentence.filter(tree_json=good_tree_json) \
            .update(state='ACCEPTED')
    trees_for_sentence.exclude(tree_json=good_tree_json) \
            .update(state='REJECTED')
    sentence.state = 'REVIEWED'
    sentence.save()

    return redirect('sentence', id=sentence.id)

@login_required
def unaccept_view(request, tree_id):
    if not request.user.is_staff and not request.user.is_superuser:
        raise PermissionDenied

    tree = get_object_or_404(Tree, id=tree_id)
    sentence = tree.assignment.sentence

    trees_for_sentence = \
            Tree.objects.filter(assignment__sentence=sentence)
    trees_for_sentence.update(state='FOR_REVIEW')
    sentence.state = 'FOR_REVIEW'
    sentence.save()

    return redirect('sentence', id=sentence.id)


def check_tree(tree):
    try:
        sentence = tree.assignment.sentence
        tokens = json.loads(sentence.tokens_json)
        parents = json.loads(tree.tree_json)
        if not isinstance(parents, list) or len(parents) != len(tokens):
            return False
        return True
    except Exception:
        return False


@login_required
def sentence_view(request, id):
    sentence = get_object_or_404(Sentence, id=id)

    if not request.user.is_superuser and not request.user.is_staff \
            and sentence.state not in ('REVIEWED', 'AUTOACCEPTED'):
        raise PermissionDenied

    assignments = sentence.assignments.filter(latest_tree_id__isnull=False) \
            .select_related()
    trees = [a.latest_tree for a in assignments]

    ok = True
    for tree in trees:
        if not check_tree(tree):
            tree.delete()
            ok = False

    if not ok:
        sentence.state = 'FOR_ANNOTATION'
        sentence.superannotator = None
        sentence.save()
        context = {
            'sentence': sentence,
        }
        return TemplateResponse(request, 'bad-sentence.html', context)


    can_review = request.user.is_superuser or request.user.is_staff
    done = can_review and not filter(lambda t: t.state == 'FOR_REVIEW', trees)

    context = {
        'sentence': sentence,
        'trees': trees,
        'can_review': can_review,
        'superannotation_done': done,
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
    sentences = Sentence.objects \
            .filter(state='FOR_ANNOTATION') \
            .exclude(assignments__user=request.user) \
            .annotate(num_a=Count('assignments')) \
            .filter(num_a__lt=3) \
            .order_by('-num_a', '-priority', 'id') \
            [:settings.ASSIGNMENT_SIZE]
    for s in sentences:
        a = Assignment(sentence=s, user=request.user)
        a.save()
    return redirect('index')

@login_required
def return_view(request):
    Assignment.objects.filter(user=request.user,
            latest_tree__isnull=True).delete()
    return redirect('index')
