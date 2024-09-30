from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


class PromotionSchemaExtension(OpenApiViewExtension):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="category", description="Filter by category", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="city", description="Filter by city", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="start_date", description="Filter by start date", required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name="is_active", description="Filter by active status", required=False, type=OpenApiTypes.BOOL)
        ],
        summary="List promotions",
        operation_id="listPromotions",
        responses={
            200: OpenApiResponse(description="List of promotions", examples={
                'application/json': {
                    "promotions": [
                        {"id": 1, "name": "Promo1", "price": 100, "is_active": True, "start_date": "2024-09-20"},
                        {"id": 2, "name": "Promo2", "price": 150, "is_active": True, "start_date": "2024-10-01"}
                    ]
                }
            })
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Redeem a promotion",
        operation_id="redeemPromotion",
        responses={
            201: OpenApiResponse(description="Promotion redeemed successfully", examples={
                'application/json': {"message": "Promotion redeemed successfully"}
            }),
            400: OpenApiResponse(description="Error: Insufficient points or promotion unavailable")
        }
    )
    def redeem_promotion(self, request, pk):
        return super().redeem_promotion(request, pk)

    @extend_schema(
        summary="Cancel redeemed promotion",
        operation_id="cancelRedeem",
        responses={
            200: OpenApiResponse(description="Promotion canceled successfully", examples={
                'application/json': {"message": "Promotion canceled, points returned"}
            }),
            400: OpenApiResponse(description="Error: No promotion found")
        }
    )
    def cancel_redeem(self, request, pk):
        return super().cancel_redeem(request, pk)





class FeedbackSchemaExtension(OpenApiViewExtension):

    @extend_schema(
        parameters=[
            OpenApiParameter(name="user", description="Filter by user", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name="date", description="Filter by date", required=False, type=OpenApiTypes.DATE),
        ],
        summary="List feedbacks",
        operation_id="listFeedbacks",
        responses={
            200: OpenApiResponse(description="List of feedbacks", examples={
                'application/json': {
                    "feedbacks": [
                        {"id": 1, "message": "Great service!", "user": "user1", "created_at": "2024-09-20"},
                        {"id": 2, "message": "Good product!", "user": "user2", "created_at": "2024-10-01"}
                    ]
                }
            })
        }
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
            400: OpenApiResponse(description="Invalid data")
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
            400: OpenApiResponse(description="Error: Feedback not found or you do not have permission")
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
