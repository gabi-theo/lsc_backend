from rest_framework.permissions import BasePermission


class IsCoordinator(BasePermission):
    def has_permission(self, request, view):
        print(request.user)
        print(request.user.role)
        return request.user.role == "coordinator"


class IsTrainer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "trainer"


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "student"
