from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
from .pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q, Max
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from datetime import datetime, timedelta

def index(request):
    return render(request, 'index.html')

class CompaniesView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['name']
    search_fields = ['name','location']
    pagination_class = CustomPageNumberPagination

class SingleCompanyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Company.objects.filter(id=self.kwargs['pk'])

class CompanyQuestionsView(generics.ListCreateAPIView):
    queryset = CompanyQuestions.objects.all()
    serializer_class = CompanyQuestionsSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['company__name']
    filter_fields = ['company__id']
    search_fields = ['company__name', 'question']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        company_id = self.request.query_params.get('company__id', None)
        if company_id:
            self.queryset = self.queryset.filter(company__id=company_id)
        return self.queryset
    
class SingleCompanyQuestionView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyQuestions.objects.all()
    serializer_class = CompanyQuestionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CompanyQuestions.objects.filter(id=self.kwargs['pk'])

class EmployeesView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['name']
    filter_fields = ['company__id']
    search_fields = ['name', 'job_title', 'company__name', 'contacted']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Employee.objects.filter(user=self.request.user)
        company_id = self.request.query_params.get('company__id', None)
        if company_id:
            queryset = queryset.filter(company__id=company_id)
        return queryset
    
class SingleEmployeeView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Employee.objects.filter(id=self.kwargs['pk'], user=self.request.user)
    

class ApplicationsView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['submission_date']
    filter_fields = ['company__id', 'submission_date', 'status']
    search_fields = ['job_title', 'company__name', 'status']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset =  Application.objects.filter(user=self.request.user)
        company_id = self.request.query_params.get('company__id', None)
        submission_date = self.request.query_params.get('submission_date', None)
        status = self.request.query_params.get('status', None)
        if company_id:
            queryset = queryset.filter(company__id=company_id)
        if submission_date:
            queryset = queryset.filter(submission_date=submission_date)
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
class SingleApplicationView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(id=self.kwargs['pk'], user=self.request.user)
    
class QuestionsView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['application__submission_date']
    filter_fields = ['application__id']
    search_fields = ['question', 'application__job_title', 'application__company__name']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset =  Question.objects.filter(user=self.request.user)
        application_id = self.request.query_params.get('application__id', None)
        if application_id:
            queryset = queryset.filter(application__id=application_id)
        return queryset
    
class SingleQuestionView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(id=self.kwargs['pk'], user=self.request.user)
    
class TodoListView(generics.ListCreateAPIView):
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['completed']
    search_fields = ['application_title']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return TodoList.objects.filter(user=self.request.user)
    
class SingleTodoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TodoList.objects.filter(id=self.kwargs['pk'], user=self.request.user)

class StatisticsView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        stats = Application.objects.filter(user=user).aggregate(
            total_applications=Count('id'),
            pending_applications=Count('id', filter=~Q(status=ApplicationStatus.REJECTED.name) & ~Q(status=ApplicationStatus.ACCEPTED.name)),
            rejected_applications=Count('id', filter=Q(status=ApplicationStatus.REJECTED.name)),
            accepted_applications=Count('id', filter=Q(status=ApplicationStatus.ACCEPTED.name)),
            last_application=Max('submission_date'),
            last_rejection=Max('submission_date', filter=Q(status=ApplicationStatus.REJECTED.name)),
            last_acceptance=Max('submission_date', filter=Q(status=ApplicationStatus.ACCEPTED.name)),
            last_pending=Max('submission_date', filter=~Q(status=ApplicationStatus.REJECTED.name) & ~Q(status=ApplicationStatus.ACCEPTED.name)),
        )

        return Response(stats)
    
class PercentsView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Aggregate in a single query
        stats = Application.objects.filter(user=user, status__in=[ApplicationStatus.ACCEPTED.name, ApplicationStatus.REJECTED.name]).aggregate(
            total_applications=Count('id'),
            applied_stage=Count('id', filter=Q(stage=Stage.APPLIED.name)),
            phonescreen_stage=Count('id', filter=Q(stage=Stage.PHONE_SCREEN.name)),
            assessment_stage=Count('id', filter=Q(stage=Stage.ASSESSMENT.name)),
            interview_stage=Count('id', filter=Q(stage=Stage.INTERVIEW.name)),
            offer_stage=Count('id', filter=Q(stage=Stage.OFFER.name)),
        )

        total = max(stats['total_applications'],1)
        for key in stats:
            stats[key] = round((stats[key]/total)*100, 2)

        return Response(stats)


class TimeSeriesView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        interval = request.query_params.get('interval', 'month')
        points = int(request.query_params.get('points', 12))
        start_date = request.query_params.get('start_date', request.user.date_joined.strftime('%Y-%m-%d'))
        if interval not in ['month', 'week', 'day']:
            return Response({'error': 'Invalid interval. Choose from: month, week, day'}, status=400)
        if points < 1 or points>100:
            return Response({'error': 'Invalid number of points Choose from 1 to 100'}, status=400)
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return Response({'error': 'Invalid date format. Use: YYYY-MM-DD'}, status=400)
        
        if interval=='day':
            trunc_func = TruncDay
            if not start_date:
                start_date = datetime.now() - timedelta(days=points-1)
            date_str = '%Y-%m-%d'
        elif interval == 'week':
            trunc_func = TruncWeek
            if not start_date:
                start_date = datetime.now() - timedelta(weeks=points)
            start_date = start_date - timedelta(days=start_date.weekday())
            date_str = '%Y-%m-W%W'
        else:
            trunc_func = TruncMonth
            if not start_date:
                start_date = datetime.now().replace(day=1) - timedelta(weeks=4*(points-1))
            date_str = '%Y-%m'

        data = Application.objects.filter(user=user, submission_date__gte=start_date).annotate(date=trunc_func('submission_date')).values('date').annotate(
            total_applications=Count('id'),
            rejections=Count('id', filter=models.Q(status=ApplicationStatus.REJECTED.name)),
            acceptances=Count('id', filter=models.Q(status=ApplicationStatus.ACCEPTED.name)),
        ).order_by('date')[:points]

        results = []
        j = 0
        for i in range(points):
            if interval == 'day':
                date_point = start_date + timedelta(days=i)
            elif interval == 'week':
                date_point = start_date + timedelta(weeks=i)
            else:
                date_point = start_date + timedelta(weeks=4*i)
            date_point = date_point.date()
            if j>=len(data) or data[j]['date'] != date_point:
                results.append({
                    'date': date_point.strftime(date_str),
                    'total_applications': 0,
                    'rejections': 0,
                    'acceptances': 0
                })
            else:
                results.append({
                    'date': data[j]['date'].strftime(date_str),
                    'total_applications': data[j]['total_applications'],
                    'rejections': data[j]['rejections'],
                    'acceptances': data[j]['acceptances']
                })
                j+=1


        response_data ={
            "points" : points,
            "start_date" : start_date.strftime(date_str),
            "interval" : interval,
            "results": results,
        }

        return Response(response_data)
