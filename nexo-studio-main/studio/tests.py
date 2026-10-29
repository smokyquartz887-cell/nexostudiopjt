
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse

from .models import Business, FAQItem, Page


class TenantIsolationTests(TestCase):
    def setUp(self):
        cache.clear()

        self.user_a = User.objects.create_user(
            username="cliente_a",
            password="Teste123!senha",
        )
        self.user_b = User.objects.create_user(
            username="cliente_b",
            password="Teste123!senha",
        )

        self.a = Business.objects.create(
            owner=self.user_a,
            name="Negocio A",
            slug="negocio-a",
            published=True,
        )
        self.b = Business.objects.create(
            owner=self.user_b,
            name="Negocio B",
            slug="negocio-b",
            published=True,
        )

        self.page_a = Page.objects.create(
            business=self.a,
            title="Privado A",
            slug="privado-a",
        )
        self.page_b = Page.objects.create(
            business=self.b,
            title="Privado B",
            slug="privado-b",
        )

        self.faq_a = FAQItem.objects.create(
            business=self.a,
            question="Qual horário A?",
            answer="Resposta privada A",
        )
        self.faq_b = FAQItem.objects.create(
            business=self.b,
            question="Qual horário B?",
            answer="Resposta privada B",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_edit_another_business_page(self):
        self.client.login(
            username="cliente_a",
            password="Teste123!senha",
        )

        response = self.client.get(
            reverse("page_edit", args=[self.page_b.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_business_faq(self):
        self.client.login(
            username="cliente_a",
            password="Teste123!senha",
        )

        response = self.client.post(
            reverse("faq_delete", args=[self.faq_b.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            FAQItem.objects.filter(pk=self.faq_b.pk).exists()
        )

    def test_public_chatbot_uses_only_business_faq(self):
        response = self.client.post(
            reverse("chatbot_api", args=[self.a.slug]),
            data='{"pergunta":"Qual horário A?"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Resposta privada A",
            response.json()["resposta"],
        )
        self.assertNotIn(
            "Resposta privada B",
            response.json()["resposta"],
        )

    def test_business_switch_rejects_other_owner(self):
        self.client.login(
            username="cliente_a",
            password="Teste123!senha",
        )

        response = self.client.post(
            reverse("switch_business"),
            {"business_id": self.b.pk},
        )

        self.assertEqual(response.status_code, 404)

    def test_faq_is_unique_per_business_not_globally(self):
        FAQItem.objects.create(
            business=self.b,
            question="Pergunta igual",
            answer="B",
        )
        FAQItem.objects.create(
            business=self.a,
            question="Pergunta igual",
            answer="A",
        )

        self.assertEqual(
            FAQItem.objects.filter(
                question="Pergunta igual"
            ).count(),
            2,
        )


class SecurityLayerTests(TestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username="security_user",
            password="Teste123!senha",
        )
        self.business = Business.objects.create(
            owner=self.user,
            name="Segurança",
            slug="seguranca",
            published=True,
        )

        FAQItem.objects.create(
            business=self.business,
            question="Horário",
            answer="Das 9h às 18h",
        )

    def test_api_rejects_non_json_content_type(self):
        response = self.client.post(
            reverse("chatbot_api", args=[self.business.slug]),
            data="pergunta=oi",
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, 415)

    def test_api_rejects_json_array(self):
        response = self.client.post(
            reverse("chatbot_api", args=[self.business.slug]),
            data='["oi"]',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_api_rejects_question_over_limit(self):
        payload = '{"pergunta":"' + ("x" * 501) + '"}'

        response = self.client.post(
            reverse("chatbot_api", args=[self.business.slug]),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_security_headers_are_added(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(
            response["X-Content-Type-Options"],
            "nosniff",
        )
        self.assertEqual(
            response["Referrer-Policy"],
            "strict-origin-when-cross-origin",
        )

    @override_settings(
        SECRET_KEY="x" * 50,
        DEBUG=False,
        ALLOWED_HOSTS=["testserver"],
    )
    def test_rate_limit_blocks_excessive_requests(self):
        from security.api_security import enforce_rate_limit

        request = RequestFactory().post(
            "/api/chat/seguranca/",
            REMOTE_ADDR="192.0.2.1",
        )

        statuses = []

        for _ in range(31):
            response = enforce_rate_limit(
                request,
                scope="test",
                limit=30,
                window=60,
            )
            statuses.append(
                response.status_code if response else 200
            )

        self.assertEqual(statuses[-1], 429)
