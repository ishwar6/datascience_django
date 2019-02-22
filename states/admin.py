from django.contrib import admin
from django.db.models.functions import Lower
from states.models import *


class NodeInline(admin.TabularInline):
    model = Node.state_node.through


class StateAdmin(admin.ModelAdmin):

    def get_ordering(self, request):
        return [Lower('tag')]  # sort case insensitive

    list_display = ('title', 'chapter', 'pk', 'tag', 'chapter')
    inlines = [
        NodeInline,
    ]


class NodeAdmin(admin.ModelAdmin):

    inlines = [
        NodeInline,
    ]
    exclude = ('state_node',)


class IllustrationInline(admin.StackedInline):
    model = Illustration
    can_delete = False
    verbose_name_plural = 'Illustration'
    fk_name = 'content'


class ContentAdmin(admin.ModelAdmin):
    inlines = (IllustrationInline, )


admin.site.register(State, StateAdmin)
admin.site.register(Node, NodeAdmin)

admin.site.register(Chapter)
admin.site.register(Content, ContentAdmin)
