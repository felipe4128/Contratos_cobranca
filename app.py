# app.py

# Requisitos:
# pip install flask flask_sqlalchemy pandas openpyxl

import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configuração do SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'credito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Injeção das cores do Sicoob nos templates
@app.context_processor
def inject_colors():
    return dict(
        cor_primaria="#00AE9D",
        cor_escura="#003641",
        cor_secundaria="#C9D200"
    )

db = SQLAlchemy(app)

# Modelo Contrato
class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_contrato = db.Column(db.Date)
    cliente = db.Column(db.String(100))
    numero = db.Column(db.String(50))
    tipo_contrato = db.Column(db.String(50))
    garantia = db.Column(db.String(100))
    valor = db.Column(db.Float)
    baixa_acima_48_meses = db.Column(db.Boolean, default=False)
    valor_abatido = db.Column(db.Float)
    ganho = db.Column(db.Float)
    custas = db.Column(db.Float)
    custas_deduzidas = db.Column(db.Float)
    protesto = db.Column(db.Boolean, default=False)
    protesto_deduzido = db.Column(db.Float)
    honorario = db.Column(db.Float)
    honorario_repassado = db.Column(db.Float)
    alvara = db.Column(db.Float)
    alvara_recebido = db.Column(db.Float)
    valor_entrada = db.Column(db.Float)
    vencimento_entrada = db.Column(db.Date)
    parcelas = db.Column(db.Integer)
    parcelas_restantes = db.Column(db.Integer)
    vencimento_parcelas = db.Column(db.Date)
    qtd_boletos_emitidos = db.Column(db.Integer)
    valor_pago_com_boleto = db.Column(db.Float)
    data_pagamento_boleto = db.Column(db.Date)
    data_baixa = db.Column(db.Date)
    obs_contabilidade = db.Column(db.Text)
    obs_contas_receber = db.Column(db.Text)
    valor_repassado_escritorio = db.Column(db.Float)

# Cria as tabelas antes de cada request
@app.before_request
def criar_tabelas():
    db.create_all()

# Rota principal: lista de contratos
@app.route('/')
def index():
    contratos = Contrato.query.all()
    return render_template('index.html', contratos=contratos)

# Rota de criação de novo contrato
@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        try:
            # Data do contrato
            data_contrato_str = request.form.get('data_contrato')
            data_contrato = datetime.strptime(data_contrato_str, '%Y-%m-%d') if data_contrato_str else None

            # Vencimento entrada e parcelas
            venc_entrada_str = request.form.get('vencimento_entrada')
            vencimento_entrada = datetime.strptime(venc_entrada_str, '%Y-%m-%d') if venc_entrada_str else data_contrato

            parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else None
            venc_parc_str = request.form.get('vencimento_parcelas')
            vencimento_parcelas = (
                datetime.strptime(venc_parc_str, '%Y-%m-%d') if venc_parc_str
                else (data_contrato + timedelta(days=30) if data_contrato else None)
            )

            c = Contrato(
                data_contrato=data_contrato,
                cliente=request.form.get('cliente') or None,
                numero=request.form.get('numero') or None,
                tipo_contrato=request.form.get('tipo_contrato') or None,
                garantia=request.form.get('garantia') or None,
                valor=float(request.form.get('valor')) if request.form.get('valor') else None,
                baixa_acima_48_meses=bool(request.form.get('baixa_acima_48_meses')),
                valor_abatido=float(request.form.get('valor_abatido')) if request.form.get('valor_abatido') else None,
                ganho=float(request.form.get('ganho')) if request.form.get('ganho') else None,
                custas=float(request.form.get('custas')) if request.form.get('custas') else None,
                custas_deduzidas=float(request.form.get('custas_deduzidas')) if request.form.get('custas_deduzidas') else None,
                protesto=bool(request.form.get('protesto')),
                protesto_deduzido=float(request.form.get('protesto_deduzido')) if request.form.get('protesto_deduzido') else None,
                honorario=float(request.form.get('honorario')) if request.form.get('honorario') else None,
                honorario_repassado=float(request.form.get('honorario_repassado')) if request.form.get('honorario_repassado') else None,
                alvara=float(request.form.get('alvara')) if request.form.get('alvara') else None,
                alvara_recebido=float(request.form.get('alvara_recebido')) if request.form.get('alvara_recebido') else None,
                valor_entrada=float(request.form.get('valor_entrada')) if request.form.get('valor_entrada') else None,
                vencimento_entrada=vencimento_entrada,
                parcelas=parcelas,
                parcelas_restantes=parcelas,
                vencimento_parcelas=vencimento_parcelas,
                qtd_boletos_emitidos=int(request.form.get('qtd_boletos_emitidos')) if request.form.get('qtd_boletos_emitidos') else None,
                valor_pago_com_boleto=float(request.form.get('valor_pago_com_boleto')) if request.form.get('valor_pago_com_boleto') else None,
                data_pagamento_boleto=datetime.strptime(request.form.get('data_pagamento_boleto'), '%Y-%m-%d') if request.form.get('data_pagamento_boleto') else None,
                data_baixa=datetime.strptime(request.form.get('data_baixa'), '%Y-%m-%d') if request.form.get('data_baixa') else None,
                obs_contabilidade=request.form.get('obs_contabilidade') or None,
                obs_contas_receber=request.form.get('obs_contas_receber') or None,
                valor_repassado_escritorio=float(request.form.get('valor_repassado_escritorio')) if request.form.get('valor_repassado_escritorio') else None
            )

            db.session.add(c)
            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return f"Erro ao salvar contrato: {e}", 400

    return render_template('novo.html')

# Rota de visualização e edição de um contrato
@app.route('/contrato/<int:id>', methods=['GET', 'POST'])
def ver_contrato(id):
    contrato = Contrato.query.get_or_404(id)

    if request.method == 'POST':
        for field in request.form:
            if hasattr(Contrato, field):
                val = request.form.get(field)
                if val == '':
                    setattr(contrato, field, None)
                elif field in ['valor', 'valor_abatido', 'ganho', 'custas', 'custas_deduzidas',
                               'protesto_deduzido', 'honorario', 'honorario_repassado',
                               'alvara', 'alvara_recebido', 'valor_entrada', 'valor_pago_com_boleto',
                               'valor_repassado_escritorio']:
                    setattr(contrato, field, float(val))
                elif field in ['parcelas', 'parcelas_restantes', 'qtd_boletos_emitidos']:
                    setattr(contrato, field, int(val))
                elif field in ['data_contrato', 'vencimento_entrada', 'vencimento_parcelas',
                               'data_pagamento_boleto', 'data_baixa']:
                    setattr(contrato, field, datetime.strptime(val, '%Y-%m-%d'))
                else:
                    setattr(contrato, field, val)
        db.session.commit()
        return redirect(url_for('ver_contrato', id=id))

    return render_template('contrato.html', contrato=contrato)

# Rota para excluir contratos em lote
@app.route('/deletar', methods=['POST'])
def deletar():
    ids = request.form.getlist('ids')
    for id_str in ids:
        c = Contrato.query.get(int(id_str))
        if c:
            db.session.delete(c)
    db.session.commit()
    return redirect(url_for('index'))

# Rota de exportação para Excel
@app.route('/exportar')
def exportar():
    contratos = Contrato.query.all()
    dados = [c.__dict__ for c in contratos]
    for d in dados:
        d.pop('_sa_instance_state', None)
    df = pd.DataFrame(dados)
    caminho = os.path.join(base_dir, 'contratos_exportados.xlsx')
    df.to_excel(caminho, index=False)
    return send_file(caminho, as_attachment=True)

# Ajuste de porta para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
