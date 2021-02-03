from django.urls import path

from highlighter_api import views

urlpatterns = [
    path(
        "/v1/twitch/<int:vid>",
        views.HighlighterModelView.as_view(),
    ),
    path(
        "/v1/twitch/vote/<str:action>",
        views.HighlightVoteView.as_view(),
    ),
]
