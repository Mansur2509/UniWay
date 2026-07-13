import logging

from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        database_status = "unavailable"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            database_status = "ok"
        except Exception:
            logger.warning("Database health check failed.")

        status_code = 200 if database_status == "ok" else 503
        return Response(
            {"status": "ok" if status_code == 200 else "degraded", "database": database_status},
            status=status_code,
        )
