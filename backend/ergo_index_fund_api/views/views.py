from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET', 'POST', 'PUT', 'HEAD', 'DELETE', 'PATCH', 'OPTIONS'])
@permission_classes([AllowAny])
def do_nothing(request, resource):
    """
    Displays nothing when someone makes a call to an invalid API endpoint.
    """
    return Response('Nothing here...',
                    status=status.HTTP_404_NOT_FOUND)
