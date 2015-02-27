from django.contrib import admin
from django.db.models import Count, Max, TextField
from django.core.urlresolvers import reverse
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from bushes.models import Sentence, Assignment, Tree

from ckeditor.widgets import CKEditorWidget


class AdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated()

site = AdminSite()

site.register(User, UserAdmin)

class SentenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'identifier', 'sentence', 'length',
            'priority', 'num_assignments', 'num_trees', 'last_tree',
            'state', 'superannotator')
    list_display_links = ('id',)
    list_filter = ('state', 'superannotator')

    def num_assignments(self, instance):
        return int(instance.num_a)
    num_assignments.admin_order_field = 'num_a'
    num_assignments.short_description = '# assignments'

    def num_trees(self, instance):
        return int(instance.num_t)
    num_trees.admin_order_field = 'num_t'
    num_trees.short_description = '# trees'

    def last_tree(self, instance):
        return instance.last_t
    last_tree.admin_order_field = 'last_t'
    last_tree.short_description = 'Last tree'

    def sentence(self, instance):
        url = reverse('sentence', args=(instance.id,))
        return '<a href="%s">%s</a>' % (url, unicode(instance))
    sentence.allow_tags = True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return request.user.is_staff or request.user.is_superuser
        return request.user.is_superuser

    def queryset(self, request):
        qs = super(SentenceAdmin, self).queryset(request)
        return qs.annotate(num_a=Count('assignments'),
                num_t=Count('assignments__latest_tree'),
                last_t=Max('assignments__latest_tree__date'),
                )

site.register(Sentence, SentenceAdmin)


class AssignmentAdmin(admin.ModelAdmin):
    fields = ('sentence', 'user', 'creation_date', 'completion_date')
    readonly_fields = ('sentence', 'user', 'creation_date')
    list_display = ('id', 'user', '__unicode__', 'creation_date',
            'completion_date')
    list_display_links = ('id', '__unicode__')
    date_hierarchy = 'completion_date'
    list_filter = ('user', 'latest_tree__state')
    list_select_related = True
    search_fields = ('sentence__text', 'user__username', 'user__first_name',
            'user__last_name')

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return self.readonly_fields

site.register(Assignment, AssignmentAdmin)


class TreeAdmin(admin.ModelAdmin):
    readonly_fields = ('assignment',)
    list_filter = ('state',)
    list_select_related = True

site.register(Tree, TreeAdmin)


class FlatPageCustom(FlatPageAdmin):
    formfield_overrides = {
        TextField: {'widget': CKEditorWidget}
    }

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

site.register(FlatPage, FlatPageCustom)
