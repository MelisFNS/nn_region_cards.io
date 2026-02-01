from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.db.models import Q, F

from .models import CityCard


class CityListView(ListView):
    model = CityCard
    template_name = "cards/city_list.html"
    context_object_name = "cards"

    def get_queryset(self):
        sort = self.request.GET.get("sort", "pop")
        q = (self.request.GET.get("q") or "").strip()

        qs = CityCard.objects.all()

        # ✅ поиск
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(region__icontains=q)
            )

        # ✅ сортировки
        if sort == "new":
            return qs.order_by("-created_at")

        if sort == "title":
            return qs.order_by("title")

        # ✅ по умолчанию сортировка по населению (большие сверху)
        return qs.order_by("-population", "-created_at")


class CityDetailView(DetailView):
    model = CityCard
    template_name = "cards/city_detail.html"
    context_object_name = "card"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        # ✅ +1 просмотр (безопасно для конкурентных запросов)
        CityCard.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)

        # обновим объект, чтобы в шаблоне показалось актуально
        obj.refresh_from_db(fields=["views_count"])
        return obj


@login_required
def city_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        region = request.POST.get("region", "").strip()
        short_description = request.POST.get("short_description", "").strip()
        content = request.POST.get("content", "").strip()

        population = request.POST.get("population") or None
        lat = request.POST.get("lat") or None
        lon = request.POST.get("lon") or None
        image = request.FILES.get("image")

        card = CityCard(
            title=title,
            region=region,
            short_description=short_description,
            content=content,
            population=population,
            lat=lat,
            lon=lon,
            image=image,

            # ✅ ВОТ ЭТО убирает NOT NULL author_id
            author=request.user,
        )
        card.save()
        return redirect("city_detail", slug=card.slug)

    return render(request, "cards/city_form.html", {"mode": "create"})


@login_required
def city_edit(request, slug):
    card = get_object_or_404(CityCard, slug=slug)

    if request.method == "POST":
        card.title = request.POST.get("title", "").strip()
        card.region = request.POST.get("region", "").strip()
        card.short_description = request.POST.get("short_description", "").strip()
        card.content = request.POST.get("content", "").strip()

        card.population = request.POST.get("population") or None
        card.lat = request.POST.get("lat") or None
        card.lon = request.POST.get("lon") or None

        new_image = request.FILES.get("image")
        if new_image:
            card.image = new_image

        # если slug был пустой/битый — пересоздастся автоматически в model.save()
        card.slug = card.slug or ""
        card.save()
        return redirect("city_detail", slug=card.slug)

    return render(request, "cards/city_form.html", {"mode": "edit", "card": card})


# ✅ удалить может ЛЮБОЙ залогиненный пользователь (не только автор)
@login_required
def city_delete(request, slug):
    card = get_object_or_404(CityCard, slug=slug)

    if request.method == "POST":
        card.delete()
        return redirect("city_list")

    return render(request, "cards/city_confirm_delete.html", {"card": card})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("city_list")
    else:
        form = UserCreationForm()

    return render(request, "cards/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("city_list")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("city_list")
