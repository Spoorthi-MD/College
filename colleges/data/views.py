import pandas as pd
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import *
from django.db import IntegrityError
from rest_framework.decorators import api_view
import logging

# Create your views here.

logger = logging.getLogger(__name__)


class CollegesViewSet(viewsets.ModelViewSet):
    queryset = Colleges.objects.all()
    serializer_class = CollegeSerializer

    def create(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        file = request.FILES.get('file')

        # Check if a file was uploaded
        if not file:
            logger.error("No file was uploaded")
            return Response({"error": "No file was uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read the data from the uploaded Excel file using pandas
            df = pd.read_excel(file, sheet_name="Colleges")

            colleges_list = []

            # Iterate through each row in the Excel data
            for index, row in df.iterrows():
                college_code = row['college_code']
                college_name = row['name']
                college = Colleges(college_code=college_code, college_name=college_name)
                colleges_list.append(college)

            # Bulk create all the Colleges objects in the list to the database
            Colleges.objects.bulk_create(colleges_list)

            logger.info("Data added successfully.")

            return Response({"message": "Data added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error while processing request: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BranchesViewSet(viewsets.ModelViewSet):
    queryset = Branches.objects.all()
    serializer_class = BranchSerializer

    def create(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        file = request.FILES.get('file')
        if not file:
            logger.error("No file was uploaded")
            return Response({"error": "No file was uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            # Check if a file was uploaded
            df = pd.read_excel(file, sheet_name="Streams")

            branch_list = []

            # Iterate through each row in the Excel dat
            for index, row in df.iterrows():
                branch_code = row['branch_code']
                branch_name = row['name']
                branch = Branches(branch_code=branch_code, branch_name=branch_name)
                branch_list.append(branch)
                print('name', branch_name)
                print('code', branch_code)
                print('list', branch_list)

            # Bulk create all the Branches objects in the list to the database
            Branches.objects.bulk_create(branch_list)

            logger.info("Data added successfully.")

            return Response({"message": "Data added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error while processing request: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StreamViewSet(viewsets.ModelViewSet):
    queryset = Streams.objects.all()
    serializer_class = StreamSerializer

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')  # Use 'assessment(1).xlsx' as the key
        if not file:
            logger.error("No file was uploaded")
            return Response({"error": "No file was uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, sheet_name="college streaams")

            stream_list = []

            for index, row in df.iterrows():
                # Extract the college_name and branch_name from the row
                college_name = row['college']
                branch_name = row['branch']

                # Get the corresponding college_id and branch_id from the database
                college_id = Colleges.objects.filter(college_name=college_name).values_list('id', flat=True).first()
                branch_id = Branches.objects.filter(branch_name=branch_name).values_list('id', flat=True).first()

                if college_id is not None and branch_id is not None:
                    # Create a new Streams object with the extracted college_id and branch_id
                    stream = Streams(college_id=college_id, branch_id=branch_id)
                    stream_list.append(stream)

            # Bulk create all the Streams objects in the list to the database
            Streams.objects.bulk_create(stream_list)

            logger.info("Data added successfully.")

            return Response({"message": "Data added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error while processing request: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Students.objects.all()
    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        file = request.FILES.get('file')

        # Check if a file was uploaded
        if not file:
            logger.error("No file was uploaded")
            return Response({"error": "No file was uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read the data from the uploaded Excel file using pandas
            df = pd.read_excel(file, sheet_name="Students")

            student_list = []

            # Iterate through each row in the Excel data
            for index, row in df.iterrows():
                # Extract the reg_num, first_name, last_name, branch_name, and college_name from the row
                reg_num = row['reg_no']
                first_name = row['first_name']
                last_name = row['last_name']
                b_name = row['branch']
                c_name = row['college']

                # Fetch the corresponding colleges using college_name
                colleges = Colleges.objects.filter(college_name=c_name)

                for college in colleges:
                    # Fetch the corresponding branch using branch_name
                    branch = Branches.objects.get(branch_name=b_name)

                    # Create the student object and assign the college and branch objects
                    student = Students(reg_num=reg_num, first_name=first_name, last_name=last_name,
                                       c_name=college, b_name=branch)
                    student_list.append(student)
                    print(student_list)

            # Bulk create all the Students objects in the list to the database
            Students.objects.bulk_create(student_list)

            logger.info("Data added successfully.")

            return Response({"message": "Data added successfully."}, status=status.HTTP_201_CREATED)

        except Branches.DoesNotExist as e:
            return Response({"error": f"Error: Branch '{b_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error while processing request: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def college_branch_student_data(request):
    data = []

    logger.info("Fetching college data")

    # Iterate through each college
    for college in Colleges.objects.prefetch_related('streams__branch__students'):
        college_data = {
            'college_id': college.id,
            'college_name': college.college_name,
            'branches': []
        }

        student_ids_set = set()

        for stream in college.streams.all():
            branch = stream.branch

            branch_data = {
                'branch_name': branch.branch_name,
                'students': []
            }

            for student in stream.branch.students.all():
                # Check if the student ID is already in the set for this college
                if student.id not in student_ids_set:
                    student_data = {
                        'reg_num': student.reg_num,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                    }
                    branch_data['students'].append(student_data)
                    # Add the student ID to the set for this college
                    student_ids_set.add(student.id)

            if branch_data['students']:
                college_data['branches'].append(branch_data)

        if college_data['branches']:
            data.append(college_data)
            logger.info("College data fetched successfully")

    return Response(data)
