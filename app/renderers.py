from rest_framework import renderers


class JSONRenderer(renderers.JSONRenderer):
    def get_indent(self, accepted_media_type, renderer_context):
        if accepted_media_type:
            # If the media type looks like 'application/json; indent=4',
            # then pretty print the result.
            # Note that we coerce `indent=0` into `indent=None`.
            base_media_type, params = renderers.parse_header(
                accepted_media_type.encode("ascii")
            )
            try:
                return renderers.zero_as_none(max(min(int(params["indent"]), 8), 0))
            except (KeyError, ValueError, TypeError):
                pass

        # If 'indent' is provided in the context, then pretty print the result.
        # E.g. If we're being called by the BrowsableAPIRenderer.
        return renderer_context.get("indent", 2)
