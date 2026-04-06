from django.core.management.base import BaseCommand

from apps.licenciamento.services import executar_verificacao_vencimentos


class Command(BaseCommand):
    help = "RF08: verifica licenças críticas e gera notificações/e-mails para Admin e Gestor."

    def handle(self, *args, **options):
        n = executar_verificacao_vencimentos()
        self.stdout.write(self.style.SUCCESS(f"Notificações criadas: {n}"))
