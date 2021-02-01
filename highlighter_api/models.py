from django.db import models


class Video(models.Model):
    id = models.IntegerField(primary_key=True)
    duration = models.IntegerField()

    def __str__(self) -> str:
        return f"Video {self.id}"

    def __repr__(self) -> str:
        return f"Video object ({self.id})"


class VideoRange(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()

    class Meta:
        abstract = True


class HighlightRange(VideoRange):
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="highlight_ranges"
    )

    @property
    def upvote_count(self):
        return self.highlight_range_votes.filter(vote_type="UP").count()

    def upvote(self, user):
        self.highlight_range_votes: models.BaseManager

        self.highlight_range_votes.update_or_create(
            user=user,
            highlight_range=self,
            defaults={"vote_type": UserVote.VoteType.UPVOTE},
        )
        return "Upvoted this highlight video"

    def downvote(self, user):
        self.highlight_range_votes.update_or_create(
            user=user,
            highlight_range=self,
            defaults={"vote_type": UserVote.VoteType.DOWNVOTE},
        )
        return "Downvoted this highlight video"

    def remove_vote(self, user):
        uv = self.highlight_range_votes.filter(user=user, highlight_range=self).first()
        if uv is not None:
            vt = uv.vote_type
            uv.delete()
            if vt == UserVote.VoteType.UPVOTE:
                return "Removed from upvoted videos"
            else:
                return "Removed from downvoted videos"
        else:
            return "Removed from voted videos"

    def __str__(self) -> str:
        return f"HighlightRange ({self.video}, {self.start}, {self.end})"

    def __repr__(self) -> str:
        return f"HighlightRange object ({self.id}, {self.start}, {self.end})"

    class Meta:
        unique_together = ("video", "start", "end")


class UserVote(models.Model):
    class VoteType(models.TextChoices):
        UPVOTE = "UP", "Upvote"
        DOWNVOTE = "DOWN", "Downvote"

    user = models.ForeignKey(
        "auth.User", related_name="user_votes", on_delete=models.CASCADE
    )
    highlight_range = models.ForeignKey(
        HighlightRange, on_delete=models.CASCADE, related_name="highlight_range_votes"
    )
    vote_type = models.TextField(choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"UserVote ({self.user}, {self.highlight_range}, {self.vote_type})"

    def __repr__(self) -> str:
        return (
            f"UserVote object ({self.user}, {self.highlight_range}, {self.vote_type})"
        )

    class Meta:
        unique_together = ("user", "highlight_range")
