# -*- coding: utf-8 -*-

from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth


if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    db = DAL('google:datastore+ndb')
    session.connect(request, response, db=db)



response.generic_patterns = [] 
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''



auth = Auth(db, host_names=configuration.get('host.names'))

auth.settings.table_user_name = 'usuario'
auth.settings.table_group_name = 'setor'
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 1 #paliativamente, pois após ser enviado para produção,s erá 2  que é igual a 'Colaborador'


auth.settings.extra_fields['usuario'] = [
    Field('cargo', 'string', label='Cargo'),
]
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

                                 
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------

# Tabela de metas
db.define_table('metas',
    Field('titulo', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('descricao', 'text', requires=IS_NOT_EMPTY(), notnull=True),
    Field('valor', 'decimal(10,2)', requires=IS_DECIMAL_IN_RANGE(0, None), notnull=True),
    Field('tipo', 'string', requires=IS_IN_SET(['venda', 'prospeccao', 'contato']), notnull=True),
    Field('colaborador_id', 'reference usuario', requires=IS_IN_DB(db, 'usuario.id', '%(first_name)s %(last_name)s'), notnull=True),
    Field('data_criacao', 'datetime', default=request.now, writable=False, notnull=True),
    Field('data_limite', 'datetime', requires=IS_NOT_EMPTY(), notnull=True)
)


# Tabela de clientes
db.define_table('clientes',
    Field('nome', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('cpf_cnpj', 'string', requires=IS_NOT_EMPTY(), label='CPF/CNPJ', notnull=True),
    Field('email', 'string', requires=IS_EMAIL(), notnull=True),
    Field('telefone', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('empresa', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('cidade', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('status', 'string', requires=IS_IN_SET(['ativo', 'inativo', 'potencial']), notnull=True)
)

# Tabela de agendamentos
db.define_table('agendamentos',
    Field('titulo', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('cliente_id', 'reference clientes', notnull=True, requires=IS_IN_DB(db, 'clientes.id', '%(nome)s')),
    Field('descricao', 'text', requires=IS_NOT_EMPTY(), notnull=True),
    Field('horario_inicio', 'datetime', requires=IS_NOT_EMPTY(), notnull=True),
    Field('horario_fim', 'datetime', requires=IS_NOT_EMPTY(), notnull=True),
    Field('recorrente', 'boolean', default=False, notnull=True),
    Field('recorrencia_dias', 'integer', default=None)
)

# Tabela de tarefas
db.define_table('tarefas',
    Field('titulo', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('descricao', 'text', requires=IS_NOT_EMPTY(), notnull=True),
    Field('colaborador_id', 'reference usuario', requires=IS_IN_DB(db, 'usuario.id', '%(first_name)s %(last_name)s'), notnull=True),
    Field('cliente_id', 'reference clientes', default=None, requires=IS_EMPTY_OR(IS_IN_DB(db, 'clientes.id', '%(nome)s')), notnull=True),
    Field('status', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('prioridade', 'string', requires=IS_IN_SET(['alta', 'media', 'baixa']), notnull=True),
    Field('data_criacao', 'datetime', default=request.now, writable=False, notnull=True),
    Field('data_conclusao', 'datetime', default=None, notnull=True)
)

# Tabela de atividades
db.define_table('atividades',
    Field('colaborador_id', 'reference usuario', requires=IS_IN_DB(db, 'usuario.id', '%(first_name)s %(last_name)s'), notnull=True),
    Field('cliente_id', 'reference clientes', default=None, requires=IS_EMPTY_OR(IS_IN_DB(db, 'clientes.id', '%(nome)s')), notnull=True),
    Field('data_atividade', 'datetime', default=request.now),
    Field('tipo', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('descricao_detalhes', 'text', requires=IS_NOT_EMPTY(), notnull=True),
    Field('resultado', 'string', requires=IS_NOT_EMPTY(), notnull=True),
    Field('proxima_interacao', 'datetime', requires=IS_NOT_EMPTY(), notnull=True)
)

if db(db.setor).count() == 0:
    db.setor.insert(role='Administrador', description='Role de Administrador')
    db.setor.insert(role='Colaborador', description='Role de Colaborador')
    db.setor.insert(role='Financeiro', description='Role de Financeiro')
    db.setor.insert(role='Vendas', description='Role de Vendas')

# Como o web2py opera com datas no formato AAAA/MM/DD, é necessário definir o formato de data para o padrão brasileiro
db.metas.data_criacao.requires = IS_DATE(format=T('%d/%m/%Y'), error_message='deve ser DD/MM/AAAA')
db.metas.data_limite.requires = IS_DATE(format=T('%d/%m/%Y'), error_message='deve ser DD/MM/AAAA')
db.agendamentos.horario_inicio.requires = IS_DATE_IN_RANGE(format=T('%d/%m/%Y %H:%M'), minimum=request.now, error_message='deve ser DD/MM/AAAA HH:MM')
db.agendamentos.horario_fim.requires = IS_DATE_IN_RANGE(format=T('%d/%m/%Y %H:%M'), minimum=request.now, error_message='deve ser DD/MM/AAAA HH:MM')
db.tarefas.data_criacao.requires = IS_DATE(format=T('%d/%m/%Y'), error_message='deve ser DD/MM/AAAA')
db.tarefas.data_conclusao.requires = IS_DATE(format=T('%d/%m/%Y'), error_message='deve ser DD/MM/AAAA')
db.atividades.data_atividade.requires = IS_DATE(format=T('%d/%m/%Y'), error_message='deve ser DD/MM/AAAA')
db.atividades.proxima_interacao.requires = IS_DATE(format=T('%d/%m/%Y'), error_message='deve ser DD/MM/AAAA')


db.commit()