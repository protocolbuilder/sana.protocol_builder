from datetime import timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from mailer.tasks import send_email
from models import EmailConfirmationKey
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from forms import SignupForm

import logging
logger = logging.getLogger('auth')


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def _flattenFormErrors(form):
    errors = form.errors.as_data()
    error_messages = ''
    for field in errors:
        error_messages += ' '
        error_messages += field
        fieldErrors = errors[field]
        for error in fieldErrors:
            error_messages += str(error)
    return error_messages.strip()


# ------------------------------------------------------------------------------
#  Sign up
#
#  While there is some risk is removing csrf protection from the signup form
#  (http://stackoverflow.com/a/15604240), there really isn't any way to insert
#  a csrf token to the user since Django never serves up any frontend html
# ------------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['POST'])
def signup(request):
    form = SignupForm(request.POST)
    valid_form = form.is_valid()
    token_key = None

    if valid_form:
        user = form.save()
        token_key = Token.objects.get(user=user).key
        logger.info("Signup Success: u:{0} e:{0}".format(user.username, user.email))

        email_confirmation_key = EmailConfirmationKey.create_from_user(user)
        email_confirmation_key.save()

        # TODO(connor): Use an HTML template for emails
        send_email.delay(user.email,
                         "Account Confirmation for Sana Protocol Builder",
                         ("Please visit http://sanaprotocolbuilder.me/auth/confirm_email/{0} "
                          "to confirm your email address.").format(email_confirmation_key.key))
    else:
        logger.info("Signup Failed: {0}".format(_flattenFormErrors(form)))

    return JsonResponse({
        'success': valid_form,
        'errors': form.errors,
        'token': token_key,
    })


# ------------------------------------------------------------------------------
# Login
# ------------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    form = AuthenticationForm(data=request.POST)
    valid_form = form.is_valid()
    token_key = None

    if valid_form:
        form.clean()  # Calls authenticate(); will through ValidationException if form is invalid
        user = form.get_user()
        token, created = Token.objects.get_or_create(user=user)

        utc_now = timezone.now()
        if not created and token.created < utc_now - timedelta(hours=24):
            token.delete()
            token = Token.objects.create(user=user)
            token.created = utc_now
            token.save()

        token_key = token.key
        logger.info("Login Success: u:{0} e:{0}".format(user.username, user.email))
    else:
        logger.info("Login Failed: {0}".format(_flattenFormErrors(form)))

    return JsonResponse({
        'success': valid_form,
        'errors': form.errors,
        'token': token_key,
    })


# ------------------------------------------------------------------------------
# Logout
# ------------------------------------------------------------------------------

@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def logout(request):
    success = False

    if request.user:
        token = Token.objects.get(user=request.user)
        if token:
            token.delete()
        success = True

    return JsonResponse({
        'success': success,
    })


# ------------------------------------------------------------------------------
# Confirm Email
# ------------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['GET'])
def confirm_email(request, key):
    email_confirmation_key = get_object_or_404(EmailConfirmationKey, key=key)

    if email_confirmation_key.expiration < timezone.now():
        return HttpResponseBadRequest("Key expired")

    user_profile = email_confirmation_key.user.profile
    user_profile.is_email_confirmed = True
    user_profile.save()

    email_confirmation_key.delete()

    return JsonResponse({
        'success': True,
    })
