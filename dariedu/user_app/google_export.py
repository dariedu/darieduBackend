import os
from django.contrib.admin.actions import action

from dariedu.gspread_config import gs


@action(description='Экспорт в Google')
def export_to_gs(modeladmin, request, queryset):
    users = queryset.all()
    gc = gs
    spreadsheet_url = os.getenv('SPREADSHEET_URL')
    spreadsheet = gc.open_by_url(spreadsheet_url)
    worksheet_name = os.getenv('WORKSHEET_NAME')
    worksheet = spreadsheet.worksheet(worksheet_name)
    first_row_values = worksheet.row_values(1)

    if all(value == '' for value in first_row_values):
        data = [
            ['tg_id', 'email', 'last_name', 'name', 'surname', 'phone', 'volunteer_hour', 'point', 'is_superuser',
             'is_staff', 'rating', 'city'],
            *[[user.tg_id, user.email, user.last_name, user.name, user.surname, user.phone,
               user.volunteer_hour, user.point, user.is_superuser, user.is_staff, user.rating, user.city] for user in
              users]
        ]
        worksheet.update(data)
    else:
        empty_row_index = len(worksheet.get_all_records()) + 1
        data = [
            [user.tg_id, user.email, user.last_name, user.name, user.surname, user.phone,
             user.volunteer_hour, user.point, user.is_superuser, user.is_staff, user.rating, user.city]
            for user in users
        ]
        worksheet.append_rows(data, table_range=f'A{empty_row_index}')

