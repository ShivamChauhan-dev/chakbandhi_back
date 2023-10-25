from django.contrib import admin


class CreatorAdminMixin(admin.ModelAdmin):
    exclude = ['creator']

    def get_list_display(self, request):
        return super().get_list_display(request) + ('creator', 'modified_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        else:
            obj.modified_by = request.user
        obj.save()
