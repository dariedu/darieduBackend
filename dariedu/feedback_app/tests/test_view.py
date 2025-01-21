from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from address_app.models import City, Location
from promo_app.models import Promotion
from task_app.models import Delivery, Task
from ..models import Feedback, RequestMessage, PhotoReport
from user_app.models import User
from dariedu import settings


User = get_user_model()


@pytest.fixture(autouse=True)
def disable_celery(settings):
    settings.CELERY_BROKER_URL = 'memory://'
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    yield
    settings.CELERY_BROKER_URL = 'redis://redis:6379'
    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.CELERY_TASK_EAGER_PROPAGATES = False


@pytest.mark.django_db
class TestFeedbackViewSet:
    @pytest.fixture
    def test_user(self):
        return User.objects.create_user(tg_id='1', name='Иван')

    @pytest.fixture
    def client(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        return client

    @pytest.fixture
    def city(self):
        return City.objects.create(city='Москва')

    @pytest.fixture
    def location(self, city):
        return Location.objects.create(
            address='ул. Ленина, 1',
            city=city,
        )

    @pytest.fixture
    def delivery(self, location):
        return Delivery.objects.create(
            date=datetime.now(),
            location=location,
        )

    @pytest.fixture
    def task(self, city, test_user):
        return Task.objects.create(
            name='Задача',
            city=city,
            start_date=datetime.now(),
            end_date=datetime.now(),
            curator=test_user,
        )

    @pytest.fixture
    def promotion(self, city):
        return Promotion.objects.create(
            name='Поощрение',
            price=4,
            is_permanent=True,
            city=city
        )

    def test_submit_delivery_feedback(self, client, delivery):
        # TODO: does not work correctly
        url = reverse('feedback-submit-feedback')
        response = client.post(url, {
            'delivery': delivery.id,
            'task': '',
            'promotion': '',
            'text': 'Ok',
            'type': 'completed_delivery'
        })
        assert response.status_code == status.HTTP_201_СREATED
        assert Feedback.objects.count() == 1
        feedback = Feedback.objects.first()
        assert feedback.user == client.user
        assert feedback.delivery == delivery.id
        assert feedback.text == 'Ok'
        assert feedback.type == 'completed_delivery'

    def test_submit_task_feedback(self, client, task):
        # TODO: does not work correctly
        url = reverse('feedback-submit-feedback')
        response = client.post(url, {
            'task': task.id,
            'text': 'Ok',
            'promotion': '',
            'delivery': '',
            'type': 'completed_task',

        })
        assert response.status_code == status.HTTP_201_СREATED
        assert Feedback.objects.count() == 1
        feedback = Feedback.objects.first()
        assert feedback.user == client.user
        assert feedback.task == task.id
        assert feedback.text == 'Ok'
        assert feedback.type == 'completed_task'

    def test_submit_promotion_feedback(self, client, promotion):
        # TODO: does not work correctly
        url = reverse('feedback-submit-feedback')
        response = client.post(url, {
            'promotion': promotion.id,
            'text': 'Ok',
            'delivery': '',
            'task': '',
            'type': 'completed_promotion',
        })
        assert response.status_code == status.HTTP_201_СREATED
        assert Feedback.objects.count() == 1
        feedback = Feedback.objects.first()
        assert feedback.user == client.user
        assert feedback.promotion == promotion.id
        assert feedback.text == 'Ok'
        assert feedback.type == 'completed_promotion'

