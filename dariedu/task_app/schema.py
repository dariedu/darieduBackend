from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, OpenApiParameter

import task_app.views


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
