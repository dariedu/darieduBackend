import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

from dariedu import settings
from ..models import City, Address, Location, RouteSheet


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
def location(db, city):
    return Location.objects.create(address='ул. Ленина, 1', city=city)


@pytest.fixture
def route_sheet(db):
    return RouteSheet.objects.create(name='Ленинская')


@pytest.fixture
def address(db):
    return Address.objects.create(address='ул. Ленина, 2')


def test_addresses_to_route_sheet(client, address, route_sheet):
    url = reverse('admin:address_app_address_changelist')
    response = client.post(url, {
        'action': 'add_addresses_to_route_sheet',
        '_selected_action': [address.id],
        'route_sheet': route_sheet.id,
        'apply': 'Применить'
    })
    assert response.status_code == 302
    address.refresh_from_db()
    assert address.route_sheet == route_sheet


def test_addresses_to_location(client, address, location):
    url = reverse('admin:address_app_address_changelist')
    response = client.post(url, {
        'action': 'add_addresses_to_location',
        '_selected_action': [address.id],
        'location': location.id,
        'apply': 'Применить'
    })
    assert response.status_code == 302
    address.refresh_from_db()
    assert address.location == location
