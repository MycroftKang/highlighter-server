import datetime

import jwt
import rest_framework.exceptions
from app.settings import SECRET_KEY
from django.db.models.query import QuerySet
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from highlighter.predict import Predictor
from highlighter.utils.load import DataSetLoader
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HighlightRange, UserVote, Video

dsloader = DataSetLoader()
predictor = Predictor()


class HighlighterModelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get highlight ranges",
        manual_parameters=[
            openapi.Parameter(
                "vid",
                openapi.IN_PATH,
                "Video ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                "Maximum number of highlight ranges",
                type=openapi.TYPE_INTEGER,
                maximum=10,
                minimum=1,
                default=3,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                "",
                examples={
                    "application/json": {
                        "id": 782734234,
                        "duration": 34093,
                        "highlights": [
                            {
                                "id": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                                "start": 1905,
                                "end": 1955,
                                "probability": 0.8838140368461609,
                                "upvoted": True,
                                "downvoted": False,
                            }
                        ],
                    },
                },
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "",
                examples={
                    "application/json": {
                        "detail": "Not Found",
                        "notice": "Highlighter is not yet supported for this video",
                    },
                },
            ),
        },
    )
    def get(self, request: Request, vid: int):
        limit = request.GET.get("limit")

        if limit is None:
            limit = 3
        else:
            limit = int(limit)

        if limit > 10:
            limit = 10

        vcd = dsloader.load_chats_by_vid(vid)

        if vcd is None:
            return Response(
                {
                    "detail": "Not Found",
                    "notice": "Highlighter is not yet supported for this video",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        vd, _ = Video.objects.get_or_create(id=vcd.vid, duration=vcd.vlen)

        vcd = dsloader.load_chats_by_vid(vid)
        vranges = predictor.get_highlight_ranges(vcd, limit)

        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(days=1, seconds=5)

        vote_query_list: QuerySet = vd.highlight_ranges.filter(
            highlight_range_votes__user=request.user,
            start__in=[d[0] for d in vranges],
            end__in=[d[1] for d in vranges],
        ).values_list("start", "end", "highlight_range_votes__vote_type")

        payload = {
            "aud": str(request.user.id),
            "exp": now + delta,
            "iat": now,
            "vid": vcd.vid,
        }

        hls = [
            {
                "id": jwt.encode(
                    {
                        **payload,
                        "hs": v[0],
                        "he": v[1],
                    },
                    SECRET_KEY,
                    algorithm="HS256",
                ),
                "start": v[0],
                "end": v[1],
                "probability": v[2],
                "upvoted": (v[0], v[1], UserVote.VoteType.UPVOTE) in vote_query_list,
                "downvoted": (v[0], v[1], UserVote.VoteType.DOWNVOTE)
                in vote_query_list,
            }
            for v in vranges
        ]

        return Response(
            {
                "id": vcd.vid,
                "duration": vcd.vlen,
                "highlights": hls,
            },
        )


class HighlightVoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Vote a highlight range",
        manual_parameters=[
            openapi.Parameter(
                "action",
                openapi.IN_PATH,
                "Voting type",
                type=openapi.TYPE_STRING,
                enum=["upvote", "downvote", "removevote"],
            ),
        ],
        request_body=openapi.Schema(
            properties={
                "id": openapi.Schema(
                    description="Highlight range ID", type=openapi.TYPE_STRING
                )
            },
            required=["id"],
            example={
                "id": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            },
            type=openapi.TYPE_OBJECT,
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                "",
                examples={
                    "application/json": {
                        "notice": "Upvoted this highlight video",
                    },
                },
            ),
        },
    )
    def post(self, request: Request, action):
        try:
            payload = jwt.decode(
                request.data["id"],
                SECRET_KEY,
                audience=str(request.user.id),
                algorithms="HS256",
            )
        except jwt.ExpiredSignatureError as e:
            print(e)
            raise rest_framework.exceptions.ValidationError()
        except jwt.InvalidTokenError as e:
            print(e)
            raise rest_framework.exceptions.ValidationError()

        vd = Video.objects.get(id=payload["vid"])
        hrange, _ = HighlightRange.objects.get_or_create(
            start=payload["hs"], end=payload["he"], video=vd
        )

        if action == "upvote":
            msg = hrange.upvote(request.user)
        elif action == "downvote":
            msg = hrange.downvote(request.user)
        elif action == "removevote":
            msg = hrange.remove_vote(request.user)
        else:
            raise Http404

        return Response({"notice": msg}, status=status.HTTP_200_OK)
