import csv
import io
import re
import unicodedata
import json
from datetime import date, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from security.api_security import enforce_rate_limit
from security.validation import parse_json_object, clean_chat_question, MAX_JSON_BODY_BYTES
from security.audit import log_security_event
from security.authorization import get_business_or_404, get_owned_object_or_404
from .models import Business, Page, Offering, Activity, FAQItem, ChatInteraction
from .forms import SignUpForm, BusinessForm, PageForm, OfferingForm, ActivityForm, FAQItemForm
from .sector_images import SECTOR_IMAGES

def landing(request):
    return render(request,'studio/landing.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Conta criada! Vamos configurar seu negócio.'
            )
            return redirect('business_create')
    else:
        form = SignUpForm()

    return render(
        request,
        'studio/signup.html',
        {
            'form': form,
            'title': 'Crie sua conta',
            'subtitle': 'Seu próximo site começa aqui.',
        }
    )

def owner_businesses(user): return Business.objects.filter(owner=user)

def current_business(request):
    """Retorna somente negócio do usuário autenticado; seleção fica na sessão."""
    businesses = owner_businesses(request.user)
    selected_id = request.session.get('active_business_id')
    if selected_id:
        selected = businesses.filter(pk=selected_id).first()
        if selected:
            return selected
    return businesses.order_by('id').first()

@login_required
def switch_business(request):
    # POST-only evita mudança de contexto por link ou prefetch.
    if request.method != 'POST':
        return redirect('dashboard')
    business = get_business_or_404(user=request.user, business_id=request.POST.get('business_id'))
    request.session['active_business_id'] = business.pk
    messages.success(request, f'Negócio ativo: {business.name}.')
    return redirect('dashboard')

@login_required
def dashboard(request):
    businesses=owner_businesses(request.user)
    business=current_business(request)
    if not business: return redirect('business_create')
    activities=business.activities.all()[:6]
    today=date.today(); start=today-timedelta(days=6)
    daily=[]
    for i in range(7):
        day=start+timedelta(days=i)
        daily.append({'label':day.strftime('%d/%m'),'count':business.activities.filter(activity_date=day).count()})
    total_activities=business.activities.count()
    open_activities=business.activities.exclude(status__in=['concluida','cancelada']).count()
    revenue=business.activities.filter(kind='venda',status='concluida').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    context={'business':business,'businesses':businesses,'activities':activities,'daily':daily,'daily_json':json.dumps(daily),'total_activities':total_activities,'open_activities':open_activities,'revenue':revenue,'offerings_count':business.offerings.count(),'pages_count':business.pages.count()}
    return render(request,'studio/dashboard.html',context)

@login_required
def business_create(request):
    if request.method=='POST':
        form=BusinessForm(request.POST,request.FILES)
        if form.is_valid():
            business=form.save(commit=False); business.owner=request.user
            business.save()
            request.session['active_business_id'] = business.pk
            Page.objects.bulk_create([Page(business=business,title='Sobre nós',slug='sobre',menu_label='Sobre',body=business.description,sort_order=1),Page(business=business,title='Contato',slug='contato',menu_label='Contato',body='Entre em contato pelos canais informados.',sort_order=2)])
            messages.success(request,'Negócio criado! Seu site já tem uma estrutura inicial.')
            return redirect('dashboard')
    else: form=BusinessForm()
    return render(request,'studio/form_page.html',{'form':form,'title':'Configure seu negócio','subtitle':'Essas informações dão personalidade ao seu site.','wide':True})

@login_required
def business_edit(request):
    business=current_business(request)
    if not business: return redirect('business_create')
    if request.method=='POST':
        form=BusinessForm(request.POST,request.FILES,instance=business)
        if form.is_valid(): form.save(); messages.success(request,'Identidade do negócio atualizada.'); return redirect('business_edit')
    else: form=BusinessForm(instance=business)
    return render(request,'studio/form_page.html',{'form':form,'title':'Identidade do negócio','subtitle':'Personalize informações, cores, estilo e imagens.','wide':True,'business':business})

@login_required
def pages_list(request):
    b=current_business(request)
    if not b: return redirect('business_create')
    return render(request,'studio/list_pages.html',{'business':b,'items':b.pages.all()})
@login_required
def page_create(request):
    b=current_business(request)
    if request.method=='POST':
        form=PageForm(request.POST)
        if form.is_valid():
            item=form.save(commit=False); item.business=b; item.slug=slugify(item.title) or 'pagina'; base=item.slug; n=2
            while Page.objects.filter(business=b,slug=item.slug).exists(): item.slug=f'{base}-{n}'; n+=1
            if not item.menu_label: item.menu_label=item.title
            item.save(); messages.success(request,'Página criada.'); return redirect('pages_list')
    else: form=PageForm()
    return render(request,'studio/form_page.html',{'form':form,'title':'Nova página','subtitle':'Adicione conteúdo ao site.'})
@login_required
def page_edit(request,pk):
    b=current_business(request); item=get_owned_object_or_404(Page.objects.all(), business=b, object_id=pk)
    if request.method=='POST':
        form=PageForm(request.POST,instance=item)
        if form.is_valid():
            obj=form.save(commit=False); obj.slug=slugify(obj.title) or item.slug; obj.save(); messages.success(request,'Página atualizada.'); return redirect('pages_list')
    else: form=PageForm(instance=item)
    return render(request,'studio/form_page.html',{'form':form,'title':'Editar página','subtitle':'Atualize o conteúdo do site.'})
@login_required
def page_delete(request,pk):
    b=current_business(request); item=get_owned_object_or_404(Page.objects.all(), business=b, object_id=pk)
    if request.method=='POST': item.delete(); messages.success(request,'Página removida.')
    return redirect('pages_list')

@login_required
def offerings_list(request):
    b=current_business(request)
    if not b: return redirect('business_create')
    return render(request,'studio/list_offerings.html',{'business':b,'items':b.offerings.all()})
@login_required
def offering_create(request):
    b=current_business(request)
    if request.method=='POST':
        form=OfferingForm(request.POST)
        if form.is_valid(): item=form.save(commit=False); item.business=b; item.save(); messages.success(request,'Item cadastrado.'); return redirect('offerings_list')
    else: form=OfferingForm()
    return render(request,'studio/form_page.html',{'form':form,'title':'Novo produto ou serviço','subtitle':'Cadastre o que seu negócio oferece.'})
@login_required
def offering_edit(request,pk):
    b=current_business(request); item=get_owned_object_or_404(Offering.objects.all(), business=b, object_id=pk)
    if request.method=='POST':
        form=OfferingForm(request.POST,instance=item)
        if form.is_valid(): form.save(); messages.success(request,'Cadastro atualizado.'); return redirect('offerings_list')
    else: form=OfferingForm(instance=item)
    return render(request,'studio/form_page.html',{'form':form,'title':'Editar produto ou serviço','subtitle':'Atualize as informações.'})
@login_required
def offering_delete(request,pk):
    b=current_business(request); item=get_owned_object_or_404(Offering.objects.all(), business=b, object_id=pk)
    if request.method=='POST': item.delete(); messages.success(request,'Cadastro removido.')
    return redirect('offerings_list')

@login_required
def activities_list(request):
    b=current_business(request)
    if not b: return redirect('business_create')
    items=b.activities.all()
    kind=request.GET.get('kind'); status=request.GET.get('status')
    if kind: items=items.filter(kind=kind)
    if status: items=items.filter(status=status)
    return render(request,'studio/list_activities.html',{'business':b,'items':items,'selected_kind':kind or '', 'selected_status':status or ''})
@login_required
def activity_create(request):
    b=current_business(request)
    if request.method=='POST':
        form=ActivityForm(request.POST)
        if form.is_valid(): item=form.save(commit=False); item.business=b; item.save(); messages.success(request,'Movimentação registrada.'); return redirect('activities_list')
    else: form=ActivityForm(initial={'activity_date':date.today()})
    return render(request,'studio/form_page.html',{'form':form,'title':'Nova movimentação','subtitle':'Registre contatos, vendas, agendamentos ou tarefas.'})
@login_required
def activity_edit(request,pk):
    b=current_business(request); item=get_owned_object_or_404(Activity.objects.all(), business=b, object_id=pk)
    if request.method=='POST':
        form=ActivityForm(request.POST,instance=item)
        if form.is_valid(): form.save(); messages.success(request,'Movimentação atualizada.'); return redirect('activities_list')
    else: form=ActivityForm(instance=item)
    return render(request,'studio/form_page.html',{'form':form,'title':'Editar movimentação','subtitle':'Atualize os dados do registro.'})
@login_required
def activity_delete(request,pk):
    b=current_business(request); item=get_owned_object_or_404(Activity.objects.all(), business=b, object_id=pk)
    if request.method=='POST': item.delete(); messages.success(request,'Movimentação removida.')
    return redirect('activities_list')

@login_required
def reports(request):
    b=current_business(request)
    if not b: return redirect('business_create')
    by_kind=list(b.activities.values('kind').annotate(total=Count('id')).order_by('kind'))
    by_status=list(b.activities.values('status').annotate(total=Count('id')).order_by('status'))
    sales=b.activities.filter(kind='venda',status='concluida').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    return render(request,'studio/reports.html',{'business':b,'by_kind':by_kind,'by_status':by_status,'sales':sales,'total':b.activities.count(),'offerings':b.offerings.count()})
@login_required
def export_csv(request):
    b=current_business(request)
    response=HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition']='attachment; filename="relatorio-movimentacoes.csv"'
    writer=csv.writer(response,delimiter=';'); writer.writerow(['Data','Título','Tipo','Status','Valor (R$)','Observações'])
    for a in b.activities.all(): writer.writerow([a.activity_date,a.title,a.get_kind_display(),a.get_status_display(),a.amount,a.notes])
    return response

@login_required
def image_library(request):
    b=current_business(request)
    if not b: return redirect('business_create')
    return render(request,'studio/image_library.html',{'business':b,'images':SECTOR_IMAGES.get(b.sector,SECTOR_IMAGES['outro'])})
@login_required
def choose_image(request,index):
    b=current_business(request)
    images=SECTOR_IMAGES.get(b.sector,SECTOR_IMAGES['outro'])
    if request.method=='POST' and index>=0 and index<len(images):
        b.hero_image=images[index][1]; b.save(update_fields=['hero_image','updated_at']); messages.success(request,'Imagem selecionada para o destaque do site.')
    return redirect('image_library')

def public_site(request,slug):
    b=get_object_or_404(Business,slug=slug,published=True)
    pages=b.pages.filter(is_visible=True); offerings=b.offerings.filter(active=True)
    return render(request,'studio/public_site.html',{'business':b,'pages':pages,'offerings':offerings})


def _normalize_text(value):
    value = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9 ]+', ' ', value).strip()

@login_required
def faq_list(request):
    business = current_business(request)
    if not business: return redirect('business_create')
    return render(request, 'studio/faq_list.html', {'business': business, 'items': business.faq_items.all()})

@login_required
def faq_create(request):
    business = current_business(request)
    if request.method == 'POST':
        form = FAQItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False); item.business = business
            try: item.save()
            except Exception:
                form.add_error('question', 'Já existe uma pergunta igual cadastrada para este negócio.')
            else:
                messages.success(request, 'Pergunta e resposta cadastradas.'); return redirect('faq_list')
    else: form = FAQItemForm()
    return render(request, 'studio/form_page.html', {'form': form, 'title': 'Nova pergunta e resposta', 'subtitle': 'Alimente a base de conhecimento do chatbot.'})

@login_required
def faq_edit(request, pk):
    business = current_business(request); item = get_owned_object_or_404(FAQItem.objects.all(), business=business, object_id=pk)
    if request.method == 'POST':
        form = FAQItemForm(request.POST, instance=item)
        if form.is_valid(): form.save(); messages.success(request, 'Pergunta atualizada.'); return redirect('faq_list')
    else: form = FAQItemForm(instance=item)
    return render(request, 'studio/form_page.html', {'form': form, 'title': 'Editar pergunta e resposta', 'subtitle': 'Atualize a resposta usada pelo chatbot.'})

@login_required
def faq_delete(request, pk):
    business = current_business(request); item = get_owned_object_or_404(FAQItem.objects.all(), business=business, object_id=pk)
    if request.method == 'POST': item.delete(); messages.success(request, 'Pergunta removida da base.')
    return redirect('faq_list')

@login_required
def faq_import(request):
    business = current_business(request)
    if request.method != 'POST' or 'file' not in request.FILES:
        messages.error(request, 'Selecione um arquivo CSV para importar.'); return redirect('faq_list')
    uploaded = request.FILES['file']
    if uploaded.size > 1024 * 1024:
        messages.error(request, 'O arquivo deve ter no máximo 1 MB.'); return redirect('faq_list')
    try:
        content = uploaded.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content), delimiter=';')
        fields = {x.strip().lower() for x in (reader.fieldnames or [])}
        if not {'pergunta', 'resposta'}.issubset(fields): raise ValueError('O CSV precisa ter as colunas pergunta;resposta e, opcionalmente, palavras_chave;ativa.')
        count = 0
        for row in reader:
            row = {str(k).strip().lower(): (v or '').strip() for k, v in row.items() if k}
            question, answer = row.get('pergunta', ''), row.get('resposta', '')
            if not question or not answer: continue
            FAQItem.objects.update_or_create(business=business, question=question, defaults={'answer': answer, 'keywords': row.get('palavras_chave', ''), 'active': row.get('ativa', 'sim').lower() not in ('nao','não','0','false')})
            count += 1
        messages.success(request, f'{count} pergunta(s) importada(s) ou atualizada(s).')
    except (UnicodeDecodeError, csv.Error, ValueError) as exc:
        messages.error(request, f'Não foi possível importar o arquivo: {exc}')
    return redirect('faq_list')

@csrf_exempt
def chatbot_api(request, slug):
    """API pública do chatbot: JSON limitado, rate limit e FAQ isolada por negócio.

    CSRF é dispensado porque este endpoint é público e chamado por visitantes anônimos;
    não executa ações autenticadas nem altera dados de negócio. A proteção contra abuso
    é complementada por limite de tamanho e requisições por IP.
    """
    if request.method != 'POST':
        response = JsonResponse({'erro': 'Use POST com JSON {"pergunta": "..."}.'}, status=405)
        response['Allow'] = 'POST'
        return response
    if request.content_type != 'application/json':
        return JsonResponse({'erro': 'Content-Type deve ser application/json.'}, status=415)
    try:
        content_length = int(request.META.get('CONTENT_LENGTH') or 0)
    except (TypeError, ValueError):
        return JsonResponse({'erro': 'Content-Length inválido.'}, status=400)
    if content_length > MAX_JSON_BODY_BYTES:
        log_security_event('chat_payload_too_large', request=request, detail=f'bytes={content_length}')
        return JsonResponse({'erro': 'A requisição excede o tamanho máximo permitido.'}, status=413)
    limited = enforce_rate_limit(request, scope=f'chat:{slug}')
    if limited:
        log_security_event('chat_rate_limit', request=request, detail=f'slug={slug}')
        return limited
    business = get_object_or_404(Business, slug=slug, published=True)
    try:
        payload = parse_json_object(request.body)
        question = clean_chat_question(payload.get('pergunta', ''))
    except ValidationError as exc:
        return JsonResponse({'erro': str(exc.message if hasattr(exc, 'message') else exc.messages[0])}, status=400)
    normalized = _normalize_text(question)
    best, best_score = None, 0
    for faq in business.faq_items.filter(active=True):
        candidates = [faq.question] + [k.strip() for k in faq.keywords.split(',') if k.strip()]
        score = 0
        for candidate in candidates:
            candidate_norm = _normalize_text(candidate)
            if candidate_norm and candidate_norm in normalized:
                score = max(score, len(candidate_norm) + 10)
            else:
                words = [w for w in candidate_norm.split() if len(w) > 2]
                overlap = sum(1 for word in words if word in normalized.split())
                score = max(score, overlap)
        if score > best_score:
            best, best_score = faq, score
    if best and best_score >= 1:
        answer = best.answer
        matched = best
    else:
        answer = f'Obrigado pelo contato com {business.name}! Ainda não encontrei uma resposta específica para essa pergunta. Entre em contato pelo e-mail {business.email or "informado no site"} ou telefone {business.phone or "disponível na página"}.'
        matched = None
    ChatInteraction.objects.create(business=business, question=question, answer=answer, matched_faq=matched)
    return JsonResponse({'resposta': answer, 'encontrada': bool(matched), 'negocio': business.name})

def api_documentation(request):
    return JsonResponse({'nome': 'Nexo Studio Chatbot API', 'versao': '1.1', 'endpoint': '/api/chat/<slug>/', 'metodo': 'POST', 'content_type': 'application/json', 'limites': {'corpo_maximo_bytes': 8192, 'pergunta_maximo_caracteres': 500, 'requisicoes_por_ip': 30, 'janela_segundos': 60}, 'erros': {'400': 'JSON ou pergunta inválidos', '405': 'Método não permitido', '413': 'Corpo muito grande', '415': 'Content-Type deve ser application/json', '429': 'Limite de requisições excedido'}, 'exemplo': {'pergunta': 'Qual o horário de atendimento?'}, 'resposta': {'resposta': 'Texto da resposta', 'encontrada': True, 'negocio': 'Nome do negócio'}, 'nota': 'O chatbot usa as perguntas e respostas cadastradas pelo proprietário. Não é uma IA generativa; não inventa respostas e registra interações para auditoria. O rate limiting local é demonstrativo e deve ser substituído/reforçado por cache compartilhado e proteção de borda em produção.'})

