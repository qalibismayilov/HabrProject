
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ArticleForm, ArticleRevisionForm
from .models import (
    Article,
    ArticleRating,
    ArticleRevision,
    ArticleVote,
    Category,
    Favorite,
)


def home(request):
    articles = Article.objects.filter(
        status=Article.Status.PUBLISHED
    ).select_related("author", "category")

    query = request.GET.get("q", "").strip()
    if query:
        articles = articles.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(author__username__icontains=query)
        )

    categories = Category.objects.all()
    return render(request, "articles/home.html", {
        "articles": articles,
        "categories": categories,
        "query": query,
    })


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if article.status != Article.Status.PUBLISHED:
        if not request.user.is_authenticated:
            return redirect("login")

        if not (
            request.user == article.author
            or request.user.is_staff
            or request.user.role in ["super_admin", "admin"]
        ):
            messages.error(request, "Bu məqaləyə baxmaq icazən yoxdur.")
            return redirect("home")

    votes = article.votes
    likes = votes.filter(vote_type=ArticleVote.VoteType.LIKE).count()
    dislikes = votes.filter(vote_type=ArticleVote.VoteType.DISLIKE).count()

    user_vote = None
    user_rating = None
    is_favorite = False

    if request.user.is_authenticated:
        user_vote = votes.filter(user=request.user).values_list(
            "vote_type", flat=True
        ).first()

        user_rating = ArticleRating.objects.filter(
            article=article, user=request.user
        ).values_list("value", flat=True).first()

        is_favorite = Favorite.objects.filter(
            article=article, user=request.user
        ).exists()

    return render(request, "articles/article_detail.html", {
        "article": article,
        "likes": likes,
        "dislikes": dislikes,
        "user_vote": user_vote,
        "user_rating": user_rating,
        "is_favorite": is_favorite,
    })


@login_required
def article_create(request):
    if request.user.is_blocked:
        messages.error(request, "Bloklanmış hesabla məqalə yarada bilməzsən.")
        return redirect("home")

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user

            if request.user.is_staff or request.user.role in [
                "super_admin", "admin"
            ]:
                article.status = Article.Status.PUBLISHED
                article.approved_by = request.user
                article.approved_at = timezone.now()
                messages.success(request, "Məqalə uğurla yayımlandı.")
            else:
                article.status = Article.Status.PENDING
                messages.success(
                    request,
                    "Məqalə yaradıldı. Admin təsdiqindən sonra yayımlanacaq."
                )

            article.save()
            return redirect("home")
    else:
        form = ArticleForm()

    return render(request, "articles/article_form.html", {
        "form": form,
        "page_title": "Yeni məqalə yarat",
        "button_text": "Məqaləni göndər",
    })


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if article.author != request.user and not (
        request.user.is_staff
        or request.user.role in ["super_admin", "admin"]
    ):
        messages.error(request, "Bu məqaləni redaktə etmək icazən yoxdur.")
        return redirect("article_detail", pk=pk)

    if request.user.is_blocked:
        messages.error(request, "Bloklanmış hesabla dəyişiklik edə bilməzsən.")
        return redirect("article_detail", pk=pk)

    if request.method == "POST":
        form = ArticleRevisionForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            revision = form.save(commit=False)
            revision.article = article
            revision.requested_by = request.user

            if request.user.is_staff or request.user.role in [
                "super_admin", "admin"
            ]:
                article.title = revision.title
                article.content = revision.content
                article.category = revision.category
                if revision.image:
                    article.image = revision.image
                article.approved_by = request.user
                article.approved_at = timezone.now()
                article.status = Article.Status.PUBLISHED
                article.save()
                messages.success(request, "Məqalə redaktə edildi.")
            else:
                revision.save()
                messages.success(
                    request,
                    "Dəyişiklik təklifin admin təsdiqinə göndərildi."
                )

            return redirect("article_detail", pk=pk)
    else:
        form = ArticleRevisionForm(initial={
            "title": article.title,
            "content": article.content,
            "category": article.category,
        })

    return render(request, "articles/article_form.html", {
        "form": form,
        "page_title": "Məqaləni redaktə et",
        "button_text": "Dəyişikliyi göndər",
        "article": article,
    })


@login_required
@require_POST
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if article.author != request.user and not (
        request.user.is_staff
        or request.user.role in ["super_admin", "admin"]
    ):
        messages.error(request, "Bu məqaləni silmək icazən yoxdur.")
        return redirect("article_detail", pk=pk)

    article.delete()
    messages.success(request, "Məqalə silindi.")
    return redirect("home")


@login_required
@require_POST
def vote_article(request, pk):
    article = get_object_or_404(
        Article, pk=pk, status=Article.Status.PUBLISHED
    )

    if request.user.is_blocked:
        messages.error(request, "Bloklanmış hesabla səs verə bilməzsən.")
        return redirect("article_detail", pk=pk)

    vote_type = request.POST.get("vote_type")

    if vote_type not in [
        ArticleVote.VoteType.LIKE,
        ArticleVote.VoteType.DISLIKE,
    ]:
        messages.error(request, "Səs növü düzgün deyil.")
        return redirect("article_detail", pk=pk)

    vote, created = ArticleVote.objects.get_or_create(
        article=article,
        user=request.user,
        defaults={"vote_type": vote_type},
    )

    if not created:
        if vote.vote_type == vote_type:
            vote.delete()
        else:
            vote.vote_type = vote_type
            vote.save(update_fields=["vote_type"])

    return redirect("article_detail", pk=pk)


@login_required
@require_POST
def rate_article(request, pk):
    article = get_object_or_404(
        Article, pk=pk, status=Article.Status.PUBLISHED
    )

    if request.user.is_blocked:
        messages.error(request, "Bloklanmış hesabla qiymət verə bilməzsən.")
        return redirect("article_detail", pk=pk)

    try:
        value = int(request.POST.get("value", ""))
    except (TypeError, ValueError):
        messages.error(request, "Qiymət 1-dən 5-ə qədər olmalıdır.")
        return redirect("article_detail", pk=pk)

    if value not in range(1, 6):
        messages.error(request, "Qiymət 1-dən 5-ə qədər olmalıdır.")
        return redirect("article_detail", pk=pk)

    ArticleRating.objects.update_or_create(
        article=article,
        user=request.user,
        defaults={"value": value},
    )

    messages.success(request, "Qiymətin qeydə alındı.")
    return redirect("article_detail", pk=pk)


@login_required
@require_POST
def toggle_favorite(request, pk):
    article = get_object_or_404(
        Article, pk=pk, status=Article.Status.PUBLISHED
    )

    if request.user.is_blocked:
        messages.error(request, "Bloklanmış hesabla seçilmişlərə əlavə edə bilməzsən.")
        return redirect("article_detail", pk=pk)

    favorite, created = Favorite.objects.get_or_create(
        article=article,
        user=request.user,
    )

    if created:
        messages.success(request, "Məqalə seçilmişlərə əlavə edildi.")
    else:
        favorite.delete()
        messages.success(request, "Məqalə seçilmişlərdən çıxarıldı.")

    return redirect("article_detail", pk=pk)


def popular_articles(request):
    articles = Article.objects.filter(
        status=Article.Status.PUBLISHED
    ).annotate(
        like_count=Count(
            "votes",
            filter=Q(votes__vote_type=ArticleVote.VoteType.LIKE),
        ),
        rating_average=Avg("ratings__value"),
    ).order_by("-like_count", "-rating_average", "-created_at")

    return render(request, "articles/popular.html", {
        "articles": articles,
    })


def category_list(request):
    categories = Category.objects.annotate(
        article_count=Count(
            "articles",
            filter=Q(articles__status=Article.Status.PUBLISHED),
        )
    )
    return render(request, "articles/categories.html", {
        "categories": categories,
    })


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    articles = Article.objects.filter(
        category=category,
        status=Article.Status.PUBLISHED,
    ).select_related("author", "category")

    return render(request, "articles/category_detail.html", {
        "category": category,
        "articles": articles,
    })


def author_list(request):
    from accounts.models import User

    authors = User.objects.filter(
        articles__status=Article.Status.PUBLISHED
    ).annotate(
        article_count=Count("articles", distinct=True)
    ).distinct().order_by("-article_count", "username")

    return render(request, "articles/authors.html", {
        "authors": authors,
    })


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(
        user=request.user,
        article__status=Article.Status.PUBLISHED,
    ).select_related("article", "article__author", "article__category")

    return render(request, "articles/favorites.html", {
        "favorites": favorites,
    })
