from datetime import datetime, timedelta, timezone

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

from address_app.models import City, Location
from dariedu import settings
from user_app.models import User
from ..models import Promotion, PromoCategory


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
    return PromoCategory.objects.create(name='Категория')

@pytest.fixture
def promo(db, city, admin_user, category):
    return Promotion.objects.create(
        category=category,
        name='Поощрение',
        price=4,
        description='Описание',
        start_date=datetime(2021, 1, 8, 12, 0, tzinfo=timezone.utc),
        end_date=datetime(2021, 1, 8, 15, 0, tzinfo=timezone.utc),
        city=city,
        quantity=3,
        available_quantity=1,
        for_curators_only=False,
        is_permanent=False,
        is_active=True,
        address='ул. Ленина, 2',
        contact_person=admin_user
    )


def test_promo_copy(client, promo, category, city):
    url = reverse('admin:promo_app_promotion_changelist')
    response = client.post(url, {
        'action': 'copy',
        '_selected_action': [promo.id],
    })
    new_promo = Promotion.objects.get(pk=promo.pk + 1)
    assert response.status_code == 302
    assert Promotion.objects.count() == 2
    assert new_promo.name == promo.name + '_copy'
    assert new_promo.is_active is False
    assert new_promo.start_date == datetime(2021, 1, 15, 12, 0, tzinfo=timezone.utc)
    assert new_promo.end_date == datetime(2021, 1, 15, 15, 0, tzinfo=timezone.utc)
    assert new_promo.is_permanent is False
    assert new_promo.available_quantity == 3
    assert new_promo.quantity == 3
    assert new_promo.for_curators_only is False
    assert new_promo.description == promo.description
    assert new_promo.city == city
    assert new_promo.address == promo.address
    assert new_promo.contact_person == promo.contact_person
    assert new_promo.category == category
