from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User, Group
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.shortcuts import get_object_or_404

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CVSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CV
        fields = ['id', 'user', 'cv', 'submission_date', 'user_id']

    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value

    def validate(self, data):
        user_id = data.get('user_id')
        if user_id:
            cv_count = CV.objects.filter(user_id=user_id).count()
            if cv_count >= 5:
                raise serializers.ValidationError("User reached the maximum number of CVs")
        return data


class CompanySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Company
        fields = ['id', 'user', 'name', 'location', 'careers_link', 'linkedin_link', 'description', 'user_id']
        validators = [
            UniqueTogetherValidator(
                queryset=Company.objects.all(),
                fields=['user_id', 'name'],
                message="Company Already Exists"
            )
        ]

    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value

class CompanyQuestionsSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    company_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = CompanyQuestions
        fields = ['id', 'company', 'question', 'answer', 'company_id']
        validators = [
            UniqueTogetherValidator(
                queryset=CompanyQuestions.objects.all(),
                fields=['company_id', 'question'],
                message="Question Already Exists"
            )
        ]
    
    def validate_company_id(self, value):
        company = get_object_or_404(Company, id=value)
        if company.user != self.context['request'].user:
            raise serializers.ValidationError("Company does not belong to the user")
        return value
    

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Employee
        fields = ['id', 'user', 'name', 'linkedin_link', 'email', 'job_title', 'contacted', 'company', 'user_id', 'company_id']
        validators = [
            UniqueTogetherValidator(
                queryset=Employee.objects.all(),
                fields=['user_id', 'company_id', 'name'],
                message="Employee Already Exists"
            )
        ]
    
    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value

class ApplicationSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    submission_date = serializers.DateField(required=False)
    description = serializers.CharField(required=False, write_only=True)
    ats_score = serializers.IntegerField(required=False, write_only=True)
    stage = serializers.CharField(required=False, write_only=True)
    submitted_cv_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    contacted_employees = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    class Meta:
        model = Application
        fields = ['id', 'user', 'company', 'job_title', 'job_type', 'link', 'submission_date', 'status', 
            'user_id', 'company_id', 'submitted_cv','submitted_cv_id', 'description', 'ats_score', 'stage', 'contacted_employees']
        
    def validate_ats_score(self, value):
        if value<0 or value>100:
            raise serializers.ValidationError("ATS Score should be between 0 and 100")
        return value
    
    def validate_contacted_employees(self, employees):
        for id in employees:
            employee = get_object_or_404(Employee,id=id)
            if employee.user != self.context['request'].user:
                raise serializers.ValidationError("Employee does not belong to the user")
        return employees
    
    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value
    
    def validate_submitted_cv_id(self, value):
        cv = get_object_or_404(CV, id=value)
        if cv.user != self.context['request'].user:
            raise serializers.ValidationError("CV does not belong to the user")
        return value

    # def validate_questions(self, questions):
    #     for id in questions:
    #         question = get_object_or_404(Question,id=id)
    #         if question.user != self.context['request'].user:
    #             raise serializers.ValidationError("Question does not belong to the user")
    #     return questions

class ApplicationDetailsSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    user = UserSerializer(read_only=True)
    submitted_cv = CVSerializer(read_only=True)
    submitted_cv_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    submission_date = serializers.DateField(read_only=True)
    contacted_employees = serializers.PrimaryKeyRelatedField(many=True, queryset=Employee.objects.all())
    class Meta:
        model = Application
        fields = ['id', 'user', 'company', 'job_title', 'job_type', 'link',
                'submission_date', 'status', 'user_id', 'company_id', 'submitted_cv', 'submitted_cv_id', 'description', 'ats_score', 'stage', 'contacted_employees']
        
    def validate_ats_score(self, value):
        if value<0 or value>100:
            raise serializers.ValidationError("ATS Score should be between 0 and 100")
        return value

    def validate_contacted_employees(self, employees):
        for employee in employees:
            if employee.user != self.context['request'].user:
                raise serializers.ValidationError("Employee does not belong to the user")
        return employees
    
    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value
    
    # def validate_questions(self, questions):
    #     for id in questions:
    #         question = get_object_or_404(Question,id=id)
    #         if question.user != self.context['request'].user:
    #             raise serializers.ValidationError("Question does not belong to the user")
    #     return questions

    
class QuestionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    application = ApplicationSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    application_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Question
        fields = ['id', 'question', 'answer', 'application', 'user', 'user_id', 'application_id']
        validators = [
            UniqueTogetherValidator(queryset=Question.objects.all(),
                fields=['question', 'application_id','user_id'], message="Question Already Exists")
        ]

    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value
    
    def validate_application_id(self, value):
        application = get_object_or_404(Application, id=value)
        if application.user != self.context['request'].user:
            raise serializers.ValidationError("Application does not belong to the user")
        return value
    
class TodoListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = TodoList
        fields = ['id', 'user', 'application_title', 'application_link', 'completed', 'user_id']
        validators = [
            UniqueTogetherValidator(queryset=TodoList.objects.all(),
                fields=['application_title', 'user_id'], message="ToDo Already Exists")
        ]

    def validate_user_id(self, value):
        if value != self.context['request'].user.id:
            raise serializers.ValidationError("Not the Same user")
        return value