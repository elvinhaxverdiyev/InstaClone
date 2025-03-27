from rest_framework import serializers

from .models import HashTag

class HashTagSerializer(serializers.ModelSerializer):
    """
    Serializer for the HashTag model.

    **Fields:**
    - `id`: Unique identifier of the hashtag (automatically included).
    - `name`: The unique name of the hashtag.

    **Usage:**
    - Converts `HashTag` model instances into JSON format.
    - Can be used for both serialization and deserialization.
    """
    class  Meta:
        model = HashTag
        fields = "__all__"