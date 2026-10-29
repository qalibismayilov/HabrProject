
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Kateqoriya adı",
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL adı",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Kateqoriya"
        verbose_name_plural = "Kateqoriyalar"

    def __str__(self):
        return self.name


class Article(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Təsdiq gözləyir"
        PUBLISHED = "published", "Yayımlanıb"
        REJECTED = "rejected", "Rədd edilib"

    title = models.CharField(
        max_length=250,
        verbose_name="Başlıq",
    )

    image = models.ImageField(
        upload_to="articles/",
        verbose_name="Məqalə şəkli",
    )

    content = models.TextField(
        verbose_name="Məqalənin mətni",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Kateqoriya",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="Müəllif",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Yayımlanma statusu",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaradılma tarixi",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Son dəyişiklik tarixi",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_articles",
        verbose_name="Təsdiqləyən admin",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Təsdiq tarixi",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Məqalə"
        verbose_name_plural = "Məqalələr"

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        result = self.ratings.aggregate(
            average=Avg("value")
        )["average"]

        return round(result, 2) if result is not None else 0


class ArticleRating(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="Məqalə",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_ratings",
        verbose_name="İstifadəçi",
    )

    value = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name="Qiymət (1–5)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Qiymətləndirmə tarixi",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["article", "user"],
                name="unique_rating_per_user_article",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(value__gte=1)
                    & models.Q(value__lte=5)
                ),
                name="rating_value_between_1_and_5",
            ),
        ]
        verbose_name = "Məqalə qiyməti"
        verbose_name_plural = "Məqalə qiymətləri"

    def __str__(self):
        return f"{self.article.title}: {self.value}/5"


class ArticleVote(models.Model):
    class VoteType(models.TextChoices):
        LIKE = "like", "Bəyən"
        DISLIKE = "dislike", "Bəyənmə"

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name="Məqalə",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_votes",
        verbose_name="İstifadəçi",
    )

    vote_type = models.CharField(
        max_length=10,
        choices=VoteType.choices,
        verbose_name="Səs növü",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Səs tarixi",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["article", "user"],
                name="unique_vote_per_user_article",
            ),
        ]
        verbose_name = "Məqalə səsi"
        verbose_name_plural = "Məqalə səsləri"

    def __str__(self):
        return f"{self.user.username} - {self.article.title} - {self.vote_type}"


class Favorite(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Məqalə",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="İstifadəçi",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Əlavə edilmə tarixi",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["article", "user"],
                name="unique_favorite_per_user_article",
            ),
        ]
        ordering = ["-created_at"]
        verbose_name = "Seçilmiş məqalə"
        verbose_name_plural = "Seçilmiş məqalələr"

    def __str__(self):
        return f"{self.user.username} - {self.article.title}"


class ArticleRevision(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Təsdiq gözləyir"
        APPROVED = "approved", "Təsdiqlənib"
        REJECTED = "rejected", "Rədd edilib"

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name="Məqalə",
    )

    title = models.CharField(
        max_length=250,
        verbose_name="Yeni başlıq",
    )

    content = models.TextField(
        verbose_name="Yeni mətn",
    )

    image = models.ImageField(
        upload_to="article_revisions/",
        null=True,
        blank=True,
        verbose_name="Yeni şəkil",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="article_revisions",
        verbose_name="Yeni kateqoriya",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_revisions",
        verbose_name="Dəyişikliyi edən",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Dəyişiklik statusu",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Dəyişiklik tarixi",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_article_revisions",
        verbose_name="Yoxlayan admin",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Yoxlanılma tarixi",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Məqalə dəyişikliyi"
        verbose_name_plural = "Məqalə dəyişiklikləri"

    def __str__(self):
        return f"{self.article.title} — {self.get_status_display()}"
