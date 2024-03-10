from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpRequest, HttpResponseForbidden
from django.core.handlers.wsgi import WSGIRequest

from .models import Note, User, Tag
from .service import create_note, filter_notes, queryset_optimization


def home_page_view(request: HttpRequest):
    """
    Обязательно! Каждая функция view должна принимать первым параметром request.
    """
    queryset = queryset_optimization(Note.objects.all())

    print(queryset.query)

    return render(request, "home.html", {"notes": queryset[:100]})


def filter_notes_view(request: WSGIRequest):
    """
    Фильтруем записи по запросу пользователя.
    HTTP метод - GET.
    Обрабатывает URL вида: /filter/?search=<text>
    """

    search: str = request.GET.get("search", "")  # `get` - получение по ключу. Если такого нет, то - "",
    queryset = queryset_optimization(
        filter_notes(search)
    )

    context: dict = {
        "notes": queryset[:100],
        "search_value_form": search,
    }
    return render(request, "home.html", context)

@login_required
def create_note_view(request: WSGIRequest):

    if request.method == "POST":
        note = create_note(request)
        return HttpResponseRedirect(reverse('show-note', args=[note.uuid]))

    # Вернется только, если метод не POST.
    return render(request, "create_form.html")

def show_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)  # Получение только ОДНОЙ записи.

    except Note.DoesNotExist:
        # Если не найдено такой записи.
        raise Http404

    return render(request, "note.html", {"note": note})


def update_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)

        if note.user != request.user:
            return HttpResponseForbidden("Запрещено!")

        if request.method == "POST":
            note.title = request.POST.get("title")
            note.content = request.POST.get("content")
            note.mod_time = timezone.now()
            if request.FILES.get("noteImage"):
                if note.image:
                    note.image.delete()
                note.image = request.FILES.get("noteImage")

            note.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "updatenote.html", {"note": note})
    except Note.DoesNotExist:
        raise Http404

def edit_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)
    except Note.DoesNotExist:
        raise Http404

    if note.user != request.user:
        return HttpResponseForbidden("Запрещено!")

    if request.method == "POST":
        note.title = request.POST["title"]
        note.content = request.POST["content"]
        note.mod_time = timezone.now()
        if request.FILES.get("noteImage"):
            if note.image:
                note.image.delete()
            note.image = request.FILES.get("noteImage")
        note.save()
        return HttpResponseRedirect(reverse('show-note', args=[note.uuid]))
    return render(request, "edit_form.html", {"note": note})

def delete_note_view(request: WSGIRequest, note_uuid):
    note = Note.objects.get(uuid=note_uuid)
    if note.user != request.user:
        return HttpResponseForbidden("Запрещено!")

    if request.method == "POST":
        Note.objects.filter(uuid=note_uuid).delete()
    return HttpResponseRedirect(reverse("home"))

def user_notes(request: WSGIRequest, username: str):
    queryset = queryset_optimization(
        Note.objects.filter(user__username=username)
    )
    # SELECT * FROM "posts_note"
    # INNER JOIN "users" ON ("posts_note"."user_id" = "users"."id")
    # WHERE "users"."username" = boris1992
    # ORDER BY "posts_note"."created_at" DESC

    print(Note.objects.filter(user__username=username).query)

    return render(request, "posts-list.html", {"notes": queryset})


def register(request: WSGIRequest):
    if request.method != "POST":
        return render(request, "registration/register.html")
    print(request.POST)
    if not request.POST.get("username") or not request.POST.get("email") or not request.POST.get("password1"):
        return render(
            request,
            "registration/register.html",
            {"errors": "Укажите все поля!"}
        )
    print(User.objects.filter(
            Q(username=request.POST["username"]) | Q(email=request.POST["email"])
    ))
    # Если уже есть такой пользователь с username или email.
    if User.objects.filter(
            Q(username=request.POST["username"]) | Q(email=request.POST["email"])
    ).count() > 0:
        return render(
            request,
            "registration/register.html",
            {"errors": "Если уже есть такой пользователь с username или email"}
        )

    # Сравниваем два пароля!
    if request.POST.get("password1") != request.POST.get("password2"):
        return render(
            request,
            "registration/register.html",
            {"errors": "Пароли не совпадают"}
        )

    # Создадим учетную запись пользователя.
    # Пароль надо хранить в БД в шифрованном виде.
    User.objects.create_user(
        username=request.POST["username"],
        email=request.POST["email"],
        password=request.POST["password1"]
    )
    return HttpResponseRedirect(reverse('home'))

def show_about_view(request: WSGIRequest):
    return render(request, "about.html")

@login_required
def profile_view(request: WSGIRequest, username: str):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return HttpResponseForbidden("Запрещено")

    if request.method == "POST":
        user = User.objects.get(username=username)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.phone = request.POST.get("phone", user.phone)
        user.save()
        return HttpResponseRedirect(reverse("home", ))
    user = User.objects.get(username=username)
    tags_queryset = Tag.objects.filter(notes__user=user).distinct()

    return render(request, 'profile.html', {'tags': tags_queryset})

