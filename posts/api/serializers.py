from django.contrib.auth import get_user_model
from rest_framework import serializers
from posts.models import Note, Tag


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

class NoteSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer(read_only=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Note
        fields = ["uuid", "title", "created_at", "image", "tags", "user"]


    def create(self, validated_data) -> Note:
        tags = validated_data.pop("tags")
        note = Note.objects.create(**validated_data)

        tags_objects: list[Tag] = []

        for tag in tags:
            obj, created = Tag.objects.get_or_create(name=tag["name"])
            tags_objects.append(obj)

        note.tags.set(tags_objects)

        return note

class NoteListSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer(read_only=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Note
        fields = ["uuid", "title", "created_at", "image", "tags", "user"]


