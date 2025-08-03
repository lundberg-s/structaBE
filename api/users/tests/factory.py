from users.models import User


class UserFactory:
    @classmethod
    def create(cls, tenant, username=None, password=None, email=None, **kwargs):
        return User.objects.create_user(
            username=username,
            password=password,
            email=email,
            tenant=tenant,
            **kwargs
        )


