from django.urls import path
from .views import Gitlab_push_webhookAPIView, Gitlab_MR_Opened_webhookAPIView, Gitlab_MR_Merged_Notif_webhookAPIView, Gitlab_MR_Merged_Label_webhookAPIView

urlpatterns = [
    path('push_rea', Gitlab_push_webhookAPIView.as_view(), name='gitlab-push-webhook'),
    path('mr_opened_rea', Gitlab_MR_Opened_webhookAPIView.as_view(), name='gitlab-mr-opened-webhook'),
    path('merged-notif_rea', Gitlab_MR_Merged_Notif_webhookAPIView.as_view(), name='gitlab-merged-notif-webhook'),
    path('change-label_rea', Gitlab_MR_Merged_Label_webhookAPIView.as_view(), name='gitlab-change-label-webhook'),
]
