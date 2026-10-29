from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

SETORES = [('gastronomia','Gastronomia'),('beleza','Beleza e bem-estar'),('servicos','Serviços profissionais'),('varejo','Varejo e loja'),('tecnologia','Tecnologia'),('educacao','Educação'),('outro','Outro negócio')]
class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField('Nome do negócio', max_length=120)
    slug = models.SlugField(unique=True, max_length=150)
    sector = models.CharField('Setor', max_length=30, choices=SETORES, default='servicos')
    tagline = models.CharField('Frase de apresentação', max_length=180, blank=True)
    description = models.TextField('Descrição', blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=180, blank=True)
    logo = models.FileField(upload_to='logos/', blank=True)
    primary_color = models.CharField(max_length=7, default='#6558F5')
    secondary_color = models.CharField(max_length=7, default='#101828')
    accent_color = models.CharField(max_length=7, default='#D6F36A')
    font_style = models.CharField(max_length=20, default='moderna', choices=[('moderna','Moderna'),('classica','Clássica'),('minimalista','Minimalista')])
    hero_image = models.URLField(blank=True)
    uploaded_hero = models.FileField(upload_to='business-images/', blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self,*args,**kwargs):
        if not self.slug:
            base=slugify(self.name) or 'meu-negocio'; slug=base; n=2
            while Business.objects.filter(slug=slug).exclude(pk=self.pk).exists(): slug=f'{base}-{n}'; n+=1
            self.slug=slug
        super().save(*args,**kwargs)
    def __str__(self): return self.name

class Page(models.Model):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name='pages')
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    body = models.TextField(blank=True)
    menu_label = models.CharField(max_length=50,blank=True)
    is_visible = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['sort_order','title']; unique_together=[('business','slug')]
    def __str__(self): return self.title

class Offering(models.Model):
    TYPES=[('produto','Produto'),('servico','Serviço')]
    business=models.ForeignKey(Business,on_delete=models.CASCADE,related_name='offerings')
    kind=models.CharField(max_length=12,choices=TYPES,default='servico')
    name=models.CharField(max_length=120)
    description=models.TextField(blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['name']
    def __str__(self): return self.name

class Activity(models.Model):
    TYPES=[('lead','Novo contato'),('venda','Venda'),('agendamento','Agendamento'),('tarefa','Tarefa'),('outro','Outro')]
    STATUS=[('aberta','Aberta'),('em_andamento','Em andamento'),('concluida','Concluída'),('cancelada','Cancelada')]
    business=models.ForeignKey(Business,on_delete=models.CASCADE,related_name='activities')
    title=models.CharField(max_length=140)
    kind=models.CharField(max_length=20,choices=TYPES,default='tarefa')
    status=models.CharField(max_length=20,choices=STATUS,default='aberta')
    amount=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    notes=models.TextField(blank=True)
    activity_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-activity_date','-created_at']
    def __str__(self): return self.title


class FAQItem(models.Model):
    """Perguntas e respostas configuradas pelo responsável pelo negócio."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='faq_items')
    question = models.CharField('Pergunta', max_length=240)
    answer = models.TextField('Resposta')
    keywords = models.CharField('Palavras-chave', max_length=300, blank=True, help_text='Separe palavras e expressões por vírgula.')
    active = models.BooleanField('Ativa', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['question']
        constraints = [models.UniqueConstraint(fields=['business', 'question'], name='unique_business_faq_question')]
    def __str__(self): return f'{self.business.name}: {self.question}'

class ChatInteraction(models.Model):
    """Registro mínimo de interações para auditoria e melhoria do conteúdo."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='chat_interactions')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    matched_faq = models.ForeignKey(FAQItem, null=True, blank=True, on_delete=models.SET_NULL, related_name='interactions')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f'{self.business.name} — {self.created_at:%d/%m/%Y %H:%M}'
