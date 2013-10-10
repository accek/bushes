# coding: utf-8

from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
import re

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

#@login_required
def index_view(request):
    text = TEXT
    tokens = text_to_tokens(text)
    context = {
        'text': text,
        'tokens': tokens,
    }
    return TemplateResponse(request, 'index.html', context)
