from datetime import date, datetime, timedelta
import os
import requests
import re
import pandas as pd
import io
import sqlite3
import unicodedata
import traceback
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, or_

app = Flask(__name__)

# --- INÍCIO DO FILTRO DE DATAS ---
@app.template_filter('formatardata')
def formatardata(valor):
    if not valor or str(valor).lower() == 'none':
        return '-' 
    try:
        segundos = int(valor) / 1000.0
        return datetime.fromtimestamp(segundos).strftime('%d/%m/%Y')
    except Exception:
        return str(valor)
# --- FIM DO FILTRO ---

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sistema.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS
# ==========================================

class TerritorioSP(db.Model):
    __tablename__ = 'territorios_sp'
    id = db.Column(db.Integer, primary_key=True)
    bairro = db.Column(db.String(150))
    distrito = db.Column(db.String(150))
    subprefeitura = db.Column(db.String(150))
    conselho = db.Column(db.String(150))

class Entidade(db.Model):
    __tablename__ = 'entidades'
    
    registro = db.Column('registro', db.String(50), primary_key=True)
    cnpj = db.Column('cnpj', db.String(50))
    nome_ong = db.Column('nome_ong', db.String(255))
    sigla = db.Column('sigla', db.String(100))
    presidencia = db.Column('presidencia', db.String(150))
    email = db.Column('email', db.String(150))
    cep = db.Column('cep', db.String(20))
    numero = db.Column('numero', db.String(20)) 
    complemento = db.Column('complemento', db.String(150))
    telefone1 = db.Column('telefone1', db.String(20))
    telefone2 = db.Column('telefone2', db.String(20))
    cel = db.Column('cel', db.String(20)) 
    site = db.Column('site', db.String(150))
    processo_sei = db.Column('processo_sei', db.String(100)) 
    proc_atualizacao = db.Column('proc_atualizacao', db.String(100))
    tipo_de_atendimento = db.Column('tipo_de_atendimento', db.String(100))
    documento_sede = db.Column('documento_sede', db.String(100))

class Registro(db.Model):
    __tablename__ = 'registros'

    id = db.Column(db.Integer, primary_key=True)
    controle = db.Column('controle', db.String(50))
    registro_reg = db.Column('registro_reg', db.String(50))
    situacao = db.Column('situacao', db.String(50))
    data_ro = db.Column('data_ro', db.String(20))
    vencimento = db.Column('vencimento', db.String(20))
    processo_fisico = db.Column('processo_fisico', db.String(100))
    solicitacao = db.Column('solicitacao', db.String(100))
    resolucao = db.Column('resolucao', db.String(100))
    validade = db.Column('validade', db.String(50))
    observacoes = db.Column('observacoes', db.Text) 
    data_do = db.Column('data_do', db.String(50))
    pag_doc = db.Column('pag_doc', db.String(50))
    cpr = db.Column('cpr', db.String(50))
    protocolo = db.Column('protocolo', db.String(100))
    campo1 = db.Column('campo1', db.String(255))
    campo2 = db.Column('campo2', db.String(255))
    campo3 = db.Column('campo3', db.String(255))

class Servico(db.Model):
    __tablename__ = 'servicos'

    rowid = db.Column('rowid', db.Integer, primary_key=True)
    
    controle_se = db.Column('controle_se', db.String(50))
    id_programa = db.Column('id_programa', db.String(50))
    registro_se = db.Column('registro_se', db.String(50))
    tipo_se = db.Column('tipo_se', db.String(100))
    cnpj_prog = db.Column('cnpj_prog', db.String(50))
    regime_atendimento = db.Column('regime_atendimento', db.String(100))
    servico_programa = db.Column('servico_programa', db.String(255))
    situacao_se = db.Column('situacao_se', db.String(50))
    resolucao_se = db.Column('resolucao_se', db.String(255))
    numero_atendidos = db.Column('numero_atendidos', db.String(50))
    faixa_etaria = db.Column('faixa_etaria', db.String(100))
    atendidos = db.Column('atendidos', db.String(100))
    numero_se = db.Column('numero_se', db.String(50))
    complemento_se = db.Column('complemento_se', db.String(150))
    cep_se = db.Column('cep_se', db.String(20))
    termo_convenio = db.Column('termo_convenio', db.String(100))
    licenca_pmsp = db.Column('licenca_pmsp', db.String(100))
    laudo_hab = db.Column('laudo_hab', db.String(100))
    avcb = db.Column('avcb', db.String(100))
    laudo_seg = db.Column('laudo_seg', db.String(100))
    situacao2 = db.Column('situacao2', db.String(50))
    telefone_se = db.Column('telefone_se', db.String(20))
    celular_se = db.Column('celular_se', db.String(20))
    n_curso_aprendiz = db.Column('n_curso_aprendiz', db.String(100))
    processo_sei_prog = db.Column('processo_sei_prog', db.String(100))
    data_do_se = db.Column('data_do_se', db.String(50))
    vencimento_prog_se = db.Column('vencimento_prog_se', db.String(50))
    protocolo_se = db.Column('protocolo_se', db.String(100))
    cpr_se = db.Column('cpr_se', db.String(50))
    data_ro_se = db.Column('data_ro_se', db.String(50))
    pag_do_se = db.Column('pag_do_se', db.String(50))
    proc_prog_atualizacao = db.Column('proc_prog_atualizacao', db.String(100))

with app.app_context():
    db.create_all()

# ==========================================
# ROTAS
# ==========================================
@app.route('/')
def index():
    return redirect(url_for('listar_entidades'))

@app.route('/entidades')
def listar_entidades():
    termo_busca = request.args.get('busca')
    pagina_atual = request.args.get('page', 1, type=int)
    
    if termo_busca:
        termo = f"%{termo_busca}%"
        paginacao = Entidade.query.filter(
            db.or_(
                Entidade.registro.ilike(termo),
                Entidade.cnpj.ilike(termo),
                Entidade.sigla.ilike(termo),
                Entidade.nome_ong.ilike(termo),
                Entidade.sigla.ilike(termo),
                Entidade.cep.ilike(termo),
                Entidade.numero.ilike(termo),
                Entidade.complemento.ilike(termo),
                Entidade.telefone1.ilike(termo),
                Entidade.telefone2.ilike(termo),
                Entidade.cel.ilike(termo),
                Entidade.email.ilike(termo),
                Entidade.site.ilike(termo),
                Entidade.processo_sei.ilike(termo),
                Entidade.proc_atualizacao.ilike(termo),
                Entidade.tipo_de_atendimento.ilike(termo),
                Entidade.documento_sede.ilike(termo)
            )
        ).paginate(page=pagina_atual, per_page=20, error_out=False)
    else:
        paginacao = Entidade.query.order_by(text('rowid DESC')).paginate(page=pagina_atual, per_page=20, error_out=False)
        
    return render_template('entidades.html', entidades=paginacao, busca=termo_busca)



@app.route('/entidade/<path:id_registro>')
def detalhe_entidade(id_registro):
    ong = Entidade.query.get(id_registro)
    
    if not ong:
        return redirect(url_for('listar_entidades'))
        
    return render_template('detalhe_entidade.html', ong=ong)

@app.route('/entidade/<path:id_registro>/editar', methods=['GET', 'POST'])
def editar_entidade(id_registro):
    ong = Entidade.query.get(id_registro)
    
    if not ong:
        return redirect(url_for('listar_entidades'))
        
    if request.method == 'POST':
        # Dados Institucionais
        ong.cnpj = request.form.get('cnpj')
        ong.nome_ong = request.form.get('nome_ong')
        ong.sigla = request.form.get('sigla')
        
        # Endereço
        ong.cep = request.form.get('cep')
        ong.numero = request.form.get('numero')
        ong.complemento = request.form.get('complemento')
        
        # Contato e Liderança
        ong.presidencia = request.form.get('presidencia')
        ong.email = request.form.get('email')
        ong.telefone1 = request.form.get('telefone1')
        ong.telefone2 = request.form.get('telefone2')
        ong.cel = request.form.get('cel')
        ong.site = request.form.get('site')
        
        # Documentação e Processos
        ong.processo_sei = request.form.get('processo_sei')
        ong.proc_atualizacao = request.form.get('proc_atualizacao')
        ong.tipo_de_atendimento = request.form.get('tipo_de_atendimento')
        ong.documento_sede = request.form.get('documento_sede')
        
        db.session.commit()
        return redirect(f'/entidade/{ong.registro}')
        
    return render_template('editar_entidade.html', ong=ong)
        

@app.route('/registros')
def listar_registros():
    termo_busca = request.args.get('busca', '')
    filtro_status = request.args.get('status', '')
    pagina_atual = request.args.get('page', 1, type=int)
    
    query = Registro.query
    
    if termo_busca:
        termo = f"%{termo_busca}%"
        query = query.filter(
            db.or_(
                Registro.registro_reg.ilike(termo),
                Registro.solicitacao.ilike(termo),
                Registro.processo_fisico.ilike(termo),
                Registro.data_ro.ilike(termo),
                Registro.data_do.ilike(termo),
                Registro.vencimento.ilike(termo),
                Registro.resolucao.ilike(termo),
                Registro.validade.ilike(termo),
                Registro.cpr.ilike(termo)
            )
        )
        
    if filtro_status == 'A_VENCER':
        hoje = datetime.now().strftime('%Y-%m-%d')
        daqui_30_dias = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        query = query.filter(
            Registro.vencimento >= hoje,
            Registro.vencimento <= daqui_30_dias
        )
        
        query = query.order_by(Registro.vencimento.asc())
        
    elif filtro_status:
        query = query.filter(Registro.situacao.ilike(filtro_status))
        
    if filtro_status != 'A_VENCER':
        query = query.order_by(text('rowid DESC'))
        
    paginacao = query.paginate(page=pagina_atual, per_page=20, error_out=False)
    
    return render_template('registros.html', registros=paginacao, busca=termo_busca, status=filtro_status)

@app.route('/servicos')
def listar_servicos():
    termo_busca = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if termo_busca:
        busca_formatada = f"%{termo_busca}%"
        servicos = Servico.query.filter(
            or_(
                Servico.registro_se.ilike(busca_formatada),
                Servico.servico_programa.ilike(busca_formatada),
                Servico.cnpj_prog.ilike(busca_formatada),
                Servico.processo_sei_prog.ilike(busca_formatada),
                Servico.resolucao_se.ilike(busca_formatada),
                Servico.situacao_se.ilike(busca_formatada)
            )
        ).order_by(Servico.rowid.desc()).paginate(page=page, per_page=20)
    else:
        servicos = Servico.query.order_by(Servico.rowid.desc()).paginate(page=page, per_page=20)
        
    return render_template('servicos.html', servicos=servicos, termo_busca=termo_busca)


@app.route('/entidade/<path:id_registro>/excluir')
def excluir_entidade(id_registro):
    ong = Entidade.query.get(id_registro)
    
    if ong:
        try:
            db.session.delete(ong)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir entidade: {e}")
            return f"Erro interno ao tentar excluir: {e}", 500
        
    return redirect(url_for('listar_entidades'))

@app.route('/registro/<int:id>/excluir')
def excluir_registro(id):
    reg = Registro.query.get(id)
    
    if reg:
        try:
            db.session.delete(reg)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir registro: {e}")
            return f"Erro interno ao tentar excluir o registro: {e}", 500
            
    return redirect('/registros')

@app.route('/registro/novo', methods=['GET', 'POST'])
def novo_registro_geral():
    if request.method == 'POST':
        registro_digitado = request.form.get('registro_reg')
        
        entidade_valida = Entidade.query.filter_by(registro=registro_digitado).first()
        
        if not entidade_valida:
            entidades = Entidade.query.all()
            return render_template('novo_registro.html', entidades=entidades, erro="Erro: O número de registro digitado não pertence a nenhuma entidade cadastrada!")

        registro_existente = Registro.query.filter_by(registro_reg=registro_digitado).first()
        
        if registro_existente:
            entidades = Entidade.query.all()
            return render_template('novo_registro.html', entidades=entidades, erro=f"Erro: Já existe um Registro cadastrado para a entidade {registro_digitado}!")
            
        todos_registros = Registro.query.all()
        maior_controle = 0
        
        for reg in todos_registros:
            if reg and reg.controle: 
                try:
                    num = int(reg.controle)
                    if num > maior_controle:
                        maior_controle = num
                except (ValueError, TypeError):
                    continue
                    
        novo_numero_controle = str(maior_controle + 1)
        
        maior_id = db.session.query(db.func.max(Registro.id)).scalar()
        novo_id = (maior_id or 0) + 1

        novo_reg = Registro(
            id=novo_id,
            controle=novo_numero_controle, 
            registro_reg=registro_digitado,
            processo_fisico=request.form.get('processo_fisico'),
            solicitacao=request.form.get('solicitacao'),
            data_ro=request.form.get('data_ro'),
            vencimento=request.form.get('vencimento'),
            resolucao=request.form.get('resolucao'),
            validade=request.form.get('validade'),
            observacoes=request.form.get('observacoes'),
            data_do=request.form.get('data_do'),
            pag_doc=request.form.get('pag_doc'),
            cpr=request.form.get('cpr'),
            protocolo=request.form.get('protocolo'),
            situacao="AGUARDANDO RO" 
        )
        
        db.session.add(novo_reg)
        db.session.commit()
        return redirect('/registros')
        
    entidades = Entidade.query.all()
    return render_template('novo_registro.html', entidades=entidades)

@app.route('/registro/<int:id>')
def detalhe_registro(id):
    reg = Registro.query.get(id)
    
    if not reg:
        return redirect('/registros')
        
    ong = Entidade.query.filter_by(registro=reg.registro_reg).first()
    
    return render_template('detalhe_registro.html', reg=reg, ong=ong)


@app.route('/registro/<int:id>/editar', methods=['GET', 'POST'])
def editar_registro(id):
    reg = Registro.query.get(id)
    
    if not reg:
        return redirect('/registros')
        
    if request.method == 'POST':
        reg.solicitacao = request.form.get('solicitacao')
        reg.processo_fisico = request.form.get('processo_fisico')
        reg.resolucao = request.form.get('resolucao')
        reg.situacao = request.form.get('situacao')
        
        reg.data_ro = request.form.get('data_ro')
        reg.vencimento = request.form.get('vencimento')
        reg.validade = request.form.get('validade')
        
        reg.data_do = request.form.get('data_do')
        reg.pag_doc = request.form.get('pag_doc')
        reg.cpr = request.form.get('cpr')
        reg.protocolo = request.form.get('protocolo')
        reg.observacoes = request.form.get('observacoes')
        
        texto_obs = request.form.get('observacoes', '').replace('[STATUS_TRAVADO]', '').strip()
        
        if request.form.get('travar_status') == 'sim':
            reg.observacoes = f"{texto_obs}\n[STATUS_TRAVADO]".strip()
        else:
            reg.observacoes = texto_obs
        
        db.session.commit()
        
        return redirect(f'/registro/{reg.id}')
        
    return render_template('editar_registro.html', reg=reg)

def converter_para_data(valor_data):
    if not valor_data or str(valor_data).lower() == 'none':
        return None

    valor_str = str(valor_data).strip()

    if '-' in valor_str and len(valor_str) == 10:
        try:
            return datetime.strptime(valor_str, '%Y-%m-%d').date()
        except Exception:
            return None

    try:
        segundos = int(valor_str) / 1000.0
        return date.fromtimestamp(segundos)
    except Exception:
        return None

@app.template_filter('data_input')
def data_input(valor):
    """Filtro exclusivo para preencher formulários HTML (AAAA-MM-DD)"""
    if not valor or str(valor).lower() == 'none':
        return ''
    
    valor_str = str(valor).strip()
    
    if '-' in valor_str and len(valor_str) == 10:
        return valor_str
        
    try:
        segundos = int(valor_str) / 1000.0
        return datetime.fromtimestamp(segundos).strftime('%Y-%m-%d')
    except Exception:
        return ''

def gerar_novo_registro():
    entidades = Entidade.query.all()
    maior_numero = 0
    
    for ong in entidades:
        if ong.registro and '/' in ong.registro:
            try:
                numero_str = ong.registro.split('/')[0]
                numero = int(numero_str)
                
                if numero > maior_numero:
                    maior_numero = numero
            except ValueError:
                continue
                
    novo_numero = maior_numero + 1
    ano_atual = datetime.now().strftime('%y')
    novo_registro_formatado = f"{str(novo_numero).zfill(4)}/{ano_atual}"
    
    return novo_registro_formatado

def atualizar_status_temporal_registros():
    hoje = date.today()
    todos_registros = Registro.query.all()
    
    for reg in todos_registros:
        d_ro = converter_para_data(reg.data_ro)
        d_ven = converter_para_data(reg.vencimento)
        d_do = converter_para_data(reg.data_do) 
        
        if d_ro and str(reg.data_ro).isdigit():
            reg.data_ro = d_ro.strftime('%Y-%m-%d')
            
        if d_ven and str(reg.vencimento).isdigit():
            reg.vencimento = d_ven.strftime('%Y-%m-%d')
            
        if d_do and str(reg.data_do).isdigit():
            reg.data_do = d_do.strftime('%Y-%m-%d')

        if reg.observacoes and "[STATUS_TRAVADO]" in reg.observacoes:
            continue
            
        if d_ro and d_ven:
            if hoje < d_ro:
                reg.situacao = "AGUARDANDO RO"
            elif d_ro <= hoje <= d_ven:
                reg.situacao = "ATIVO"
            elif hoje > d_ven:
                reg.situacao = "VENCIDO"
                
    db.session.commit()

@app.before_request
def rodar_automacoes_background():
    try:
        atualizar_status_temporal_registros()
    except Exception as e:
        print(f"Erro na automação de status: {e}")

@app.route('/nova_entidade', methods=['GET', 'POST'])
def nova_entidade():
    if request.method == 'POST':
        novo_registro = gerar_novo_registro()
        
        nova_ong = Entidade(
            registro=novo_registro,
            cnpj=request.form.get('cnpj'),
            nome_ong=request.form.get('nome_ong'),
            sigla=request.form.get('sigla'),
            cep=request.form.get('cep'),
            numero=request.form.get('numero'),
            complemento=request.form.get('complemento'),
            presidencia=request.form.get('presidencia'),
            email=request.form.get('email'),
            telefone1=request.form.get('telefone1'),
            telefone2=request.form.get('telefone2'),
            cel=request.form.get('cel'),
            site=request.form.get('site'),
            processo_sei=request.form.get('processo_sei'),
            proc_atualizacao=request.form.get('proc_atualizacao'),
            tipo_de_atendimento=request.form.get('tipo_de_atendimento'),
            documento_sede=request.form.get('documento_sede')
        )
        
        db.session.add(nova_ong)
        db.session.commit()
        
        return redirect(f'/entidade/{novo_registro}')
    
    sugestao_registro = gerar_novo_registro()
    return render_template('nova_entidade.html', registro_gerado=sugestao_registro)

@app.route('/programa/novo', methods=['GET', 'POST'])
def novo_programa():
    if request.method == 'POST':
        registro_digitado = request.form.get('registro_se')
        
        entidade_valida = Entidade.query.filter_by(registro=registro_digitado).first()
        
        if not entidade_valida and registro_digitado:
            entidades = Entidade.query.order_by(text('rowid DESC')).all()
            return render_template('novo_programa.html', entidades=entidades, erro="Erro: O número de registro digitado não pertence a nenhuma entidade cadastrada!")
            
        novo_prog = Servico(
            registro_se=registro_digitado,
            id_programa=request.form.get('id_programa'),
            controle_se=request.form.get('controle_se', ''),
            cnpj_prog=request.form.get('cnpj_prog'),
            servico_programa=request.form.get('servico_programa'),
            tipo_se=request.form.get('tipo_se'),
            regime_atendimento=request.form.get('regime_atendimento'),
            faixa_etaria=request.form.get('faixa_etaria'),
            atendidos=request.form.get('atendidos'),
            numero_atendidos=request.form.get('numero_atendidos'),
            cep_se=request.form.get('cep_se'),
            numero_se=request.form.get('numero_se'),
            complemento_se=request.form.get('complemento_se'),
            telefone_se=request.form.get('telefone_se'),
            celular_se=request.form.get('celular_se'),
            avcb=request.form.get('avcb'),
            laudo_hab=request.form.get('laudo_hab'),
            laudo_seg=request.form.get('laudo_seg'),
            licenca_pmsp=request.form.get('licenca_pmsp'),
            termo_convenio=request.form.get('termo_convenio'),
            situacao2=request.form.get('situacao2'),
            processo_sei_prog=request.form.get('processo_sei_prog'),
            proc_prog_atualizacao=request.form.get('proc_prog_atualizacao'),
            n_curso_aprendiz=request.form.get('n_curso_aprendiz'),
            resolucao_se=request.form.get('resolucao_se'),
            data_ro_se=request.form.get('data_ro_se'),
            vencimento_prog_se=request.form.get('vencimento_prog_se'),
            data_do_se=request.form.get('data_do_se'),
            pag_do_se=request.form.get('pag_do_se'),
            protocolo_se=request.form.get('protocolo_se'),
            cpr_se=request.form.get('cpr_se'),
            situacao_se=request.form.get('situacao_se', 'ATIVO')
        )
        
        db.session.add(novo_prog)
        db.session.commit()
        return redirect('/servicos')
        
    entidades = Entidade.query.order_by(text('rowid DESC')).all()
    return render_template('novo_programa.html', entidades=entidades)

@app.route('/programa/<int:id_linha>/editar', methods=['GET', 'POST'])
def editar_programa(id_linha):
    prog = Servico.query.get(id_linha)
    
    if not prog:
        return redirect('/servicos')
        
    if request.method == 'POST':
        prog.registro_se = request.form.get('registro_se')
        prog.controle_se = request.form.get('controle_se', '')
        prog.id_programa = request.form.get('id_programa')
        prog.cnpj_prog = request.form.get('cnpj_prog')
        prog.servico_programa = request.form.get('servico_programa')
        prog.tipo_se = request.form.get('tipo_se')
        prog.regime_atendimento = request.form.get('regime_atendimento')
        prog.faixa_etaria = request.form.get('faixa_etaria')
        prog.atendidos = request.form.get('atendidos')
        prog.numero_atendidos = request.form.get('numero_atendidos')
        prog.cep_se = request.form.get('cep_se')
        prog.numero_se = request.form.get('numero_se')
        prog.complemento_se = request.form.get('complemento_se')
        prog.telefone_se = request.form.get('telefone_se')
        prog.celular_se = request.form.get('celular_se')
        prog.avcb = request.form.get('avcb')
        prog.laudo_hab = request.form.get('laudo_hab')
        prog.laudo_seg = request.form.get('laudo_seg')
        prog.licenca_pmsp = request.form.get('licenca_pmsp')
        prog.termo_convenio = request.form.get('termo_convenio')
        prog.situacao2 = request.form.get('situacao2')
        prog.processo_sei_prog = request.form.get('processo_sei_prog')
        prog.proc_prog_atualizacao = request.form.get('proc_prog_atualizacao')
        prog.n_curso_aprendiz = request.form.get('n_curso_aprendiz')
        prog.resolucao_se = request.form.get('resolucao_se')
        prog.pag_do_se = request.form.get('pag_do_se')
        prog.protocolo_se = request.form.get('protocolo_se')
        prog.cpr_se = request.form.get('cpr_se')
        prog.situacao_se = request.form.get('situacao_se')
        prog.data_ro_se = request.form.get('data_ro_se')
        prog.vencimento_prog_se = request.form.get('vencimento_prog_se')
        prog.data_do_se = request.form.get('data_do_se')
        
        db.session.commit()
        
        return redirect(f'/servicos/{id_linha}')
        
    ong = Entidade.query.filter_by(registro=prog.registro_se).first()
    entidades = Entidade.query.order_by(text('rowid DESC')).all()
    
    return render_template('editar_programa.html', prog=prog, ong=ong, entidades=entidades)

@app.route('/servicos/<int:id_linha>')
def detalhe_programa(id_linha):
    
    prog = Servico.query.get(id_linha) 
    
    if not prog:
        return redirect('/servicos') 
        
    ong = Entidade.query.filter_by(registro=prog.registro_se).first()
    
    return render_template('detalhe_programa.html', prog=prog, ong=ong)

@app.route('/programa/<int:id_linha>/excluir')
def excluir_programa(id_linha):
    prog = Servico.query.get(id_linha)
    
    if prog:
        try:
            db.session.delete(prog)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir programa: {e}")
            return f"Erro interno ao tentar excluir o programa: {e}", 500
            
    return redirect('/servicos')

@app.route('/entidade/<path:registro>/certificado')
def gerar_certificado(registro):
    ong = Entidade.query.filter_by(registro=registro).first()
    
    if not ong:
        return redirect('/entidades')
        
    dados_registro = Registro.query.filter_by(registro_reg=registro).order_by(text('rowid DESC')).first()
        
    rua = "Endereço não informado"
    bairro = ""
    distrito = ""
    subprefeitura = ""
    conselho = ""
    
    if ong.cep:
        cep_limpo = ''.join(filter(str.isdigit, str(ong.cep)))
        if len(cep_limpo) == 8:
            try:
                resposta = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
                dados = resposta.json()
                if 'erro' not in dados:
                    rua = dados.get('logradouro', '')
                    bairro_original = dados.get('bairro', '')
                    bairro = bairro_original
                    
                    import unicodedata
                    
                    def normalizar(texto):
                        if not texto: return ""
                        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()
                        texto = texto.replace('jd.', 'jardim').replace('vl.', 'vila').replace('pq.', 'parque')
                        return texto.strip()
                        
                    if bairro_original:
                        bairro_busca = normalizar(bairro_original)
                        
                        todos_territorios = TerritorioSP.query.all()
                        
                        for t in todos_territorios:
                            bairro_banco = normalizar(t.bairro)
                            
                            if bairro_banco in bairro_busca or bairro_busca in bairro_banco:
                                distrito = t.distrito
                                subprefeitura = t.subprefeitura
                                conselho = t.conselho
                                break 
                                
            except Exception as e:
                print(f"Erro ao buscar CEP: {e}")
                rua = "Erro ao buscar endereço"

    return render_template('certificado.html', 
                           ong=ong, 
                           rua=rua, 
                           bairro=bairro, 
                           reg=dados_registro,
                           distrito=distrito,
                           subprefeitura=subprefeitura,
                           conselho=conselho)

def normalizar_bairro(texto):
    if not texto: 
        return ""
        
    texto = str(texto)
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()
    texto = re.sub(r'\s*\((zl|zs|zn|zo|zc|zona leste|zona sul|zona norte|zona oeste|centro)\)\s*', '', texto)
    texto = texto.replace('jd.', 'jardim ').replace('vl.', 'vila ').replace('pq.', 'parque ')
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

@app.route('/servico/<int:rowid>/certificado')
def gerar_certificado_servico(rowid):
    servico = Servico.query.get(rowid)
    if not servico:
        return redirect('/servicos')
        
    ong = Entidade.query.filter_by(registro=servico.registro_se).first()
    
    reg = Registro.query.filter_by(registro_reg=servico.registro_se).order_by(text('rowid DESC')).first()

    rua = "Endereço não informado"
    bairro = ""
    distrito = ""
    subprefeitura = ""
    conselho = ""

    if servico.cep_se:
        cep_limpo = ''.join(filter(str.isdigit, str(servico.cep_se)))
        if len(cep_limpo) == 8:
            try:
                resposta = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
                dados = resposta.json()
                if 'erro' not in dados:
                    rua = dados.get('logradouro', '')
                    bairro_original = dados.get('bairro', '')
                    bairro = bairro_original
                    
                    if bairro_original:
                        bairro_busca = normalizar_bairro(bairro_original)
                        
                        if bairro_busca:
                            todos_territorios = TerritorioSP.query.all()
                            
                            for t in todos_territorios:
                                bairro_banco = normalizar_bairro(t.bairro)
                                
                                if bairro_banco and (bairro_banco == bairro_busca or bairro_busca in bairro_banco):
                                    distrito = t.distrito
                                    subprefeitura = t.subprefeitura
                                    conselho = t.conselho
                                    break 
                                
            except Exception as e:
                print(f"Erro ao buscar CEP: {e}")
                rua = "Erro ao buscar endereço"

    return render_template('certificado_servico.html', 
                           servico=servico,
                           ong=ong, 
                           reg=reg,
                           rua=rua, 
                           bairro=bairro, 
                           distrito=distrito,
                           subprefeitura=subprefeitura,
                           conselho=conselho)

@app.template_filter('limpar_numero')
def limpar_numero(valor):
    if not valor:
        return 'S/N'
        
    texto = str(valor)
    
    if texto.endswith('.0'):
        return texto[:-2]
        
    return texto

@app.template_filter('formatar_sei')
def formatar_sei(valor):
    if not valor:
        return '-'
    
    numeros = re.sub(r'\D', '', str(valor))
    
    if len(numeros) == 16:
        return f"{numeros[:4]}.{numeros[4:8]}/{numeros[8:15]}-{numeros[15]}"
    
    return valor

@app.template_filter('formatar_cnpj')
def formatar_cnpj(valor):
    if not valor:
        return '-'
    numeros = re.sub(r'\D', '', str(valor))
    
    if len(numeros) == 14:
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    
    return valor

@app.route('/exportar-excel')
def exportar_excel():
    output = io.BytesIO()
    
    conexao = sqlite3.connect('C:/Users/x539532/Downloads/Banco_de_Dados_CPR/sistema.db') 
    
    df_entidades = pd.read_sql_query("SELECT * FROM entidades", conexao)
    df_registros = pd.read_sql_query("SELECT * FROM registros", conexao)
    df_servicos = pd.read_sql_query("SELECT * FROM servicos", conexao)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_entidades.to_excel(writer, sheet_name='Entidades (ONGs)', index=False)
        df_registros.to_excel(writer, sheet_name='Registros', index=False)
        df_servicos.to_excel(writer, sheet_name='Serviços', index=False)
        
    conexao.close()
    
    output.seek(0)
    
    return send_file(output, download_name='Extracao_Sistema_CPR.xlsx', as_attachment=True)

@app.route('/api/dados_registro')
def api_dados_registro():
    numero_registro = request.args.get('registro')
    
    if not numero_registro:
        return jsonify({'erro': 'Registro não informado'}), 400

    ong = Entidade.query.filter_by(registro=numero_registro).first()
    reg = Registro.query.filter_by(registro_reg=numero_registro).order_by(Registro.id.desc()).first()

    if not ong:
        return jsonify({'erro': 'Registro não encontrado'}), 404

    dados = {
        'cnpj': ong.cnpj if ong.cnpj else '',
        'processo_sei': ong.processo_sei if ong.processo_sei else '',
        'resolucao': reg.resolucao if reg and reg.resolucao else '',
        'vencimento': reg.vencimento if reg and reg.vencimento else '',
        'data_do': reg.data_do if reg and reg.data_do else '',
        'telefone': ong.telefone1 if ong.telefone1 else '',
        'data_ro': reg.data_ro if reg and reg.data_ro else '',
        'situacao': reg.situacao if reg and reg.situacao else '',
        'protocolo': reg.protocolo if reg and reg.protocolo else '',
        'cpr': reg.cpr if reg and reg.cpr else ''
    }
    
    return jsonify(dados)

@app.template_filter('data_br')
def formatar_data_br(valor):
    if not valor:
        return ""

    try:
        if isinstance(valor, str):
            data_obj = datetime.strptime(valor, '%Y-%m-%d')
            return data_obj.strftime('%d/%m/%Y')

        if hasattr(valor, 'strftime'):
            return valor.strftime('%d/%m/%Y')

    except ValueError:
        return valor

    return valor

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')