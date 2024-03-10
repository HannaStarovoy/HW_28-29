from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination

from posts.api.permissions import IsOwnerOrReadOnly
from posts.api.serializers import NoteSerializer, TagSerializer, NoteListSerializer
from posts.models import Note, Tag


class NoteListCreateAPIView(ListCreateAPIView):
    """
    Класс API view, для endpoint'a просмотра перечня рецептов и создания новых.
    """
    queryset = Note.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """В зависимости от метода HTTP возвращает соответствующий класс для создания сериализатора"""
        if self.request.method == 'POST':
            return NoteSerializer
        return NoteListSerializer

    def perform_create(self, serializer):
        """Во время создания рецепта добавляем владельца"""
        serializer.save(user=self.request.user)

class NoteDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    Класс API view, для endpoint'a просмотра, изменения и удаления одной заметки.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    lookup_field = "uuid"  # По какому (уникальному) полю модели будет найдена заметка.
    lookup_url_kwarg = "id"  # Какой параметр указать в urlpatterns, для поиска заметки.
    permission_classes = [IsOwnerOrReadOnly]


class TagListCreateAPIView(ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


