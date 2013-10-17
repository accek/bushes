from django.contrib import admin
from django.db.models import Count
from django.core.urlresolvers import reverse
from bushes.models import Sentence, Assignment, Tree

class SentenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'identifier', 'sentence', 'length',
            'num_assignments', 'num_trees')
    list_display_links = ('id',)

    def length(self, instance):
        return len(instance.text.split())
    length.short_description = '# words'

    def num_assignments(self, instance):
        return int(instance.num_a)
    num_assignments.admin_order_field = 'num_a'
    num_assignments.short_description = '# assignments'

    def num_trees(self, instance):
        return int(instance.num_t)
    num_trees.admin_order_field = 'num_t'
    num_trees.short_description = '# trees'

    def sentence(self, instance):
        url = reverse('sentence', args=(instance.id,))
        return '<a href="%s">%s</a>' % (url, unicode(instance))
    sentence.allow_tags = True

    def queryset(self, request):
        qs = super(SentenceAdmin, self).queryset(request)
        return qs.annotate(num_a=Count('assignments'),
                num_t=Count('assignments__latest_tree'))

admin.site.register(Sentence, SentenceAdmin)

class AssignmentAdmin(admin.ModelAdmin):
    fields = ('sentence', 'user', 'completion_date')
    readonly_fields = ('sentence', 'user', 'creation_date')
    list_display = ('id', 'user', '__unicode__', 'completion_date')
    list_display_links = ('id', '__unicode__')
    date_hierarchy = 'completion_date'
    list_filter = ('user',)
    list_select_related = True
    search_fields = ('sentence__text', 'user__username', 'user__first_name',
            'user__last_name')

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return self.readonly_fields

admin.site.register(Assignment, AssignmentAdmin)

class TreeAdmin(admin.ModelAdmin):
    readonly_fields = ('assignment',)
    list_select_related = True

admin.site.register(Tree, TreeAdmin)
