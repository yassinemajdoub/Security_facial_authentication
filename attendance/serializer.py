from rest_framework import serializers
import pickle
import uuid
import os
import shutil
import face_recognition
from .models import RegisteredUser

MEDIA_ROOT = 'media/'


class RegisterUserSerializer(serializers.Serializer):
    file = serializers.ImageField()
    text = serializers.CharField()
    usertype = serializers.CharField()

    def create(self, validated_data):
        file = validated_data['file']
        text = validated_data['text']
        role = validated_data['usertype']
        
        file.name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(MEDIA_ROOT, file.name)
        with open(image_path, "wb") as f:
            f.write(file.read())

        shutil.copy(image_path, os.path.join(MEDIA_ROOT, f'{text}.png'))

        embeddings = face_recognition.face_encodings(face_recognition.load_image_file(image_path))

        # Convert the embeddings list to binary using pickle
        embeddings_binary = pickle.dumps(embeddings[0])
        
        registered_user = RegisteredUser(name=text, image=file,embeddings=embeddings_binary,role=role)
        registered_user.save()

        os.remove(image_path)

        return registered_user
    
class LoginSerializer(serializers.Serializer):
    file = serializers.ImageField()    


class fetchmodelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredUser
        fields = ['name', 'role']  # Include the desired fields from your RegisteredUser model


