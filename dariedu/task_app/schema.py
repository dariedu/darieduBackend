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
                description='Get volunteer deliveries'
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
                            'выполняются доставки (id)': [1, 6, 25],
                            'количество активных доставок (id)': [5, 32, 56, 78],
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
                tags=['Deliveries'],
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

        return Fixed

      
class Fix1(OpenApiViewExtension):
    target_class = task_app.views.TaskViewSet

    def view_replacement(self):
        @extend_schema(tags=['Tasks'])
        class Fixed(self.target_class):
            @extend_schema(
                description='Get the list of available tasks\n\n'
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
                        type=int
                    ),
                    OpenApiParameter(
                        name='is_completed',
                        description='Filter by completed tasks',
                        required=False,
                        type=int
                    )
                ],
                tags=['Tasks']
            )
            def my(self, request, *args, **kwargs):
                return super().my(request, *args, **kwargs)

        return Fixed
