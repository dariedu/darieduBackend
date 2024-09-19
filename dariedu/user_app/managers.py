from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, tg_id, password=None, **extra_fields):
        """
            Create and save a user with the given tg id.
        """
        if not tg_id:
            raise ValueError("The Telegram ID must be set")

        user = self.model(tg_id=tg_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, tg_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(tg_id, password, **extra_fields)
