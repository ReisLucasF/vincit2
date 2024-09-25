@auth.requires_login()
def index():
    # Aqui ele consulta os usuários existesntes para retornar na view
    usuarios = db(db.usuario).select()
    return dict(usuarios=usuarios)

@auth.requires_login()
def criar():
    if request.post_vars:
        # Usa o insert para inserir na tabela do db.py
        db.usuario.insert(
            first_name=request.post_vars.first_name,
            last_name=request.post_vars.last_name,
            email=request.post_vars.email,
            password=db.usuario.password.validate(request.post_vars.password)[0], 
            cargo=request.post_vars.cargo
        )
        redirect(URL('index'))  # Redireciona para a view de usuários após a criação
    
    # Aqui busca os setores existentes para retornar na view
    setores = db(db.setor).select()
    return dict(setores=setores)


@auth.requires_login()
def editar():
    usuario_id = request.args(0) or redirect(URL('index'))
    usuario = db.usuario(usuario_id) or redirect(URL('index'))

    if request.post_vars:
        # Aqui é bem similar a anterior, a diferença é que ele usa o update para atualizar
        usuario.update_record(
            first_name=request.post_vars.first_name,
            last_name=request.post_vars.last_name,
            email=request.post_vars.email,
            cargo=request.post_vars.cargo
        )
        redirect(URL('index'))  

    setores = db(db.setor).select()
    return dict(usuario=usuario, setores=setores)


@auth.requires_login()
# talvez seja interessante vermos a viabilidade de excluir um usuário ou apenas desativar
def deletar():
    usuario_id = request.args(0) or redirect(URL('index'))
    db(db.usuario.id == usuario_id).delete()
    session.flash = 'Usuário deletado com sucesso!'
    redirect(URL('index'))
