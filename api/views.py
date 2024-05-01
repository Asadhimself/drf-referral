import time
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.fields import ObjectDoesNotExist
from rest_framework.generics import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema_view, extend_schema

from account.models import Account, InviteKey, PhoneToken

from .serializers import (
    AccountSerializer,
    PhoneTokenCreateSerializer,
    PhoneTokenValidateSerializer,
)


@extend_schema(tags=["Login"])
class LoginValidateCreateAPIView(APIView):
    serializer_class = PhoneTokenValidateSerializer()
    @extend_schema(
        summary="Register phone number and send OTP to get auth token",
        description="Step-by-step usage:\n"\
        "1) Send valid phone number. As a result, you will recieve OTP\n"\
        "2) Send phone number with recieved OTP. You will recieve Auth token"
    )
    def post(self, request, format=None):
        if request.data.get("phone_number") and not request.data.get(
            "otp"
        ):  # Create OTP
            serializer = PhoneTokenCreateSerializer(data=request.data)
            if serializer.is_valid():
                token = PhoneToken.create_otp_for_number(
                    request.data.get("phone_number")
                )
                phone_token = PhoneTokenCreateSerializer(token)
                data = phone_token.data

                time.sleep(2)
                data["otp"] = token.otp
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error_message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif request.data.get("phone_number") and request.data.get(
            "otp"
        ):  # Validate OTP and display TokenAuth
            serializer = PhoneTokenValidateSerializer(data=request.data)
            if serializer.is_valid():
                otp = request.data.get("otp")
                phone_number = request.data.get("phone_number")
                otp_obj = get_object_or_404(PhoneToken, phone_number=phone_number, otp=otp)
                if otp_obj.used:
                    return Response(
                        {"error_message": "OTP is already used"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user = authenticate(request, phone_number=phone_number, otp=otp)
                otp_obj.used = True
                otp_obj.save()
                if user is not None:
                    login(request, user, backend="account.backend.AccountBacked")
                    token, created = Token.objects.get_or_create(user=user)
                    data = {
                        "url_account": reverse_lazy("api:account"),
                        "token": token.key,
                    }
                    return Response(data)
                else:
                    return Response(
                        {"error_message": "OTP doesn't exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error_message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error_message": "send 'phone_number' or 'otp' options"},
                status=status.HTTP_400_BAD_REQUEST,
            )

@extend_schema(tags=["Profile"])
class AccountRetrieveUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_object(self, pk):
        try:
            return Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            raise Http404
    @extend_schema(
        summary="Get profile info. Works only with auth token in headers",
        description="example curl:\n"\
        "curl -H 'Authorization: Token your-auth-token' http://localhost:8000/api/account/"
    )
    def get(self, request, *args, **kwargs):
        user = self.get_object(request.user.pk)
        if user:
            serializer = self.serializer_class(user)
            data = {"url_account": reverse_lazy("api:account")}
            data.update(serializer.data)
            return Response(data)

    @extend_schema(
        summary="Change profile info. Works only with auth token in headers",
        description="example curl:\n"\
        "curl.exe -H 'Authorization: Token your-auth-token' -d 'invite=invite-code' -X PUT http://exmaple.com/api/account/"
    )
    def put(self, request, *args, **kwargs):
        user = self.get_object(request.user.pk)
        serializer = self.serializer_class(user, data=request.data, partial=True)

        if serializer.is_valid():
            if request.data.get("invite"):
                invite = request.data.get("invite")
                if user.invite:
                    return Response(
                        {"message": "You have already entered the invite code"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if user.user_invite.key == invite:
                    return Response(
                        {"message": "You can't enter your invite code."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                try:
                    invite_obj = InviteKey.objects.get(key=invite)
                except ObjectDoesNotExist:
                    return Response(
                        {"message": "Invite code doesn't exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                serializer.save(invite=invite_obj)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
