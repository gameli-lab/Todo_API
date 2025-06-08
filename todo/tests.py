from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, Task
from unittest.mock import patch
from django.utils import timezone
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken


class UserTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'fullname': 'Benjamin Torfu',
            'phone': '0541813988',
            'email': 'btorfu@gmail.com',
            'password': 'Sp33d1',
            'confirm_password': 'Sp33d1',
        }
        self.user = User.objects.create_user(
            fullname=self.user_data['fullname'],
            phone=self.user_data['phone'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
    def test_user_registration(self):
        new_user_data = {
        'fullname': 'New User',
        'phone': '0541813999',
        'email': 'newuser@example.com',
        'password': 'Sp33d1',
        'confirm_password': 'Sp33d1',
    }
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
    def test_user_registration_existing_email(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])
    def test_user_registration_existing_phone(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data['errors'])
    def test_user_login(self):
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    def test_user_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'No active account found with the given credentials')
    def test_user_login_nonexistent_email(self):
        response = self.client.post(self.login_url, {
            'email': 'btorfu@yahoo.com',
            'password': self.user_data['password']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'No active account found with the given credentials')
    def test_user_login_empty_email(self):
        response = self.client.post(self.login_url, {
            'email': '',
            'password': self.user_data['password']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])
        self.assertEqual(response.data['errors']['email'], ['This field may not be blank.'])
    def test_user_login_empty_password(self):
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': ''
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['errors'])
        self.assertEqual(response.data['errors']['password'], ['This field may not be blank.'])
class TaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            fullname='Benjamin Torfu',
            phone='0541813989',
            email='btorfu@gmail.com',
            password='Sp33d1'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.task_data = {
            'title': 'Test Task',
            'description': 'This is a test task.',
            'due_date': '2023-12-31',
            'status': 'pending' 
        }
        self.task_url = reverse('task-list')
        self.task = Task.objects.create(
            title=self.task_data['title'],
            description=self.task_data['description'],
            due_date=timezone.make_aware(datetime.strptime(self.task_data['due_date'], '%Y-%m-%d')),
            status=self.task_data['status'],
            user=self.user
        )
    def test_create_task(self):
        response = self.client.post(self.task_url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title=self.task_data['title']).exists())
    def test_create_task_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(self.task_url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_list_tasks(self):
        response = self.client.get(self.task_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task.title)
    def test_list_tasks_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.task_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_update_task(self):
        update_data = {
            'title': 'Updated Task',
            'description': 'This is an updated test task.',
            'due_date': '2024-01-01',
            'status': 'completed'
        }
        response = self.client.put(reverse('task-detail', args=[self.task.id]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, update_data['title'])
        self.assertEqual(self.task.description, update_data['description'])
        self.assertEqual(self.task.due_date.strftime('%Y-%m-%d'), update_data['due_date'])
        self.assertEqual(self.task.status, update_data['status'])
    def test_update_task_unauthenticated(self):
        self.client.credentials()
        update_data = {
            'title': 'Updated Task',
            'description': 'This is an updated test task.',
            'due_date': '2024-01-01',
            'status': 'completed'
        }
        response = self.client.put(reverse('task-detail', args=[self.task.id]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_delete_task(self):
        response = self.client.delete(reverse('task-detail', args=[self.task.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
    def test_delete_task_unauthenticated(self):
        self.client.credentials()
        response = self.client.delete(reverse('task-detail', args=[self.task.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())
    def test_update_task_not_found(self):
        update_data = {
            'title': 'Updated Task',
            'description': 'This is an updated test task.',
            'due_date': '2024-01-01',
            'status': 'completed'
        }
        response = self.client.put(reverse('task-detail', args=[999]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Not found.')
    def test_delete_task_not_found(self):
        response = self.client.delete(reverse('task-detail', args=[999]), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_create_task_invalid_due_date(self):
        invalid_task_data = {
            'title': 'Invalid Task',
            'description': 'This task has an invalid due date.',
            'due_date': '2020-01-01',  # Past date
            'status': 'pending'
        }
        response = self.client.post(self.task_url, invalid_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('due_date', response.data['errors'])
        self.assertEqual(response.data['errors']['due_date'], ['Due date cannot be in the past.'])
    def test_create_task_empty_title(self):
        invalid_task_data = {
            'title': '',  # Empty title
            'description': 'This task has an empty title.',
            'due_date': '2024-01-01',
            'status': 'pending'
        }
        response = self.client.post(self.task_url, invalid_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data['errors'])
        self.assertEqual(response.data['errors']['title'], ['This field may not be blank.'])
    def test_update_task_status(self):
        update_status_data = {
            'status': 'completed'
        }
        response = self.client.patch(reverse('task-status', args=[self.task.id]), update_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, update_status_data['status'])
    def test_update_task_status_invalid(self):
        update_status_data = {
            'status': 'invalid_status'  # Invalid status
        }
        response = self.client.patch(reverse('task-status', args=[self.task.id]), update_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data['errors'])
        self.assertEqual(response.data['errors']['status'], ['"invalid_status" is not a valid choice.'])
        self.assertEqual(self.task.status, self.task_data['status'])
    def test_update_task_status_not_found(self):
        update_status_data = {
            'status': 'completed'
        }
        response = self.client.patch(reverse('task-status', args=[999]), update_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Not found.')
    def test_update_task_status_unauthenticated(self):
        self.client.credentials()
        update_status_data = {
            'status': 'completed'
        }
        response = self.client.patch(reverse('task-status', args=[self.task.id]), update_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.task.status, self.task_data['status'])
        
    def test_update_task_status_unauthorized(self):
        another_user = User.objects.create_user(
            fullname='Another User',
            phone='0541813999',
            email='QXx9o@example.com',
            password='Sp33d2'
        )
        self.client.force_authenticate(user=another_user)
        update_status_data = {
            'status': 'completed'
        }
        response = self.client.patch(reverse('task-status', args=[self.task.id]), update_status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.task.status, self.task_data['status'])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.task_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task.title)
        self.assertEqual(response.data[0]['status'], self.task.status)
        self.assertEqual(response.data[0]['user'], self.user.id)
        self.client.force_authenticate(user=None)
        response = self.client.get(self.task_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('task-detail', args=[self.task.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task.title)
        self.assertEqual(response.data['description'], self.task.description)
        self.assertEqual(response.data['due_date'], self.task.due_date.strftime('%Y-%m-%d'))
        self.assertEqual(response.data['status'], self.task.status)
        self.assertEqual(response.data['user'], self.user.id)

    def test_list_tasks(self):
        response = self.client.get(self.task_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Tasks retrieved successfully.")
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], self.task.title)

    def test_filter_tasks_by_status(self):
      response = self.client.get(f"{self.task_url}?status=pending", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 1)
      
      response = self.client.get(f"{self.task_url}?status=completed", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 0)
    
    def test_filter_tasks_by_due_date(self):
        #response = self.client.get(f"{self.task_url}?due_date={self.task.due_date.strftime('%Y-%m-%d')}", format='json')
        if isinstance(self.task.due_date, str):
            due_date = self.task.due_date
        else:
            due_date = self.task.due_date.strftime('%Y-%m-%d')
        response = self.client.get(f"{self.task_url}?due_date={due_date}", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], self.task.title)
        
        response = self.client.get(f"{self.task_url}?due_date=2024-01-01", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)

    def test_filter_tasks_by_title(self):
        response = self.client.get(f"{self.task_url}?title={self.task.title}", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], self.task.title)
        
        response = self.client.get(f"{self.task_url}?title=Nonexistent", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)
    
    def test_filter_tasks_by_description(self):
        response = self.client.get(f"{self.task_url}?description={self.task.description}", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['description'], self.task.description)
        
        response = self.client.get(f"{self.task_url}?description=Nonexistent", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)
    
    def test_search_tasks(self):
      response = self.client.get(f"{self.task_url}?search=Test", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 1)
      
      response = self.client.get(f"{self.task_url}?search=NonExistent", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 0)

    def test_pagination(self):
      """Test API pagination behavior."""
      # Create 10 additional tasks to trigger pagination
      for i in range(10):
          Task.objects.create(
              title=f"Pagination Task {i}",
              description=f"Testing pagination {i}",
              due_date="2024-12-31",
              status="pending",
              user=self.user
          )
      
      # Test default pagination (should return first page)
      response = self.client.get(self.task_url, format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertTrue(response.data['success'])
      
      # Check pagination data is included
      self.assertIn('count', response.data)
      self.assertIn('next', response.data)
      self.assertIn('previous', response.data)
      self.assertEqual(response.data['count'], 11)  # Original task + 10 new ones
      self.assertIsNotNone(response.data['next'])  # Should have next page
      self.assertIsNone(response.data['previous'])  # No previous page for first page
      
      # Test explicit page parameter
      response = self.client.get(f"{self.task_url}?page=2", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertIsNone(response.data['next'])  # No next page
      self.assertIsNotNone(response.data['previous'])  # Should have previous page
      
      # Test page size parameter
      response = self.client.get(f"{self.task_url}?page_size=5", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 5)
      
      # Test invalid page number
      response = self.client.get(f"{self.task_url}?page=999", format='json')
      self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_tasks_with_multiple_criteria(self):
      """Test filtering tasks with multiple criteria."""
      # Create additional tasks with different attributes
      Task.objects.create(
          title="Important Meeting",
          description="Board meeting",
          due_date="2024-06-15",
          status="in_progress",
          user=self.user
      )
      Task.objects.create(
          title="Project Deadline",
          description="Submit final project",
          due_date="2024-07-30",
          status="pending",
          user=self.user
      )
      
      # Filter by status AND title
      response = self.client.get(f"{self.task_url}?status=pending&title=Project", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 1)
      self.assertEqual(response.data['data'][0]['title'], "Project Deadline")
      
      # Filter by title AND description
      response = self.client.get(f"{self.task_url}?title=Meeting&description=Board", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 1)
      self.assertEqual(response.data['data'][0]['title'], "Important Meeting")
      
      # Filter that should return no results
      response = self.client.get(f"{self.task_url}?status=completed&title=Meeting", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 0)
      
      # Filter with unrelated criteria to ensure AND behavior
      response = self.client.get(f"{self.task_url}?title=Meeting&title=Project", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 0)  # Both criteria can't be matched simultaneously
  
    def test_date_range_filtering(self):
      """Test filtering tasks by date ranges."""
      # Create tasks with different dates
      Task.objects.create(
          title="Early Task",
          description="Due early in the year",
          due_date="2024-02-15",
          status="pending",
          user=self.user
      )
      Task.objects.create(
          title="Mid-Year Task",
          description="Due in the middle of the year",
          due_date="2024-06-30",
          status="pending",
          user=self.user
      )
      Task.objects.create(
          title="End-Year Task",
          description="Due at end of year",
          due_date="2024-12-15",
          status="pending",
          user=self.user
      )
      
      # Test due_date_after filter
      response = self.client.get(f"{self.task_url}?due_date_after=2024-06-01", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 2)  # Mid-Year and End-Year tasks
      
      # Test due_date_before filter
      response = self.client.get(f"{self.task_url}?due_date_before=2024-07-01", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 2)  # Early and Mid-Year tasks
      
      # Test date range (both before and after)
      response = self.client.get(f"{self.task_url}?due_date_after=2024-03-01&due_date_before=2024-11-01", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 1)  # Only Mid-Year task
      self.assertEqual(response.data['data'][0]['title'], "Mid-Year Task")
      
      # Test no results within range
      response = self.client.get(f"{self.task_url}?due_date_after=2025-01-01", format='json')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(len(response.data['data']), 0)

    def test_overdue_tasks_filter(self):
      """Test filtering for overdue tasks."""
      # This test requires mocking timezone.now() to simulate overdue tasks
      
      # Create tasks with different dates
      Task.objects.create(
          title="Past Task",
          description="Task with past due date",
          due_date="2023-01-15",  # Intentionally in the past
          status="pending",
          user=self.user
      )
      
      with patch('django.utils.timezone.now') as mock_now:
          # Mock current date to be 2023-02-01
          mock_now.return_value = datetime(2023, 2, 1, tzinfo=timezone.get_default_timezone())
          
          # Test is_overdue filter
          response = self.client.get(f"{self.task_url}?is_overdue=true", format='json')
          self.assertEqual(response.status_code, status.HTTP_200_OK)
          self.assertEqual(len(response.data['data']), 1)
          self.assertEqual(response.data['data'][0]['title'], "Past Task")
          
          # Test combination with status
          response = self.client.get(f"{self.task_url}?is_overdue=true&status=completed", format='json')
          self.assertEqual(response.status_code, status.HTTP_200_OK)
          self.assertEqual(len(response.data['data']), 0)  # No completed overdue tasks