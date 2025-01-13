from datetime import datetime, timedelta, timezone

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

from address_app.models import City, Location
from dariedu import settings
from user_app.models import User
from ..models import Task, Delivery, TaskCategory


@pytest.fixture(autouse=True)
def disable_celery():
    settings.CELERY_BROKER_URL = 'memory://'
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    yield
    settings.CELERY_BROKER_URL = 'redis://redis:6379'
    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.CELERY_TASK_EAGER_PROPAGATES = False


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(tg_id='1', password='password')


@pytest.fixture
def client(admin_user):
    client = Client()
    client.login(tg_id='1', password='password')
    return client


@pytest.fixture
def city(db):
    return City.objects.create(city='Москва')


@pytest.fixture
def category(db):
    return TaskCategory.objects.create(name='Категория')


@pytest.fixture
def location(db, city):
    return Location.objects.create(address='ул. Ленина, 1', city=city)


@pytest.fixture
def task(db, city, admin_user, category):
    return Task.objects.create(
        name='Задача',
        city=city,
        category=category,
        description='Описание задачи',
        volunteers_needed=2,
        volunteers_taken=1,
        volunteer_price=2,
        curator_price=3,
        start_date=datetime(2021, 1, 1, 12, 0, tzinfo=timezone.utc),
        end_date=datetime(2021, 1, 1, 15, 0, tzinfo=timezone.utc),
        curator=admin_user,
    )


def test_task_copy(client, task):
    url = reverse('admin:task_app_task_changelist')
    response = client.post(url, {
        'action': 'copy',
        '_selected_action': [task.id],
    })
    new_task = Task.objects.get(pk=task.pk + 1)
    assert response.status_code == 302
    assert Task.objects.count() == 2
    assert new_task.name == task.name
    assert new_task.description == task.description
    assert new_task.category == task.category
    assert new_task.volunteers_needed == task.volunteers_needed
    assert new_task.volunteers_taken == 0
    assert new_task.volunteer_price == task.volunteer_price
    assert new_task.curator_price == task.curator_price
    assert new_task.start_date == datetime(2021, 1, 8, 12, 0, tzinfo=timezone.utc)
    assert new_task.end_date == datetime(2021, 1, 8, 15, 0, tzinfo=timezone.utc)
    assert new_task.curator == task.curator
    assert new_task.is_active is False
    assert new_task.is_completed is False


@pytest.fixture
def delivery(db, admin_user, location):
    return Delivery.objects.create(
        date=datetime(2021, 1, 1, 15, 0, tzinfo=timezone.utc),
        curator=admin_user,
        location=location,
        volunteers_needed=3,
        volunteers_taken=1
    )


def test_delivery_copy(client, delivery, location):
    url = reverse('admin:task_app_delivery_changelist')
    response = client.post(url, {
        'action': 'copy',
        '_selected_action': [delivery.id],
    })
    new_delivery = Delivery.objects.get(pk=delivery.pk + 1)
    assert response.status_code == 302
    assert Delivery.objects.count() == 2
    assert new_delivery.date == datetime(2021, 1, 8, 15, 0, tzinfo=timezone.utc)
    assert new_delivery.curator == delivery.curator
    assert new_delivery.location == location
    assert new_delivery.volunteers_needed == delivery.volunteers_needed
    assert new_delivery.volunteers_taken == 0
    assert new_delivery.is_active is False
    assert new_delivery.is_completed is False
    assert new_delivery.in_execution is False
    assert new_delivery.is_free is True
