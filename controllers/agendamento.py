# controllers/agendamento.py
@auth.requires_login()
def index():
    """
    List all agendamentos
    """
    app_name = request.application
    agendamentos = db(db.agendamentos).select()
    return dict(agendamentos=agendamentos,app_name=app_name)

@auth.requires_login()
def create():
    """
    Create a new agendamento
    """
    form = SQLFORM(db.agendamentos).process()
    if form.accepted:
        response.flash = 'Agendamento criado com sucesso!'
        redirect(URL('index'))
    elif form.errors:
        response.flash = 'Erro no formulário!'
    return dict(form=form)

@auth.requires_login()
def read():
    """
    Read a specific agendamento
    """
    agendamento_id = request.args(0, cast=int)
    agendamento = db.agendamentos(agendamento_id) or redirect(URL('index'))
    return dict(agendamento=agendamento)

@auth.requires_login()
def update():
    """
    Update an existing agendamento
    """
    agendamento_id = request.args(0, cast=int)
    agendamento = db.agendamentos(agendamento_id) or redirect(URL('index'))
    form = SQLFORM(db.agendamentos, agendamento, showid=False).process()
    if form.accepted:
        response.flash = 'Agendamento atualizado com sucesso!'
        redirect(URL('index'))
    elif form.errors:
        response.flash = 'Erro no formulário!'
    return dict(form=form)

@auth.requires_login()
def delete():
    """
    Delete an agendamento
    """
    agendamento_id = request.args(0, cast=int)
    db(db.agendamentos.id == agendamento_id).delete()
    response.flash = 'Agendamento excluído com sucesso!'
    redirect(URL('index'))

@auth.requires_login()
def api_get_agendamentos():
    """
    API para retornar agendamentos filtrados por data de início e fim.
    O FullCalendar envia os parâmetros 'start' e 'end' com o formato ISO 8601.
    """
    try:
        start = request.vars.start
        end = request.vars.end
        
        if not start or not end:
            raise ValueError("Datas 'start' e 'end' são obrigatórias")

        from datetime import datetime
        
        start_date = datetime.fromisoformat(start[:-6])  
        end_date = datetime.fromisoformat(end[:-6])

        agendamentos = db((db.agendamentos.horario_inicio >= start_date) &
                          (db.agendamentos.horario_fim <= end_date)).select()

        events = []
        for agendamento in agendamentos:
            events.append({
                'id': agendamento.id,
                'title': agendamento.titulo,
                'start': agendamento.horario_inicio.isoformat(),
                'end': agendamento.horario_fim.isoformat(),
                'extendedProps': {
                    'cliente_id': agendamento.cliente_id,
                    'descricao': agendamento.descricao
                }
            })


        return response.json(events)

    except Exception as e:
        return response.json({'status': 'error', 'message': str(e)})



@auth.requires_login()
def api_criar_agendamento():
    """
    API para criar um novo agendamento.
    Recebe dados em formato JSON via POST e salva no banco de dados.
    """
    if request.env.request_method == 'POST':
        try:
            dados = request.post_vars

            novo_agendamento_id = db.agendamentos.insert(
                titulo=dados.titulo,
                cliente_id=dados.cliente_id,
                descricao=dados.descricao,
                horario_inicio=dados.horario_inicio,
                horario_fim=dados.horario_fim,
                recorrente=dados.recorrente,
                recorrencia_dias=dados.recorrencia_dias
            )
            db.commit()

            return response.json({'status': 'success', 'agendamento_id': novo_agendamento_id})

        except Exception as e:
            return response.json({'status': 'error', 'message': str(e)})
    else:
        return response.json({'status': 'error', 'message': 'Método inválido. Use POST.'})



@auth.requires_login()
def api_update_agendamento():
    """
    API para atualizar um agendamento existente.
    Atualiza apenas os campos que foram enviados na requisição.
    """
    if request.env.request_method == 'POST':
        try:
            dados = request.post_vars

            agendamento = db.agendamentos(dados.id)
            if not agendamento:
                return response.json({'status': 'error', 'message': 'Agendamento não encontrado'})

            agendamento.update_record(
                horario_inicio=dados.get('horario_inicio', agendamento.horario_inicio),
                horario_fim=dados.get('horario_fim', agendamento.horario_fim),
                titulo=dados.get('titulo', agendamento.titulo),  
                cliente_id=dados.get('cliente_id', agendamento.cliente_id),
                descricao=dados.get('descricao', agendamento.descricao),
                recorrente=dados.get('recorrente', agendamento.recorrente),
                recorrencia_dias=dados.get('recorrencia_dias', agendamento.recorrencia_dias)
            )
            db.commit()

            return response.json({'status': 'success'})
        except Exception as e:
            return response.json({'status': 'error', 'message': str(e)})
    else:
        return response.json({'status': 'error', 'message': 'Método inválido. Use POST.'})

