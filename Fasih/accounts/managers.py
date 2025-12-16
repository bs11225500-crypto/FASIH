from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, name=None, role=None):
        if not email:
            raise ValueError("Email is required")

        user = self.model(
            email=self.normalize_email(email),
            name=name or "",
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name=None):
        user = self.create_user(
            email=email,
            password=password,
            name=name
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
