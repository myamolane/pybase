from rest_framework_jwt.settings import api_settings


class JWTExtension:
    @staticmethod
    def generate_token(account):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(account)
        token = jwt_encode_handler(payload)
        return token
