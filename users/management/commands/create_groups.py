from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from users.models import User

MODERATOR_GROUP = "Модератор продуктов"
CONTENT_MANAGER_GROUP = "Контент-менеджер"

# Группа -> список прав в формате (приложение, кодовое имя права)
GROUPS = {
    MODERATOR_GROUP: [
        ("catalog", "can_unpublish_product"),
        ("catalog", "delete_product"),
    ],
    CONTENT_MANAGER_GROUP: [
        ("blog", "view_blogpost"),
        ("blog", "add_blogpost"),
        ("blog", "change_blogpost"),
        ("blog", "delete_blogpost"),
    ],
}


class Command(BaseCommand):
    help = (
        "Создаёт группы «Модератор продуктов» и «Контент-менеджер» с нужными правами. "
        "Можно сразу добавить в группу пользователя: --moderator EMAIL, --content-manager EMAIL."
    )

    def add_arguments(self, parser):
        parser.add_argument("--moderator", metavar="EMAIL", help="Добавить пользователя в модераторы")
        parser.add_argument(
            "--content-manager", metavar="EMAIL", help="Добавить пользователя в контент-менеджеры"
        )

    def handle(self, *args, **options):
        for group_name, permission_keys in GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            permissions = []
            for app_label, codename in permission_keys:
                try:
                    permissions.append(
                        Permission.objects.get(
                            content_type__app_label=app_label, codename=codename
                        )
                    )
                except Permission.DoesNotExist as error:
                    raise CommandError(
                        f"Нет права {app_label}.{codename}. Сначала выполните migrate."
                    ) from error
            group.permissions.set(permissions)
            status = "создана" if created else "обновлена"
            codes = ", ".join(codename for _, codename in permission_keys)
            self.stdout.write(self.style.SUCCESS(f"Группа «{group_name}» {status}: {codes}"))

        self._add_user(options.get("moderator"), MODERATOR_GROUP)
        self._add_user(options.get("content_manager"), CONTENT_MANAGER_GROUP)

    def _add_user(self, email, group_name):
        if not email:
            return
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as error:
            raise CommandError(f"Пользователь {email} не найден.") from error
        user.groups.add(Group.objects.get(name=group_name))
        self.stdout.write(self.style.SUCCESS(f"{user.email} добавлен в группу «{group_name}»"))
