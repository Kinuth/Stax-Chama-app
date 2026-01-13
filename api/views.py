from rest_framework import viewsets, status, permissions
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Loan, ChamaGroup, Membership, Contribution
from .serializers import LoanSerializer, UserSerializer, ChamaGroupSerializer   
from django.shortcuts import render
import os
from django.conf import settings
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, ContributionSerializer
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
        
        members = [{
            "id": m.user.id,
            "username": m.user.username,
            "phone_number": getattr(m.user, 'phone_number', ''),
            "is_approved": m.is_approved
        } for m in Membership.objects.filter(group=group)]
        return Response({
            "group_name": group.name,
            "total_balance": float(group.balance),
            "members": members,  # Now includes pending members
        })
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        group = self.get_object()
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(phone_number=phone)
            Membership.objects.get_or_create(user=user, group=group, defaults={'is_approved': False})
            return Response({"message": "Invite sent and membership created"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this phone not found"}, status=status.HTTP_404_NOT_FOUND)

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Filter to only contributions for groups the user is a member/chairman of
        user = self.request.user
        return Contribution.objects.filter(
            Q(group__members=user) | Q(group__chairman=user)
        ).distinct()

    def perform_create(self, serializer):
        # 1. Save the contribution record
        contribution = serializer.save(member=self.request.user)
        
        # 2. Update the Chama's total balance
        group = contribution.group
        group.balance += contribution.amount
        group.save()

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Filter to only loans for groups the user is a member/chairman of
        user = self.request.user
        return Loan.objects.filter(
            Q(group__members=user) | Q(group__chairman=user)
        ).distinct()


    def perform_create(self, serializer):
        # Automatically set the borrower to the authenticated user
        serializer.save(borrower=self.request.user)

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

@action(methods=['get'], detail=False, permission_classes=[AllowAny])
def migrate_db(request):
    try:
        call_command('migrate', interactive=False)
        return HttpResponse("Migration successful", status=200)
    except Exception as e:
        return HttpResponse(f"Migration failed: {str(e)}", status=500)