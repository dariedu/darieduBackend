from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .serializers import FeedbackSerializer


class FeedbackSchemaExtension(OpenApiViewExtension):

    @extend_schema(
        parameters=[
            OpenApiParameter(name="user", description="Filter by user", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="date", description="Filter by date", required=False, type=OpenApiTypes.DATE),
        ],
        summary="List feedbacks",
        operation_id="listFeedbacks",
        responses={200: OpenApiResponse(description="List of feedbacks", examples={
            'application/json': {
                "feedbacks": [
                    {"id": 1, "type": "delivery", "text": "Great service!", "user": "user1", "created_at": "2024-09-20"},
                    {"id": 2, "type": "promotion", "text": "Good product!", "user": "user2", "created_at": "2024-10-01"}
                ]
            }
        })}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Submit feedback",
        operation_id="submitFeedback",
        request=FeedbackSerializer,
        responses={
            201: OpenApiResponse(description="Feedback submitted successfully", examples={
                'application/json': {"message": "Спасибо за ваш отзыв!"}
            }),
            400: OpenApiResponse(description="Invalid data", examples={
                'application/json': {"error": {"text": ["This field may not be blank."]}}
            })
        }
    )
    def submit_feedback(self, request):
        return super().submit_feedback(request)

    @extend_schema(
        summary="Cancel submitted feedback",
        operation_id="cancelFeedback",
        responses={
            200: OpenApiResponse(description="Feedback canceled successfully", examples={
                'application/json': {"message": "Отзыв успешно удален."}
            }),
            403: OpenApiResponse(description="Error: Feedback not found or you do not have permission")
        }
    )
    def cancel_feedback(self, request, pk):
        return super().cancel_feedback(request, pk)

    @extend_schema(
        summary="Get feedback stats",
        operation_id="feedbackStats",
        responses={
            200: OpenApiResponse(description="Feedback statistics", examples={
                'application/json': {"total_feedback": 5}
            })
        }
    )
    def feedback_stats(self, request):
        return super().feedback_stats(request)
