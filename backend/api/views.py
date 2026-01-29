# backend/api/views.py
"""
API Views for the Chemical Equipment Visualizer.
Handles CSV upload, data retrieval, summary, and PDF generation.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
import json

from .models import Dataset
from .serializers import DatasetSerializer, DatasetListSerializer, UserSerializer
from .utils import parse_csv_data, calculate_summary, generate_pdf_report


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_csv(request):
    """
    Upload and process a CSV file.
    
    POST /api/upload/
    - Accepts multipart form data with 'file' field
    - Parses CSV, calculates summary statistics
    - Stores in database, maintains max 5 records
    
    Returns:
        JSON with dataset id, parsed data, and summary
    """
    
    # Check if file was provided
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided. Please upload a CSV file.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_file = request.FILES['file']
    
    # Validate file extension
    if not uploaded_file.name.endswith('.csv'):
        return Response(
            {'error': 'Invalid file type. Please upload a CSV file.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Read file content
        file_content = uploaded_file.read()
        
        # Parse CSV and get DataFrame
        data_list, df = parse_csv_data(file_content)
        
        # Calculate summary statistics
        summary = calculate_summary(df)
        
        # Create dataset record in database
        dataset = Dataset.objects.create(
            name=uploaded_file.name,
            uploaded_by=request.user if request.user.is_authenticated else None,
            raw_data=json.dumps(data_list),
            summary=json.dumps(summary),
            record_count=len(data_list)
        )
        
        # Cleanup old records (keep only last 5)
        Dataset.cleanup_old_records(keep_count=5)
        
        # Return success response
        serializer = DatasetSerializer(dataset)
        return Response({
            'message': 'File uploaded and processed successfully',
            'dataset': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error processing file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dataset(request, pk):
    """
    Retrieve a specific dataset by ID.
    
    GET /api/dataset/<id>/
    
    Returns:
        Full dataset with raw data and summary
    """
    
    try:
        dataset = Dataset.objects.get(pk=pk)
        serializer = DatasetSerializer(dataset)
        return Response(serializer.data)
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_dataset(request):
    """
    Get the most recently uploaded dataset.
    
    GET /api/dataset/latest/
    
    Returns:
        Most recent dataset or empty response
    """
    
    dataset = Dataset.objects.first()  # Ordered by -uploaded_at
    
    if dataset:
        serializer = DatasetSerializer(dataset)
        return Response(serializer.data)
    else:
        return Response(
            {'message': 'No datasets found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_history(request):
    """
    Get upload history (last 5 datasets).
    
    GET /api/history/
    
    Returns:
        List of datasets with summary info (no raw data)
    """
    
    datasets = Dataset.objects.all()[:5]
    serializer = DatasetListSerializer(datasets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary(request, pk):
    """
    Get only the summary statistics for a dataset.
    
    GET /api/summary/<id>/
    
    Returns:
        Summary statistics dictionary
    """
    
    try:
        dataset = Dataset.objects.get(pk=pk)
        return Response({
            'id': dataset.id,
            'name': dataset.name,
            'summary': dataset.get_summary()
        })
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def download_pdf(request, pk):
    """
    Generate and download PDF report for a dataset.
    
    GET /api/pdf/<id>/
    
    Returns:
        PDF file as attachment
    """
    
    try:
        dataset = Dataset.objects.get(pk=pk)
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(dataset)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{dataset.name}.pdf"'
        
        return response
        
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_dataset(request, pk):
    """
    Delete a specific dataset.
    
    DELETE /api/dataset/<id>/delete/
    """
    
    try:
        dataset = Dataset.objects.get(pk=pk)
        dataset.delete()
        return Response(
            {'message': 'Dataset deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# ============== Authentication Views ==============

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user.
    
    POST /api/auth/register/
    Body: { "username": "...", "password": "...", "email": "..." }
    """
    
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login and get authentication token.
    
    POST /api/auth/login/
    Body: { "username": "...", "password": "..." }
    """
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token.key
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout and delete token.
    
    POST /api/auth/logout/
    """
    
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except:
        return Response({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user profile.
    
    GET /api/auth/profile/
    """
    
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email
    })