import json
import traceback

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from backend.fund.FundPortfolio import FundPortfolio
from backend.fund.IndexFundSnapshot import IndexFundSnapshot
from backend.redis.RedisManager import RedisManager
from backend.user.FundUser import FundUser
from backend.util import clean_email


@api_view(['GET', 'POST', 'PUT', 'HEAD', 'DELETE', 'PATCH', 'OPTIONS'])
@permission_classes([AllowAny])
def do_nothing(request, resource):
    """
    Displays nothing when someone makes a call to an invalid API endpoint.
    """
    return Response('Nothing here...',
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def new_user(request):
    """
    Registers a new user, or returns the reason why user registration failed.
    Parameters:
        + 'email_address' of the new user
        + 'name' of the new user
        + 'password' for the new user
    """

    # Get parameters.
    email_address = request.POST.get('email_address', None)
    name = request.POST.get('name', None)
    password = request.POST.get('password', None)

    if True:
        pass
        # return Response('Test new user creation', status=status.HTTP_200_OK)

    # Validate parameter text.
    try:
        assert email_address is not None and name is not None and password is not None
        email_address = clean_email(email_address)
        assert 4 <= len(email_address.strip()) <= 150
        assert len(name.strip()) <= 150
        assert 8 <= len(password.strip()) <= 30
    except Exception as e:
        return Response(f"The request for a new user must include fields for both a unique "
                        f"'email_address' and a 'name' not longer than 150 characters, "
                        f"as well as a secure 'password' (containing uppercase, lowercase, number, and character) "
                        f"between 8 and 30 characters: {traceback.format_exc()}",
                        status=status.HTTP_400_BAD_REQUEST)

    # Check email input against existing emails to ensure uniqueness.
    try:
        new_user = User(username=email_address)
    except Exception as e:
        return Response(f'The email you entered has already been taken. Please '
                        f'try another email.  {traceback.format_exc()}',
                        status=status.HTTP_400_BAD_REQUEST)

    # Save new Django user in the SQL database.
    try:
        new_user.set_password(password)
        new_user.save()
    except Exception as e:
        return Response(f'Could not save user password: {traceback.format_exc()}',
                        status=status.HTTP_400_BAD_REQUEST)

    # Save name in Redis database.
    try:
        redis = RedisManager()
        if not redis.connect():
            raise ValueError('Could not initialize reddit connection')
        redis.save_new_user(user_email=email_address,
                            user_name=name)
    except Exception as e:
        return Response(f'Could not set user name in redis. User was created but could be corrupted:'
                        f' {traceback.format_exc()}',
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Return success.
    return Response(f"Successfully created auth user with email '{email_address}' and name '{name}'",
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def user_profile(request):
    """
    Returns a user profile containing data on the user,
        or an empty JSON object if user not found.

    NOTE: Anyone can pull this data on anyone else as long as they have an account.

    Parameters:
        + 'email_address' of the user
    """

    # Get parameters.
    email_address = request.POST.get('email_address', None)

    # Validate parameters.
    try:
        assert email_address is not None and len(email_address.strip()) > 2
        email_address = clean_email(email_address)
        assert len(email_address) >= 1
    except Exception as e:
        return Response("Invalid 'email_address' parameter",
                        status=status.HTTP_400_BAD_REQUEST)

    # Validate requester permissions.
    try:

        # ...ensure django user is not anonymous.
        django_user = request.user
        conditions = [django_user.is_superuser,
                      django_user.username == email_address]
        if django_user.is_anonymous or not any(conditions):
            return Response(f'You do not have permission to view the profile of {email_address}',
                            status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        traceback.print_exc()
        return Response(f'Could not load Django user matching your access token')

    # Get data from redis.
    redis = RedisManager()
    if not redis.connect():
        return Response('Error connecting to redis. See docker logs.',
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    user_profile = FundUser.from_db(email_address, redis)

    # Return the profile.
    return Response({} if user_profile is None else user_profile.to_json(), status=status.HTTP_200_OK)


@api_view(['POST'])
def save_fund(request):
    """
    Overwrites or creates a new index (portfolio) with a name
        that is unique to the fund manager.

    NOTE: An index fund can only be created in the name of the sender
        of this request, who must be authenticated with a Django.

    Parameters:
        + 'fund_id' string is required
        + 'manager_email' string is required and must equal to the auth user sending this request (unless admin)
        + 'investor_emails', string array is optional
        + 'portfolio' json object is optional,
            i.e. {tokens: [{token:BTC, portfolio_pct:1.2, buy_target:20000, sell_target:90000}, ...] }
    """

    # Get parameters.
    fund_id = request.POST.get('fund_id', None)
    manager_email = request.POST.get('manager_email', None)
    investor_emails = request.POST.get('investor_emails', [])
    portfolio_json = request.POST.get('portfolio', {})
    if isinstance(portfolio_json, str):
        try:
            portfolio_json = json.loads(portfolio_json)
        except Exception as e:
            portfolio_json = {}

    # Validate parameters.
    # ...validate manager email.
    try:
        assert manager_email is not None and len(manager_email.strip()) > 2
        manager_email = clean_email(manager_email)
        assert len(manager_email) >= 1
        if manager_email != request.user.username and not request.user.is_superuser:
            return Response(f"Invalid 'manager_email' parameter: you cannot create a fund under another user's email.",
                            status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(f"Invalid 'manager_email' parameter: {manager_email}",
                        status=status.HTTP_400_BAD_REQUEST)

    # ...validate fund id.
    try:
        if fund_id is None:
            return Response(f"Invalid 'fund_id' parameter: '{fund_id}'",
                    status=status.HTTP_400_BAD_REQUEST)
        fund_id = str(fund_id).lower().strip()
        redis = RedisManager()
        if not redis.connect():
            raise ValueError('Could not connect to redis')
        existing_manager = redis.get_fund_manager_email(fund_id)
        if existing_manager is not None and existing_manager != manager_email:
            return Response(f"{fund_id} is already managed by {existing_manager}. To switch managers, "
                            f"use /api/fund/transfer",
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        error_msg = f"ERROR! Could not validate 'fund_id' parameter: {traceback.format_exc()}"
        print(error_msg)
        return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ...sanitize investor emails.
    investor_emails = [clean_email(email) for email in investor_emails]
    investor_emails = list(dict.fromkeys(investor_emails))
    if manager_email in investor_emails:
        investor_emails.remove(manager_email)

    # ...convert input to Portfolio object.
    portfolio = FundPortfolio.from_json(portfolio_json)
    portfolio = FundPortfolio(tokens=[]) if portfolio is None else portfolio

    print(manager_email)
    print(f'{investor_emails}')
    print(f'{portfolio_json}')

    # Create fund object.
    fund_snapshot = IndexFundSnapshot(fund_id=fund_id,
                                      manager_email=manager_email,
                                      investor_emails=investor_emails,
                                      portfolio=portfolio)

    # Update fund data in Redis.
    redis.set_fund_manager_email(fund_id, manager_email)
    redis.set_fund_investor_emails(fund_id, investor_emails)
    redis.set_fund_portfolio(fund_id, portfolio)

    # Return new fund object.
    return Response(fund_snapshot.to_json(),
                    status=status.HTTP_200_OK)
