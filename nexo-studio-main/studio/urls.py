
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Página pública e autenticação
    path("", views.landing, name="landing"),
    path("conta/criar/", views.signup, name="signup"),
    path(
        "conta/entrar/",
        auth_views.LoginView.as_view(
            template_name="studio/login.html"
        ),
        name="login",
    ),
    path(
        "conta/sair/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # Painel e gerenciamento do negócio
    path("painel/", views.dashboard, name="dashboard"),
    path(
        "negocio/selecionar/",
        views.switch_business,
        name="switch_business",
    ),
    path("negocio/novo/", views.business_create, name="business_create"),
    path(
        "negocio/identidade/",
        views.business_edit,
        name="business_edit",
    ),

    # Páginas e menus
    path("paginas/", views.pages_list, name="pages_list"),
    path("paginas/nova/", views.page_create, name="page_create"),
    path(
        "paginas/<int:pk>/editar/",
        views.page_edit,
        name="page_edit",
    ),
    path(
        "paginas/<int:pk>/excluir/",
        views.page_delete,
        name="page_delete",
    ),

    # Produtos e serviços
    path("catalogo/", views.offerings_list, name="offerings_list"),
    path("catalogo/novo/", views.offering_create, name="offering_create"),
    path(
        "catalogo/<int:pk>/editar/",
        views.offering_edit,
        name="offering_edit",
    ),
    path(
        "catalogo/<int:pk>/excluir/",
        views.offering_delete,
        name="offering_delete",
    ),

    # Movimentações
    path("movimentacoes/", views.activities_list, name="activities_list"),
    path(
        "movimentacoes/nova/",
        views.activity_create,
        name="activity_create",
    ),
    path(
        "movimentacoes/<int:pk>/editar/",
        views.activity_edit,
        name="activity_edit",
    ),
    path(
        "movimentacoes/<int:pk>/excluir/",
        views.activity_delete,
        name="activity_delete",
    ),

    # Relatórios
    path("relatorios/", views.reports, name="reports"),
    path("relatorios/exportar/", views.export_csv, name="export_csv"),

    # Biblioteca de imagens
    path("imagens/", views.image_library, name="image_library"),
    path(
        "imagens/<int:index>/selecionar/",
        views.choose_image,
        name="choose_image",
    ),

    # Chatbot e perguntas frequentes
    path("perguntas/", views.faq_list, name="faq_list"),
    path("perguntas/nova/", views.faq_create, name="faq_create"),
    path(
        "perguntas/<int:pk>/editar/",
        views.faq_edit,
        name="faq_edit",
    ),
    path(
        "perguntas/<int:pk>/excluir/",
        views.faq_delete,
        name="faq_delete",
    ),
    path("perguntas/importar/", views.faq_import, name="faq_import"),

    # API
    path(
        "api/chat/<slug:slug>/",
        views.chatbot_api,
        name="chatbot_api",
    ),
    path(
        "api/documentacao/",
        views.api_documentation,
        name="api_documentation",
    ),

    # Site público de cada negócio
    path("s/<slug:slug>/", views.public_site, name="public_site"),
]
