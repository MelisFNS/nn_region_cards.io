from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class CityCard(models.Model):
    title = models.CharField("Город", max_length=200)
    region = models.CharField("Регион", max_length=200)

    slug = models.SlugField(unique=True, max_length=255, blank=True)

    image = models.ImageField(upload_to="cities/", blank=True, null=True)

    population = models.PositiveIntegerField(blank=True, null=True)

    short_description = models.TextField(blank=True)
    content = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # автор обязателен (под твою текущую БД)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="city_cards")

    # ✅ статистика просмотров
    views_count = models.PositiveIntegerField(default=0)

    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # ✅ генерируем slug, если пустой
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)
            if not base:
                base = "city"

            slug = base
            i = 2
            while CityCard.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
