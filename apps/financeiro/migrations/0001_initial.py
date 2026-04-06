import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0002_delete_gasto"),
    ]

    operations = [
        migrations.CreateModel(
            name="Entrada",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("projeto", "Projeto"),
                            ("investimento", "Investimento"),
                            ("outros", "Outros"),
                        ],
                        max_length=32,
                    ),
                ),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("data_transacao", models.DateField()),
                (
                    "projeto",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="entradas",
                        to="core.projeto",
                    ),
                ),
            ],
            options={
                "verbose_name": "entrada",
                "verbose_name_plural": "entradas",
                "ordering": ("-data_transacao",),
            },
        ),
        migrations.CreateModel(
            name="Gasto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("material", "Material"),
                            ("mao_de_obra", "Mão de obra"),
                            ("licenca", "Licença"),
                            ("fixo", "Fixo"),
                            ("outros", "Outros"),
                        ],
                        max_length=32,
                    ),
                ),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("data_transacao", models.DateField()),
                (
                    "vinculo_licenciamento",
                    models.BooleanField(
                        default=False,
                        help_text="Se verdadeiro, a categoria é fixada em Licença (RF03).",
                    ),
                ),
                (
                    "parceiro",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="gastos",
                        to="core.parceiro",
                    ),
                ),
                (
                    "projeto",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="gastos",
                        to="core.projeto",
                    ),
                ),
            ],
            options={
                "verbose_name": "gasto",
                "verbose_name_plural": "gastos",
                "ordering": ("-data_transacao",),
            },
        ),
    ]
