import logging
import os

from celery import shared_task
from django.core.cache import cache
from user_app.models import User

from dariedu.gspread_config import gs

from .models import Delivery
from address_app.models import RouteAssignment, Beneficiar, Address

logger = logging.getLogger('google.sheets')

gc = gs
spreadsheet_url = os.getenv('SPREADSHEET_URL')
spreadsheet = gc.open_by_url(spreadsheet_url)
worksheet_name = os.getenv('WS_DELIVERY')
worksheet = spreadsheet.worksheet(worksheet_name)


@shared_task(bind=True, max_retries=3)
def export_deliveries(self, delivery_id):
    try:
        delivery = Delivery.objects.select_related('curator', 'location').prefetch_related(
            'assignments__volunteer'
        ).get(id=delivery_id)
    except Delivery.DoesNotExist:
        logger.error(f"Delivery {delivery_id} not found")
        return

    cache_key = f"delivery_exported_{delivery_id}"
    if cache.get(cache_key):
        logger.info(f"Delivery {delivery_id} already exported")
        return

    volunteers = set()
    for assignment in delivery.assignments.all():
        volunteers.update(assignment.volunteer.all())

    if not volunteers:
        logger.info(f"No volunteers for delivery {delivery_id}")
        return

    rows = []
    for volunteer in volunteers:

        route_assignment = RouteAssignment.objects.filter(delivery=delivery, volunteer=volunteer).first()

        if route_assignment:
            route_sheet = route_assignment.route_sheet
            addresses = Address.objects.filter(route_sheet=route_sheet)
            beneficiaries = Beneficiar.objects.filter(address__in=addresses)
            beneficiary_names = ', '.join(
                [f"{beneficiary.full_name.split()[0]} {beneficiary.full_name.split()[1][0]}. "
                 f"{beneficiary.full_name.split()[2][0]}." for beneficiary in
                 beneficiaries])

            row = [
                delivery.date.strftime('%d.%m.%Y'),
                delivery.location.address,
                f'{delivery.curator.last_name} {delivery.curator.name}'.strip(),
                f"{volunteer.last_name} {volunteer.name}".strip(),
                getattr(volunteer, 'tg_username', ''),
                getattr(volunteer, 'phone', ''),
                volunteer.email,
                '✅' if route_assignment is not None else '❌',
                beneficiary_names
            ]
            rows.append(row)

    try:
        # headers = worksheet.row_values(1)
        # expected_headers = ['Дата доставки', 'Локация', 'Куратор', 'Фамилия Имя', 'TG username', 'Телефон', 'Email',
        #                     'Комментарии']
        # if headers != expected_headers:
        #     worksheet.insert_row(expected_headers, 1)

        if rows:
            worksheet.append_rows(rows)

        cache.set(cache_key, True, timeout=60)
        logger.info(f"Exported delivery {delivery_id}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        self.retry(exc=e, countdown=30)
