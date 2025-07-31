from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from io import BytesIO
import os

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
    valor_contrato_sistema = db.Column(db.Float, nullable=True)
    baixa_acima_48_meses = db.Column(db.Boolean, default=False)
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
    valor_das_parcelas = db.Column(db.Float, nullable=True)
    parcelas = db.Column(db.Integer, default=0)
    parcelas_restantes = db.Column(db.Integer, default=0)
    vencimento_parcelas = db.Column(db.Date, nullable=True)
    quantidade_boletos_emitidos = db.Column(db.Integer, nullable=True)
    valor_pg_com_boleto = db.Column(db.Float, nullable=True)
    data_pg_boleto = db.Column(db.Date, nullable=True)
    data_baixa = db.Column(db.Date, nullable=True)
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
        c = Contrato(
            cpf=request.form.get('cpf'),
            data_contrato=datetime.strptime(request.form.get('data_contrato'), '%Y-%m-%d') if request.form.get('data_contrato') else None,
            cliente=request.form.get('cliente'),
            numero=request.form.get('numero'),
            tipo_contrato=request.form.get('tipo_contrato'),
            cooperado=request.form.get('cooperado'),
            garantia=request.form.get('garantia'),
            valor_contrato_sistema=float(request.form.get('valor_contrato_sistema')) if request.form.get('valor_contrato_sistema') else None,
            baixa_acima_48_meses=bool(request.form.get('baixa_acima_48_meses')),
            valor_abatido=float(request.form.get('valor_abatido')) if request.form.get('valor_abatido') else None,
            ganho=float(request.form.get('ganho')) if request.form.get('ganho') else None,
            custas=float(request.form.get('custas')) if request.form.get('custas') else None,
            custas_deduzidas=float(request.form.get('custas_deduzidas')) if request.form.get('custas_deduzidas') else None,
            protesto=float(request.form.get('protesto')) if request.form.get('protesto') else None,
            protesto_deduzido=float(request.form.get('protesto_deduzido')) if request.form.get('protesto_deduzido') else None,
            honorario=float(request.form.get('honorario')) if request.form.get('honorario') else None,
            honorario_repassado=float(request.form.get('honorario_repassado')) if request.form.get('honorario_repassado') else None,
            alvara=float(request.form.get('alvara')) if request.form.get('alvara') else None,
            alvara_recebido=float(request.form.get('alvara_recebido')) if request.form.get('alvara_recebido') else None,
            valor_entrada=float(request.form.get('valor_entrada')) if request.form.get('valor_entrada') else None,
            vencimento_entrada=datetime.strptime(request.form.get('vencimento_entrada'), '%Y-%m-%d') if request.form.get('vencimento_entrada') else None,
            valor_das_parcelas=float(request.form.get('valor_das_parcelas')) if request.form.get('valor_das_parcelas') else None,
            parcelas=int(request.form.get('parcelas')) if request.form.get('parcelas') else 0,
            parcelas_restantes=int(request.form.get('parcelas_restantes')) if request.form.get('parcelas_restantes') else 0,
            vencimento_parcelas=datetime.strptime(request.form.get('vencimento_parcelas'), '%Y-%m-%d') if request.form.get('vencimento_parcelas') else None,
            quantidade_boletos_emitidos=int(request.form.get('quantidade_boletos_emitidos')) if request.form.get('quantidade_boletos_emitidos') else None,
            valor_pg_com_boleto=float(request.form.get('valor_pg_com_boleto')) if request.form.get('valor_pg_com_boleto') else None,
            data_pg_boleto=datetime.strptime(request.form.get('data_pg_boleto'), '%Y-%m-%d') if request.form.get('data_pg_boleto') else None,
            data_baixa=datetime.strptime(request.form.get('data_baixa'), '%Y-%m-%d') if request.form.get('data_baixa') else None,
            obs_contabilidade=request.form.get('obs_contabilidade'),
            obs_contas_receber=request.form.get('obs_contas_receber'),
            valor_repassar_escritorio=float(request.form.get('valor_repassar_escritorio')) if request.form.get('valor_repassar_escritorio') else None
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/info/<int:id>', methods=['GET','POST'])
def editar_info(id):
    c = Contrato.query.get_or_404(id)
    if request.method == 'POST':
        c.cooperado = request.form.get('cooperado')
        c.garantia = request.form.get('garantia')
        c.valor_contrato_sistema = float(request.form.get('valor_contrato_sistema')) if request.form.get('valor_contrato_sistema') else c.valor_contrato_sistema
        c.baixa_acima_48_meses = bool(request.form.get('baixa_acima_48_meses'))
        c.valor_abatido = float(request.form.get('valor_abatido')) if request.form.get('valor_abatido') else c.valor_abatido
        c.ganho = float(request.form.get('ganho')) if request.form.get('ganho') else c.ganho
        c.custas = float(request.form.get('custas')) if request.form.get('custas') else c.custas
        c.custas_deduzidas = float(request.form.get('custas_deduzidas')) if request.form.get('custas_deduzidas') else c.custas_deduzidas
        c.protesto = float(request.form.get('protesto')) if request.form.get('protesto') else c.protesto
        c.protesto_deduzido = float(request.form.get('protesto_deduzido')) if request.form.get('protesto_deduzido') else c.protesto_deduzido
        c.honorario = float(request.form.get('honorario')) if request.form.get('honorario') else c.honorario
        c.honorario_repassado = float(request.form.get('honorario_repassado')) if request.form.get('honorario_repassado') else c.honorario_repassado
        c.alvara = float(request.form.get('alvara')) if request.form.get('alvara') else c.alvara
        c.alvara_recebido = float(request.form.get('alvara_recebido')) if request.form.get('alvara_recebido') else c.alvara_recebido
        c.valor_entrada = float(request.form.get('valor_entrada')) if request.form.get('valor_entrada') else c.valor_entrada
        c.vencimento_entrada = datetime.strptime(request.form.get('vencimento_entrada'), '%Y-%m-%d') if request.form.get('vencimento_entrada') else c.vencimento_entrada
        c.valor_das_parcelas = float(request.form.get('valor_das_parcelas')) if request.form.get('valor_das_parcelas') else c.valor_das_parcelas
        c.parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else c.parcelas
        c.parcelas_restantes = int(request.form.get('parcelas_restantes')) if request.form.get('parcelas_restantes') else c.parcelas_restantes
        c.vencimento_parcelas = datetime.strptime(request.form.get('vencimento_parcelas'), '%Y-%m-%d') if request.form.get('vencimento_parcelas') else c.vencimento_parcelas
        c.quantidade_boletos_emitidos = int(request.form.get('quantidade_boletos_emitidos')) if request.form.get('quantidade_boletos_emitidos') else c.quantidade_boletos_emitidos
        c.valor_pg_com_boleto = float(request.form.get('valor_pg_com_boleto')) if request.form.get('valor_pg_com_boleto') else c.valor_pg_com_boleto
        c.data_pg_boleto = datetime.strptime(request.form.get('data_pg_boleto'), '%Y-%m-%d') if request.form.get('data_pg_boleto') else c.data_pg_boleto
        c.data_baixa = datetime.strptime(request.form.get('data_baixa'), '%Y-%m-%d') if request.form.get('data_baixa') else c.data_baixa
        c.obs_contabilidade = request.form.get('obs_contabilidade')
        c.obs_contas_receber = request.form.get('obs_contas_receber')
        c.valor_repassar_escritorio = float(request.form.get('valor_repassar_escritorio')) if request.form.get('valor_repassar_escritorio') else c.valor_repassar_escritorio
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('info.html', contrato=c)

@app.route('/parcelas/<int:id>')
def parcelas(id):
    c = Contrato.query.get_or_404(id)
    return render_template('parcelas.html', contrato=c)

@app.route('/exportar')
def exportar():
    contratos = Contrato.query.all()
    data = [{col: getattr(c, attr) for col, attr in [
        ('CPF','cpf'),('Cliente','cliente'),('Contrato','numero'),('Tipo','tipo_contrato'),
        ('Cooperado','cooperado'),('Garantia','garantia'),('Valor Contrato Sistema','valor_contrato_sistema'),
        ('Baixa >48m','baixa_acima_48_meses'),('Valor Abatido','valor_abatido'),('Ganho','ganho'),
        ('Custas','custas'),('Custas Deduzidas','custas_deduzidas'),('Protesto','protesto'),
        ('Protesto Deduzido','protesto_deduzido'),('Honorario','honorario'),
        ('Honorario Repassado','honorario_repassado'),('Alvará','alvara'),
        ('Alvará Recebido','alvara_recebido'),('Valor Entrada','valor_entrada'),
        ('Vencimento Entrada','vencimento_entrada'),('Valor Parcelas','valor_das_parcelas'),
        ('Parcelas','parcelas'),('Parcelas Restantes','parcelas_restantes'),
        ('Vencimento Parcelas','vencimento_parcelas'),
        ('Quantidade Boletos','quantidade_boletos_emitidos'),
        ('Valor Pg Boleto','valor_pg_com_boleto'),
        ('Data Pg Boleto','data_pg_boleto'),('Data Baixa','data_baixa'),
        ('Obs Contabilidade','obs_contabilidade'),('Obs Contas Receber','obs_contas_receber'),
        ('Valor Repassar Escritório','valor_repassar_escritorio')
    ]} for c in contratos]
    df = pd.DataFrame(data)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return send_file(buf, download_name='contratos.xlsx', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
