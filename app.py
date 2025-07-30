from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import pandas as pd

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'credito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.context_processor
def inject_colors():
    return dict(
        cor_primaria="#00AE9D",
        cor_escura="#003641",
        cor_secundaria="#C9D200"
    )

db = SQLAlchemy(app)

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_contrato = db.Column(db.Date)
    cliente = db.Column(db.String(100))
    numero = db.Column(db.String(50))
    tipo_contrato = db.Column(db.String(50))
    garantia = db.Column(db.String(100))
    valor = db.Column(db.Float)
    baixa_48_meses = db.Column(db.Float)
    valor_abatido = db.Column(db.Float)
    ganho = db.Column(db.Float)
    custas = db.Column(db.Float)
    custas_deduzidas = db.Column(db.Float)
    protesto = db.Column(db.Float)
    protesto_deduzido = db.Column(db.Float)
    honorario = db.Column(db.Float)
    honorario_repassado = db.Column(db.Float)
    alvara = db.Column(db.Float)
    alvara_recebido = db.Column(db.Float)
    valor_entrada = db.Column(db.Float)
    vencimento_entrada = db.Column(db.Date)
    valor_parcelas = db.Column(db.Float)
    parcelas = db.Column(db.Integer)
    parcelas_restantes = db.Column(db.Integer)
    vencimento_parcelas = db.Column(db.Date)
    qtd_boletos = db.Column(db.Integer)
    valor_pg_boleto = db.Column(db.Float)
    data_pg_boleto = db.Column(db.Date)
    data_baixa = db.Column(db.Date)
    obs_contabilidade = db.Column(db.Text)
    obs_contas_receber = db.Column(db.Text)
    valor_repassado_escritorio = db.Column(db.Float)

class Parcela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'))
    numero = db.Column(db.Integer)
    valor = db.Column(db.Float)
    vencimento = db.Column(db.Date)
    quitada = db.Column(db.Boolean, default=False)

@app.before_request
def criar_tabelas():
    db.create_all()

@app.route('/')
def index():
    contratos = Contrato.query.all()
    return render_template('index.html', contratos=contratos)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        data_contrato_str = request.form.get('data_contrato')
        data_contrato = datetime.strptime(data_contrato_str, '%Y-%m-%d') if data_contrato_str else None
        parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else 0
        valor = float(request.form.get('valor')) if request.form.get('valor') else 0
        vencimento_parcelas = datetime.strptime(request.form.get('vencimento_parcelas'), '%Y-%m-%d') if request.form.get('vencimento_parcelas') else (data_contrato + timedelta(days=30) if data_contrato else None)

        contrato = Contrato(
            data_contrato=data_contrato,
            cliente=request.form.get('cliente') or None,
            numero=request.form.get('numero') or None,
            tipo_contrato=request.form.get('tipo_contrato') or None,
            garantia=request.form.get('garantia') or None,
            valor=valor,
            baixa_48_meses=float(request.form.get('baixa_48_meses')) if request.form.get('baixa_48_meses') else None,
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
            vencimento_entrada=datetime.strptime(request.form.get('vencimento_entrada'), '%Y-%m-%d') if request.form.get('vencimento_entrada') else data_contrato,
            valor_parcelas=float(request.form.get('valor_parcelas')) if request.form.get('valor_parcelas') else None,
            parcelas=parcelas,
            parcelas_restantes=parcelas,
            vencimento_parcelas=vencimento_parcelas,
            qtd_boletos=int(request.form.get('qtd_boletos')) if request.form.get('qtd_boletos') else None,
            valor_pg_boleto=float(request.form.get('valor_pg_boleto')) if request.form.get('valor_pg_boleto') else None,
            data_pg_boleto=datetime.strptime(request.form.get('data_pg_boleto'), '%Y-%m-%d') if request.form.get('data_pg_boleto') else None,
            data_baixa=datetime.strptime(request.form.get('data_baixa'), '%Y-%m-%d') if request.form.get('data_baixa') else None,
            obs_contabilidade=request.form.get('obs_contabilidade') or None,
            obs_contas_receber=request.form.get('obs_contas_receber') or None,
            valor_repassado_escritorio=float(request.form.get('valor_repassado_escritorio')) if request.form.get('valor_repassado_escritorio') else None
        )
        db.session.add(contrato)
        db.session.commit()

        valor_parcela = round(valor / parcelas, 2) if parcelas else 0
        for i in range(1, parcelas + 1):
            venc = (vencimento_parcelas or data_contrato) + timedelta(days=30*(i-1))
            p = Parcela(contrato_id=contrato.id, numero=i, valor=valor_parcela, vencimento=venc)
            db.session.add(p)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/contrato/<int:id>', methods=['GET', 'POST'])
def ver_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    parcelas = Parcela.query.filter_by(contrato_id=id).all()
    if request.method == 'POST':
        for field, val in request.form.items():
            if hasattr(Contrato, field):
                v = val or None
                if field in ['valor','baixa_48_meses','valor_abatido','ganho','custas','custas_deduzidas','protesto','protesto_deduzido','honorario','honorario_repassado','alvara','alvara_recebido','valor_entrada','valor_parcelas','valor_pg_boleto','valor_repassado_escritorio']:
                    v = float(v) if v else None
                elif field in ['parcelas','parcelas_restantes','qtd_boletos']:
                    v = int(v) if v else None
                elif 'data' in field or 'vencimento' in field:
                    v = datetime.strptime(v,'%Y-%m-%d') if v else None
                setattr(contrato, field, v)
        db.session.commit()
        return redirect(url_for('ver_contrato', id=id))
    return render_template('contrato.html', contrato=contrato, parcelas=parcelas)

@app.route('/parcela/<int:id>/quitar', methods=['POST'])
def quitar_parcela(id):
    p = Parcela.query.get_or_404(id)
    p.quitada = True
    contrato = Contrato.query.get(p.contrato_id)
    if contrato.parcelas_restantes:
        contrato.parcelas_restantes -= 1
    db.session.commit()
    return redirect(url_for('ver_contrato', id=contrato.id))

@app.route('/deletar', methods=['POST'])
def deletar():
    ids = request.form.getlist('ids')
    for i in ids:
        c = Contrato.query.get(int(i))
        Parcela.query.filter_by(contrato_id=c.id).delete()
        db.session.delete(c)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    dados = [c.__dict__ for c in Contrato.query.all()]
    for d in dados: d.pop('_sa_instance_state', None)
    df = pd.DataFrame(dados)
    path = os.path.join(base_dir, 'contratos_exportados.xlsx')
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
