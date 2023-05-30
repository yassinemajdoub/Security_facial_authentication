import os
import uuid
import pickle
import face_recognition
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from django.http import HttpResponse

import cv2
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import RegisterUserSerializer,LoginSerializer,fetchmodelSerializer
from rest_framework import status
from scipy.spatial.distance import euclidean
import pandas as pd


from .models import AttendanceLog, RegisteredUser


MEDIA_ROOT = 'media/'


@csrf_exempt
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        file = serializer.validated_data['file']

        file.name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(MEDIA_ROOT, file.name)
        with open(image_path, "wb") as f:
            f.write(file.read())

        user_name, match_status = recognize(face_recognition.load_image_file(image_path))

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
       
        file.name = f"{uuid.uuid4()}.png"

        image_path = os.path.join(MEDIA_ROOT, file.name)
        with open(image_path, "wb") as f:
            f.write(file.read())

        user_name, match_status = recognize(face_recognition.load_image_file(image_path))

        if match_status:
            attendance_log = AttendanceLog(user=user_name, status='OUT')
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

@api_view(['get'])
@csrf_exempt
def fetchROLE(request):
    try:
        current_user_name = AttendanceLog.objects.last().user
        print(current_user_name)
        current_user = RegisteredUser.objects.get(name=current_user_name)
        fetching_status = "Success"  # Example success status
        # Serialize the RegisteredUser object
        serializer = fetchmodelSerializer(current_user)
        serialized_user = serializer.data

        return Response({'fetching_status': fetching_status, 'current_user': serialized_user})
    except Exception as e:
        error_message = str(e)  # Get the error message
        return Response({'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_attendance_logs(request):
    logs = AttendanceLog.objects.all()

    # Create a DataFrame from the AttendanceLog objects
    data = {
        'User': [log.user for log in logs],
        'Status': [log.status for log in logs],
    }
    df = pd.DataFrame(data)

    # Convert the DataFrame to Excel
    excel_file = 'attendance_logs.xlsx'
    df.to_excel(excel_file, index=False)

    # Serve the Excel file as a download
    with open(excel_file, 'rb') as f:
        response = HttpResponse(f, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{excel_file}"'
        return response

    

def compare_faces(face1, face2):
    distance = euclidean(face1, face2)
    similarity_score = 1 / (1 + distance)
    return distance,similarity_score

def recognize(img):
    # Assume there will be at most 1 match in the database

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found', False
    else:
        embeddings_unknown = embeddings_unknown[0]
        print("UNknown-user-embedings",embeddings_unknown)


    registered_users = RegisteredUser.objects.all()
    best_score = 0
    best_user = None
    

    for registered_user in registered_users:
        embeddings = pickle.loads(registered_user.embeddings)
        embeddings = np.array(embeddings)  # Convert to NumPy array
        embeddings = embeddings.reshape(-1)

        distance, similarity_score = compare_faces(embeddings, embeddings_unknown)

        print(f"The similarity score for user {registered_user.name} is: {similarity_score}")

        if similarity_score > best_score:
            best_score = similarity_score
            best_user=registered_user.name
            

    threshold = 0.7  # Adjust the threshold based on your requirements

    if best_score > threshold:
        return best_user, True

    return 'unknown_person', False

