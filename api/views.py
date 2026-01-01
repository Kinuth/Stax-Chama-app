from rest_framework import viewsets, status, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Loan, ChamaGroup
from .serializers import LoanSerializer, UserSerializer, ChamaGroupSerializer   

from django.shortcuts import render

def api_root(request):
    return render(request, 'index.html') # Ensure 'index.html' is in a 'templates' folder or correctly linked

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """
        Allow anyone to create a user (register), but only admin can modify others.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ChamaGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Chama Groups (view, create, update, delete).
    """
    queryset = ChamaGroup.objects.all()
    serializer_class = ChamaGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Optionally: set the current user as the creator/admin of the group
        serializer.save(created_by=self.request.user)

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        loan = self.get_object()
        if loan.group.balance < loan.amount:
            return Response({'error': 'Insufficient group funds'}, status=status.HTTP_400_BAD_REQUEST)
        
        loan.status = 'APPROVED'
        loan.group.balance -= loan.amount
        loan.group.save()
        loan.save()
        return Response({'status': 'Loan Approved and Disbursed'})