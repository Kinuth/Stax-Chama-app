from rest_framework import viewsets, status, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Loan, ChamaGroup, Membership
from .serializers import LoanSerializer, UserSerializer, ChamaGroupSerializer   
from django.shortcuts import render
import os
from django.conf import settings
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from api import models


def api_root(request):
    # Construct the path to your index.html in the static folder
    file_path = os.path.join(settings.BASE_DIR, 'static', 'index.html')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Frontend index.html not found in static folder.", status=404)
# Ensure 'index.html' is in a 'templates' folder or correctly linked

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

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
    serializer_class = ChamaGroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users should only see Chamas they are members of
        user = self.request.user
        return ChamaGroup.objects.filter(
            Q(members=user) | Q(chairman=user)
        ).distinct()
    
    def perform_create(self, serializer):
        # Automatically set the creator as the chairman
        group = serializer.save(chairman=self.request.user)
        # Add the creator as an approved member immediately
        Membership.objects.create(user=self.request.user, group=group, is_approved=True)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        group = self.get_object()
        members = group.members.all()
        return Response({
            "group_name": group.name,
            "total_balance": float(group.balance),
            "members": UserSerializer(members, many=True).data,
        })

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        group = self.get_object()
        phone = request.data.get('phone')
        # Logic to find user by phone and create a pending membership
        return Response({"message": "Invite sent"}, status=status.HTTP_200_OK)

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
    
class DashboardAnalyticsView(APIView):
    def get(self, request):
        # 1. Distribution Data (Pie/Donut Chart)
        # Calculates total funds currently out as loans vs cash in groups
        total_loaned = Loan.objects.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        total_savings = ChamaGroup.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        
        # 2. Monthly Trends (Bar/Line Chart)
        # Group loans by month for the last 6 months
        monthly_stats = (
            Loan.objects.filter(status='APPROVED')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_index('-month')[:6]
        )

        # 3. Recent Transactions (Table)
        recent_loans = Loan.objects.all().order_by('-created_at')[:5]
        transactions = [{
            "date": l.created_at.strftime("%Y-%m-%d"),
            "user": l.borrower.username,
            "amount": float(l.amount),
            "status": l.status
        } for l in recent_loans]

        return Response({
            "distribution": {
                "loaned": float(total_loaned),
                "savings": float(total_savings)
            },
            "monthly_trends": list(monthly_stats),
            "recent_transactions": transactions
        })