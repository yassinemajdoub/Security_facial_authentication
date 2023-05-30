from django.urls import path

from attendance.views import login, logout, register_new_user, get_attendance_logs,fetchROLE

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register_new_user, name='register'),
    path('attendance-logs/', get_attendance_logs, name='attendance_logs'),
    path('fetch_role/', fetchROLE, name='fetchROLE'),
]
