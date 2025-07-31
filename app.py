from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///credito.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=True)
    data_contrato = db.Column(db.Date, nullable=True)
    cliente = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(50), nullable=True)
    tipo_contrato = db.Column(db.String(50), nullable=True)
    cooperado = db.Column(db.String(100), nullable=True)
    garantia = db.Column(db.String(100), nullable=True)
    valor = db.Column(db.Float, nullable=True)
    valor_contrato_sistema = db.Column(db.Float, nullable=True)
    baixa_acima_48_meses = db.Column(db.Boolean, nullable=True, default=False)
    valor_abatido = db.Column(db.Float, nullable=True)
    ganho = db.Column(db.Float, nullable=True)
    custas = db.Column(db.Float, nullable=True)
    custas_deduzidas = db.Column(db.Float, nullable=True)
    protesto = db.Column(db.Float, nullable=True)
    protesto_deduzido = db.Column(db.Float, nullable=True)
    honorario = db.Column(db.Float, nullable=True)
    honorario_repassado = db.Column(db.Float, nullable=True)
    alvara = db.Column(db.Float, nullable=True)
    alvara_recebido = db.Column(db.Float, nullable=True)
    valor_entrada = db.Column(db.Float, nullable=True)
    vencimento_entrada = db.Column(db.Date, nullable=True)
    parcelas = db.Column(db.Integer, default=0)
    parcelas_restantes = db.Column(db.Integer, default=0)
    valor_das_parcelas = db.Column(db.Float, nullable=True)
    vencimento_parcelas = db.Column(db.Date, nullable=True)
    quantidade_boletos_emitidos = db.Column(db.Integer, nullable=True)
    valor_pg_com_boleto = db.Column(db.Float, nullable=True)
    data_pg_boleto = db.Column(db.Date, nullable=True)
    data_baixa = db.Column(db.Date, nullable=True)
    demais_info = db.Column(db.Text, nullable=True)
    obs_contabilidade = db.Column(db.Text, nullable=True)
    obs_contas_receber = db.Column(db.Text, nullable=True)
    valor_repassar_escritorio = db.Column(db.Float, nullable=True)

@app.before_request
def before_request():
    db.create_all()

@app.route('/')
def index():
    contratos = Contrato.query.all()
    return render_template('index.html', contratos=contratos)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        # Read form data...
        cpf = request.form.get('cpf')
        data_str = request.form.get('data_contrato')
        data_contrato = datetime.strptime(data_str, '%Y-%m-%d') if data_str else None
        cliente = request.form.get('cliente')
        numero = request.form.get('numero')
        tipo_contrato = request.form.get('tipo_contrato')
        cooperado = request.form.get('cooperado') or None
        garantia = request.form.get('garantia') or None
        valor = float(request.form.get('valor')) if request.form.get('valor') else None
        valor_contrato_sistema = float(request.form.get('valor_contrato_sistema')) if request.form.get('valor_contrato_sistema') else None
        baixa_acima_48_meses = True if request.form.get('baixa_acima_48_meses') else False
        valor_abatido = float(request.form.get('valor_abatido')) if request.form.get('valor_abatido') else None
        ganho = float(request.form.get('ganho')) if request.form.get('ganho') else None
        custas = float(request.form.get('custas')) if request.form.get('custas') else None
        custas_deduzidas = float(request.form.get('custas_deduzidas')) if request.form.get('custas_deduzidas') else None
        protesto = float(request.form.get('protesto')) if request.form.get('protesto') else None
        protesto_deduzido = float(request.form.get('protesto_deduzido')) if request.form.get('protesto_deduzido') else None
        honorario = float(request.form.get('honorario')) if request.form.get('honorario') else None
        honorario_repassado = float(request.form.get('honorario_repassado')) if request.form.get('honorario_repassado') else None
        alvara = float(request.form.get('alvara')) if request.form.get('alvara') else None
        alvara_recebido = float(request.form.get('alvara_recebido')) if request.form.get('alvara_recebido') else None
        valor_entrada = float(request.form.get('valor_entrada')) if request.form.get('valor_entrada') else None
        venc_str_ent = request.form.get('vencimento_entrada')
        vencimento_entrada = datetime.strptime(venc_str_ent, '%Y-%m-%d') if venc_str_ent else None
        parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else 0
        parcelas_restantes = int(request.form.get('parcelas_restantes')) if request.form.get('parcelas_restantes') else None
        valor_das_parcelas = float(request.form.get('valor_das_parcelas')) if request.form.get('valor_das_parcelas') else None
        venc_str_parc = request.form.get('vencimento_parcelas')
        vencimento_parcelas = datetime.strptime(venc_str_parc, '%Y-%m-%d') if venc_str_parc else None
        quantidade_boletos_emitidos = int(request.form.get('quantidade_boletos_emitidos')) if request.form.get('quantidade_boletos_emitidos') else None
        valor_pg_com_boleto = float(request.form.get('valor_pg_com_boleto')) if request.form.get('valor_pg_com_boleto') else None
        data_pg_str = request.form.get('data_pg_boleto')
        data_pg_boleto = datetime.strptime(data_pg_str, '%Y-%m-%d') if data_pg_str else None
        data_baixa_str = request.form.get('data_baixa')
        data_baixa = datetime.strptime(data_baixa_str, '%Y-%m-%d') if data_baixa_str else None
        demais_info = request.form.get('demais_info') or None
        obs_contabilidade = request.form.get('obs_contabilidade') or None
        obs_contas_receber = request.form.get('obs_contas_receber') or None
        valor_repassar_escritorio = float(request.form.get('valor_repassar_escritorio')) if request.form.get('valor_repassar_escritorio') else None

        contrato = Contrato(
            cpf=cpf, data_contrato=data_contrato, cliente=cliente, numero=numero,
            tipo_contrato=tipo_contrato, cooperado=cooperado, garantia=garantia,
            valor=valor, valor_contrato_sistema=valor_contrato_sistema,
            baixa_acima_48_meses=baixa_acima_48_meses, valor_abatido=valor_abatido,
            ganho=ganho, custas=custas, custas_deduzidas=custas_deduzidas,
            protesto=protesto, protesto_deduzido=protesto_deduzido,
            honorario=honorario, honorario_repassado=honorario_repassado,
            alvara=alvara, alvara_recebido=alvara_recebido,
            valor_entrada=valor_entrada, vencimento_entrada=vencimento_entrada,
            parcelas=parcelas, parcelas_restantes=parcelas_restantes,
            valor_das_parcelas=valor_das_parcelas,
            vencimento_parcelas=vencimento_parcelas,
            quantidade_boletos_emitidos=quantidade_boletos_emitidos,
            valor_pg_com_boleto=valor_pg_com_boleto,
            data_pg_boleto=data_pg_boleto, data_baixa=data_baixa,
            demais_info=demais_info,
            obs_contabilidade=obs_contabilidade,
            obs_contas_receber=obs_contas_receber,
            valor_repassar_escritorio=valor_repassar_escritorio
        )
        db.session.add(contrato)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/info/<int:id>', methods=['GET', 'POST'])
def editar_info(id):
    contrato = Contrato.query.get_or_404(id)
    if request.method == 'POST':
        contrato.cooperado = request.form.get('cooperado') or None
        contrato.garantia = request.form.get('garantia') or None
        contrato.valor = float(request.form.get('valor')) if request.form.get('valor') else None
        contrato.valor_contrato_sistema = float(request.form.get('valor_contrato_sistema')) if request.form.get('valor_contrato_sistema') else None
        contrato.baixa_acima_48_meses = True if request.form.get('baixa_acima_48_meses') else False
        contrato.valor_abatido = float(request.form.get('valor_abatido')) if request.form.get('valor_abatido') else None
        contrato.ganho = float(request.form.get('ganho')) if request.form.get('ganho') else None
        contrato.custas = float(request.form.get('custas')) if request.form.get('custas') else None
        contrato.custas_deduzidas = float(request.form.get('custas_deduzidas')) if request.form.get('custas_deduzidas') else None
        contrato.protesto = float(request.form.get('protesto')) if request.form.get('protesto') else None
        contrato.protesto_deduzido = float(request.form.get('protesto_deduzido')) if request.form.get('protesto_deduzido') else None
        contrato.honorario = float(request.form.get('honorario')) if request.form.get('honorario') else None
        contrato.honorario_repassado = float(request.form.get('honorario_repassado')) if request.form.get('honorario_repassado') else None
        contrato.alvara = float(request.form.get('alvara')) if request.form.get('alvara') else None
        contrato.alvara_recebido = float(request.form.get('alvara_recebido')) if request.form.get('alvara_recebido') else None
        contrato.valor_entrada = float(request.form.get('valor_entrada')) if request.form.get('valor_entrada') else None
        venc_str_ent = request.form.get('vencimento_entrada')
        contrato.vencimento_entrada = datetime.strptime(venc_str_ent, '%Y-%m-%d') if venc_str_ent else None
        contrato.parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else None
        contrato.parcelas_restantes = int(request.form.get('parcelas_restantes')) if request.form.get('parcelas_restantes') else None
        contrato.valor_das_parcelas = float(request.form.get('valor_das_parcelas')) if request.form.get('valor_das_parcelas') else None
        venc_str_parc = request.form.get('vencimento_parcelas')
        contrato.vencimento_parcelas = datetime.strptime(venc_str_parc, '%Y-%m-%d') if venc_str_parc else None
        contrato.quantidade_boletos_emitidos = int(request.form.get('quantidade_boletos_emitidos')) if request.form.get('quantidade_boletos_emitidos') else None
        contrato.valor_pg_com_boleto = float(request.form.get('valor_pg_com_boleto')) if request.form.get('valor_pg_com_boleto') else None
        data_pg_str = request.form.get('data_pg_boleto')
        contrato.data_pg_boleto = datetime.strptime(data_pg_str, '%Y-%m-%d') if data_pg_str else None
        data_baixa_str = request.form.get('data_baixa')
        contrato.data_baixa = datetime.strptime(data_baixa_str, '%Y-%m-%d') if data_baixa_str else None
        contrato.demais_info = request.form.get('demais_info') or None
        contrato.obs_contabilidade = request.form.get('obs_contabilidade') or None
        contrato.obs_contas_receber = request.form.get('obs_contas_receber') or None
        contrato.valor_repassar_escritorio = float(request.form.get('valor_repassar_escritorio')) if request.form.get('valor_repassar_escritorio') else None
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('info.html', contrato=contrato)

@app.route('/exportar')
def exportar():
    contratos = Contrato.query.all()
    rows = []
    for c in contratos:
        rows.append({
            'CPF': c.cpf,
            'Cliente': c.cliente,
            'Contrato': c.numero,
            'Tipo': c.tipo_contrato,
            'Cooperado': c.cooperado,
            'Garantia': c.garantia,
            'Valor': c.valor,
            'Valor no Sistema': c.valor_contrato_sistema,
            'Baixa >48m': c.baixa_acima_48_meses,
            'Valor Abatido': c.valor_abatido,
            'Ganho': c.ganho,
            'Custas': c.custas,
            'Custas Deduzidas': c.custas_deduzidas,
            'Protesto': c.protesto,
            'Protesto Deduzido': c.protesto_deduzido,
            'Honorário': c.honorario,
            'Honorário Repassado': c.honorario_repassado,
            'Alvará': c.alvara,
            'Alvará Recebido': c.alvara_recebido,
            'Valor Entrada': c.valor_entrada,
            'Venc. Entrada': c.vencimento_entrada,
            'Parcelas': c.parcelas,
            'Parcelas Restantes': c.parcelas_restantes,
            'Valor p/ Parcela': c.valor_das_parcelas,
            'Venc. Parcela': c.vencimento_parcelas,
            'Boletos Emitidos': c.quantidade_boletos_emitidos,
            'Valor pg. Boleto': c.valor_pg_com_boleto,
            'Data pg. Boleto': c.data_pg_boleto,
            'Data da Baixa': c.data_baixa,
            'Obs. Contab.': c.obs_contabilidade,
            'Obs. Cx Receb.': c.obs_contas_receber,
            'Repasse Escritório': c.valor_repassar_escritorio
        })
    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Contratos')
    output.seek(0)
    return send_file(output, download_name='contratos.xlsx', as_attachment=True)


import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
