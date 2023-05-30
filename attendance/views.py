import os
import uuid
import pickle
import shutil
import face_recognition
import numpy as np
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from django.http import HttpResponse

import cv2
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import RegisterUserSerializer,LoginSerializer
from rest_framework import status

from .models import AttendanceLog, RegisteredUser


MEDIA_ROOT = 'media/'


@csrf_exempt
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        file = serializer.validated_data['file']
        name= serializer.validated_data['text']
        file.name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(MEDIA_ROOT, file.name)
        with open(image_path, "wb") as f:
            f.write(file.read())

        user_name, match_status = recognize(face_recognition.load_image_file(image_path),name)

        if match_status:
            attendance_log = AttendanceLog(user=user_name, status='IN')
            attendance_log.save()

        os.remove(image_path)

        return Response({'user': user_name, 'match_status': match_status})

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@csrf_exempt
def logout(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        file = serializer.validated_data['file']
        name= serializer.validated_data['text']
        file.name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(MEDIA_ROOT, file.name)
        with open(image_path, "wb") as f:
            f.write(file.read())

        user_name, match_status = recognize(face_recognition.load_image_file(image_path),name)

        if match_status:
            attendance_log = AttendanceLog(user=user_name, status='IN')
            attendance_log.save()

        os.remove(image_path)

        return Response({'user': user_name, 'match_status': match_status})

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@csrf_exempt
def register_new_user(request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid():
        registered_user = serializer.save()
        
        # Assuming you have a registered user with ID 1
        registered_user = RegisteredUser.objects.get(name=serializer.validated_data['text'])

        # Retrieve the embeddings binary data
        embeddings_binary = registered_user.embeddings

        # Decode the embeddings using pickle
        embeddings = pickle.loads(embeddings_binary)

        return Response({'registration_status': 200, 'embeddings': embeddings})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_attendance_logs(request):
    filename = 'out.zip'
    logs_directory = os.path.join(MEDIA_ROOT, 'logs')

    shutil.make_archive(filename[:-4], 'zip', logs_directory)

    with open(filename, 'rb') as f:
        response = HttpResponse(f, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def recognize(img,name):
    # Assume there will be at most 1 match in the database

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found', False
    else:
        embeddings_unknown = embeddings_unknown[0]
        print("UNknown-user-embedings",embeddings_unknown)


    registered_user = RegisteredUser.objects.get(name=name)
    embeddings = pickle.loads(registered_user.embeddings)
    embeddings = np.array(embeddings)  # Convert to NumPy array
    print("known-user-embedings",embeddings)

    # Normalize embeddings
    known_embedding = embeddings / np.linalg.norm(embeddings)
    unknown_embedding = embeddings_unknown / np.linalg.norm(embeddings_unknown)

    # Reshape embeddings to 2D arrays
    # Reshape embeddings to 1D arrays
    known_embedding = known_embedding.reshape(-1)
    unknown_embedding = unknown_embedding.reshape(-1)
    print("Resahped_known-user-embedings",known_embedding)
    print("reshaped_UNknown-user-embedings",unknown_embedding)

    threshold = 0.  # Adjust the threshold based on your requirements

    # Compute cosine similarity
    similarity = cosine_similarity([known_embedding], [unknown_embedding])
    print(similarity)

    if similarity > threshold:
        return registered_user.name, True

    return 'unknown_person', False

