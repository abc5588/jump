from django.urls import path
from rest_framework_bulk.routes import BulkRouter
from .. import api

app_name = 'acls'

router = BulkRouter()
router.register(r'asset', api.AssetACLViewSet, 'asset')

urlpatterns = [
    path(r'asset/login-confirm/', api.ValidateAssetLoginConfirmApi.as_view(), name='validate-asset-login-confirm'),
    path(r'ticket/status/', api.TicketStatusApi.as_view(), name='ticket-status')
]

urlpatterns += router.urls
