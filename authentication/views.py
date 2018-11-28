from rest_framework import permissions, viewsets, status, views
from rest_framework.decorators import action, permission_classes
from authentication.models import Account, EmailVerifyRecord
from authentication.permissions import IsAccountOwner
from authentication.serializers import AccountSerializer
import json
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from django.contrib.auth import logout
import authentication.utils.email_send as email_util
from core.utils.JWTExtension import JWTExtension
from core.utils.metadata import Metadata, MetaListdata, MetadataSerializer, MetadataListSerializer


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response(Metadata().serialized_data(), status=status.HTTP_204_NO_CONTENT)


class AccountViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), IsAccountOwner(),)

    def list(self, request, page=None, page_size=20):
        total = self.queryset.count()
        data = self.serializer_class(self.queryset, many=True).data
        return Response(MetaListdata(data=data, total=total).serialized_data())

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            account = Account.objects.create_user(**serializer.validated_data)
            email_util.send(account.email)

            return Response(
                Metadata(data=serializer.validated_data).serialized_data()
                , status=status.HTTP_201_CREATED)
        return Response({
            Metadata(status='BadRequest', message='Account could not be created with received data.').serialized_data()
        })

    def delete(self, request, username):
        account = Account.objects.get(username=username)

    @action(methods=['get'], detail=False)
    @permission_classes((permissions.IsAuthenticated,))
    def current(self, request):
        data = self.serializer_class(request.user).data
        return Response(
            Metadata(data=data).serialized_data()
        )


# @permission_classes((permissions.AllowAny,))
class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        account = authenticate(username=username, password=password)
        if account is not None:
            if account.email_verified:
                login(request, account)

                token = JWTExtension.generate_token(account)

                return Response(MetadataSerializer(Metadata(data={
                    'token': token,
                    'is_admin': account.is_admin,
                    'username': username,
                })).data)
            else:

                return Response(
                    Metadata(status='forbidden', message='Please active your account by email').serialized_data())
        else:

            return Response(
                    Metadata(status='unauthorized', message='Username/password combination invalid.').serialized_data()
                )


@permission_classes((permissions.AllowAny,))
class VerifiesViewSet(viewsets.ViewSet):
    queryset = EmailVerifyRecord.objects.all()

    @staticmethod
    def handle_register(record, account):
        account.email_verified = True
        account.save()
        record.delete()
        return 'register'

    @staticmethod
    def handle_forget():
        return 'forget'

    def retrieve(self, request, pk):
        record = self.queryset.get(code=pk)
        if record is None:
            return Response({
                'success': False,
                'message': 'code not exist',
            })
        account = Account.objects.get(email=record.email)
        if account is None:
            return Response(Metadata(status='NotFound', message='email not exist').serialized_data())

        handler = {
            'register': lambda _record, _account: self.handle_register(record=_record, account=_account),
            'forget': lambda _record, _account: self.handle_forget()
        }
        return Response(
            Metadata().serialized_data()
        )

    def create(self, request, format=None):
        data = request.data
        username = data.get('username', None)
        email = data.get('email', None)
        send_type = data.get('send_type', None)
        if send_type not in email_util.send_types_handler:
            return Response({
                'message': 'no such send type'
            }, status=status.HTTP_400_BAD_REQUEST)
        account = Account.objects.get(username=username)
        if account is None:
            return Response(Metadata('NotFound', message='Username/email combination invalid').serialized_data())
        if account.email != email:
            return Response(Metadata('NotFound', message='Username/email combination invalid').serialized_data())
        email_util.send(email, send_type)
        return Response(Metadata().serialized_data())

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk):
        data = request.data
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            return Response(
                Metadata(status='fail', message='password not equal with confirm password').serialized_data()
            )
        email = self.queryset.get(code=pk)
        if email is None:
            return Response(
                Metadata(status='NotFound', message='code is not correct').serialized_data()
            )
        account = Account.objects.get(email=email.email)
        if account is None:
            return Response(
                Metadata(status='NotFound', message='email has not been registered').serialized_data()
            )
        account.set_password(password)
        account.save()
        email.delete()
        token = JWTExtension.generate_token(account)
        return Response(Metadata(data={
            'token': token,
            'is_admin': account.is_admin
        }).serialized_data())
