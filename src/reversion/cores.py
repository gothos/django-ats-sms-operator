from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from is_core.main import UIRestModelISCore
from is_core.generic_views.inlines.inline_objects_views import TabularInlineObjectsView

from reversion.models import Revision, Version


class DataRevisionIsCore(UIRestModelISCore):
    abstract = True

    model = Revision
    list_display = ('created_at', 'user', 'comment')
    rest_list_fields = ('pk',)
    rest_list_obj_fields = ('pk',)
    menu_group = 'data-revision'

    form_fieldsets = (
        (None, {'fields': ('created_at', 'user', 'comment')}),
        (_('Versions'), {'inline_view': 'VersionInlineFormView'}),
    )
    form_readonly_fields = ('V', 'user', 'comment', 'serialized_data')

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class VersionInlineFormView(TabularInlineObjectsView):
        model = Version
        fields = (
            ('type', _('type')),
            ('content_type', _('content type')),
            ('object', _('object')),
            ('data', _('data')),
        )

        def parse_object(self, obj):
            return {'type': obj.get_type_display(), 'object': self.get_object(obj), 'content_type': obj.content_type,
                    'data': ', '.join(('%s: %s' % (k, v if v != '' else '--') for k, v in obj.flat_field_dict.items()))}
        
        def get_object(self, version):
            obj = version.object
            if (obj and hasattr(getattr(obj, 'get_absolute_url', None), '__call__')
                and hasattr(getattr(obj, 'can_see_edit_link', None), '__call__') and
                obj.can_see_edit_link(self.request)):
                    return '<a href="%s">%s</a>' % (obj.get_absolute_url(), force_text(obj))
            return obj

        def get_objects(self):
            return self.parent_instance.versions.all()


    form_inline_views = [VersionInlineFormView]