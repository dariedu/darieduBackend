from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from rest_framework import status

import task_app.views


class Fix2(OpenApiViewExtension):
    target_class = task_app.views.DeliveryViewSet

    def view_replacement(self):
        @extend_schema(tags=['Deliveries'])
        class Fixed(self.target_class):
            @extend_schema(
                parameters=[
                    OpenApiParameter("is_active", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                                     description="Filter by is_active", required=False),
                    OpenApiParameter("is_completed", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                                     description="Filter by is_completed", required=False),
                    OpenApiParameter("volunteer", OpenApiTypes.INT, OpenApiParameter.QUERY,
                                     description="Filter by volunteer ID", required=False),
                    OpenApiParameter("route_sheet", OpenApiTypes.INT, OpenApiParameter.QUERY,
                                     description="Filter by route_sheet ID", required=False),
                ],
                summary="List deliveries",
                operation_id="listDeliveries",
                examples=[
                    OpenApiExample(
                        "Get example",
                        description="Example of obtaining a list of deliveries",
                        value={
                            "deliveries": [
                                {
                                    "id": 1,
                                    "date": "2024-09-03T13:28:56Z",
                                    "price": 1,
                                    "is_free": 'true',
                                    "is_active": 'true',
                                    "is_completed": 'false',
                                    "in_execution": 'false',
                                    "volunteer": 'null',
                                    "route_sheet": 1
                                },
                                {
                                    "id": 2,
                                    "date": "2024-09-04T06:00:00Z",
                                    "price": 2,
                                    "is_free": 'false',
                                    "is_active": 'true',
                                    "is_completed": 'false',
                                    "in_execution": 'false',
                                    "volunteer": 1,
                                    "route_sheet": 2
                                },
                            ]
                        }
                    )
                ],
                description='You can get the entire list of deliveries, or a list by filter'
            )
            def list(self, request, *args, **kwargs):
                return super().list(request, *args, **kwargs)

            @extend_schema(
                tags=['Deliveries'],
                summary="Get volunteer deliveries",
                operation_id="getVolunteerDeliveries",
                examples=[
                    OpenApiExample(
                        "Post example",
                        description="Get a list of deliveries for a volunteer",
                        value={
                            'свободные': [
                                {"delivery_id": 1, "address": "123 Main St", "status": "free"},
                                {"delivery_id": 2, "address": "456 Elm St", "status": "free"}
                            ],
                            'мои активные доставки': [
                                {"delivery_id": 3, "address": "789 Oak St", "status": "in_execution"}
                            ],
                            'мои завершенные доставки': [
                                {"delivery_id": 4, "address": "321 Pine St", "status": "completed"}
                            ],
                        },
                        status_codes=[str(status.HTTP_200_OK)],
                    ),
                ],
                description='Пример фильтров для календаря: '
                            'api/deliveries/volunteer/?after=2024-10-05&before=2024-10-20. '
                            'Формат даты: YYYY-MM-DD можно использовать вместе или по отдельности.'
            )
            def volunteer_deliveries(self, request):
                return super().volunteer_deliveries(request)

            @extend_schema(
                tags=['Deliveries'],
                summary="Get curator deliveries",
                operation_id="getCuratorDeliveries",

                examples=[
                    OpenApiExample(
                        "Post example",
                        description="Example of obtaining a id of deliveries",
                        value={
                              "выполняются доставки": [
                                {
                                  "id_delivery": 24,
                                  "id_route_sheet": [
                                    4, 7
                                  ]
                                }
                              ],
                              "количество активных доставок": [
                                {
                                  "id_delivery": 23,
                                  "id_route_sheet": [
                                    8, 9, 10
                                  ]
                                },
                              ],
                              "количество завершенных доставок": [
                                {
                                    "id_delivery": 48,
                                    "id_route_sheet": [
                                        4
                                    ]
                                },
                               ],
                            },
                        status_codes=[str(status.HTTP_200_OK)],
                    ),
                ],
                description='Get curator deliveries'
            )
            def deliveries_curator(self, request):
                return super().deliveries_curator(request)

            @extend_schema(
                tags=['Deliveries'],
                summary="Take delivery",
                operation_id="takeDelivery",
                responses={
                    201: OpenApiResponse(
                        description="Delivery taken",
                        examples={"delivery_id": 1, "address": "123 Main St", "status": "in_execution"}
                    ),
                    400: OpenApiResponse(
                        description="Error: Delivery is already taken",
                        examples={"error": "Delivery is already taken"}
                    )
                },
                description='Take delivery'
            )
            def take_delivery(self, request, pk):
                return super().take_delivery(request, pk)

            @extend_schema(
                tags=['Deliveries_confirm/cancel'],
                summary="Cancel delivery",
                operation_id="cancelDelivery",
                responses={
                    201: OpenApiResponse(
                        description="Delivery canceled",
                        examples={"delivery_id": 1, "address": "123 Main St", "status": "free"}
                    ),
                    403: OpenApiResponse(
                        description="Error: You are not authorized to cancel this delivery",
                        examples={"error": "You are not authorized to cancel this delivery"}
                    )
                },
                description='Cancel delivery'
            )
            def cancel_delivery(self, request, pk):
                return super().cancel_delivery(request, pk)

            @extend_schema(
                tags=['Deliveries'],
                summary="Delivery activation",
                operation_id="deliveryActivation",
                methods=['post'],
                request=OpenApiTypes.NONE,
            )
            def delivery_activation(self, request, pk):
                return super().delivery_activation(request, pk)

            @extend_schema(
                tags=['Deliveries_confirm/cancel'],
                summary="Confirm delivery",
                operation_id="confirmDelivery",
                methods=['post'],
                request=OpenApiTypes.NONE,
            )
            def confirm_delivery(self, request, pk):
                return super().confirm_delivery(request, pk)

            @extend_schema(
                tags=['Deliveries_confirm/cancel'],
                summary="The list is not confirmed deliveries ",
                operation_id="listNotConfirm",
                methods=['get'],
            )
            def list_not_confirm(self, request):
                return super().list_not_confirm(request)

            @extend_schema(
                tags=['Deliveries_confirm/cancel'],
                summary="The list is confirmed deliveries ",
                operation_id="listConfirm",
                methods=['get'],
            )
            def list_confirm(self, request):
                return super().list_confirm(request)

        return Fixed

      
class Fix1(OpenApiViewExtension):
    target_class = task_app.views.TaskViewSet

    def view_replacement(self):
        @extend_schema(tags=['Tasks'])
        class Fixed(self.target_class):
            @extend_schema(
                description='Get the list of available tasks\n'
                            '+ filtering by date (for start_date) YYYY-MM-DD, category and city\n'
                            'Available task is: active, uncompleted, not timed out, has free spots',
            )
            def list(self, request, *args, **kwargs):
                return super().list(request, *args, **kwargs)

            @extend_schema(
                parameters=[
                    OpenApiParameter(
                        name='is_active',
                        description='Filter by active tasks',
                        required=False,
                        type=str  # TODO: make as in promo
                    ),
                    OpenApiParameter(
                        name='is_completed',
                        description='Filter by completed tasks',
                        required=False,
                        type=str
                    )
                ],
                tags=['Tasks']
            )
            def my(self, request, *args, **kwargs):
                return super().my(request, *args, **kwargs)

            @extend_schema(
                tags=['Task_confirm/refuse'],
            )
            def refuse(self, request, *args, **kwargs):
                return super().refuse(request, *args, **kwargs)

            @extend_schema(
                tags=['Task_confirm/refuse']
            )
            def confirm(self, request, *args, **kwargs):
                return super().confirm(request, *args, **kwargs)

            @extend_schema(
                tags=['Task_confirm/refuse']
            )
            def list_not_confirmed(self, request, *args, **kwargs):
                return super().list_not_confirmed(request, *args, **kwargs)

            @extend_schema(
                tags=['Task_confirm/refuse']
            )
            def list_confirmed_tasks(self, request, *args, **kwargs):
                return super().list_confirmed_tasks(request, *args, **kwargs)

        return Fixed
