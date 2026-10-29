
from django.contrib import admin
from django.utils import timezone

from .models import (
    Article,
    ArticleRating,
    ArticleRevision,
    ArticleVote,
    Category,
    Favorite,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "created_at",
        "approved_by",
    )

    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "content", "author__username")
    readonly_fields = ("created_at", "updated_at", "approved_at")
    list_select_related = ("author", "category", "approved_by")
    actions = ("approve_articles", "reject_articles")

    @admin.action(description="Seçilmiş məqalələri yayımla")
    def approve_articles(self, request, queryset):
        queryset.update(
            status=Article.Status.PUBLISHED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )

    @admin.action(description="Seçilmiş məqalələri rədd et")
    def reject_articles(self, request, queryset):
        queryset.update(
            status=Article.Status.REJECTED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )


@admin.register(ArticleRevision)
class ArticleRevisionAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "requested_by",
        "status",
        "created_at",
        "reviewed_by",
    )

    list_filter = ("status", "created_at")
    search_fields = ("article__title", "requested_by__username")
    readonly_fields = ("created_at",)
    list_select_related = ("article", "requested_by", "category")
    actions = ("approve_revisions", "reject_revisions")

    @admin.action(description="Seçilmiş dəyişiklikləri təsdiqlə")
    def approve_revisions(self, request, queryset):
        for revision in queryset.select_related("article", "category"):
            if revision.status != ArticleRevision.Status.PENDING:
                continue

            article = revision.article

            article.title = revision.title
            article.content = revision.content
            article.category = revision.category

            if revision.image:
                article.image = revision.image

            article.status = Article.Status.PUBLISHED
            article.approved_by = request.user
            article.approved_at = timezone.now()

            article.save()

            revision.status = ArticleRevision.Status.APPROVED
            revision.reviewed_by = request.user
            revision.reviewed_at = timezone.now()
            revision.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                ]
            )

    @admin.action(description="Seçilmiş dəyişiklikləri rədd et")
    def reject_revisions(self, request, queryset):
        for revision in queryset.filter(
            status=ArticleRevision.Status.PENDING
        ):
            revision.status = ArticleRevision.Status.REJECTED
            revision.reviewed_by = request.user
            revision.reviewed_at = timezone.now()
            revision.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                ]
            )


@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "value", "created_at")
    list_filter = ("value", "created_at")
    search_fields = ("article__title", "user__username")


@admin.register(ArticleVote)
class ArticleVoteAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "vote_type", "created_at")
    list_filter = ("vote_type", "created_at")
    search_fields = ("article__title", "user__username")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "created_at")
    search_fields = ("article__title", "user__username")
