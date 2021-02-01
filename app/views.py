from django.http import JsonResponse
from rest_framework.views import exception_handler


def Http404(request, exception=None):
    return JsonResponse(
        {"detail": "Not found."}, status=404, json_dumps_params={"indent": 2}
    )


