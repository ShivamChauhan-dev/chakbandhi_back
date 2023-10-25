from rest_framework import renderers
from rest_framework.response import Response


class DataJSONRenderer(renderers.JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context: dict = None):
        view = renderer_context.get("view")
        response: Response = view.response

        if response.exception or hasattr(view, 'pagination_class') and view.pagination_class:
            return super().render(data, accepted_media_type, renderer_context)
        else:
            return super().render({"data": data}, accepted_media_type, renderer_context)
