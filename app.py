import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'credito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.context_processor
def inject_colors():
    return dict(cor_primaria="#00AE9D", cor_escura="#003641", cor_secundaria="#C9D200")

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=True)
    data_contrato = db.Column(db.Date, nullable=True)
    cliente = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(50), nullable=True)
    tipo_contrato = db.Column(db.String(50), nullable=True)
    garantia = db.Column(db.String(100), nullable=True)
    valor = db.Column(db.Float, nullable=True)
    parcelas = db.Column(db.Integer, default=0)
    parcelas_restantes = db.Column(db.Integer, default=0)
    vencimento_parcelas = db.Column(db.Date, nullable=True)

class Parcela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'))
    numero = db.Column(db.Integer)
    valor = db.Column(db.Float)
    vencimento = db.Column(db.Date)
    quitada = db.Column(db.Boolean, default=False)
    contrato = db.relationship('Contrato', backref=db.backref('parcelas_list', lazy=True))

@app.before_request
def criar_tabelas():
    db.create_all()

@app.route('/')
def index():
    contratos = Contrato.query.all()
    resumo = []
    for c in contratos:
        valor_pago = sum(p.valor for p in c.parcelas_list if p.quitada)
        resumo.append({'cpf': c.cpf, 'cliente': c.cliente, 'numero': c.numero,
                       'tipo': c.tipo_contrato, 'valor': c.valor, 'valor_pago': valor_pago, 'id': c.id})
    return render_template('index.html', resumo=resumo)

@app.route('/novo', methods=['GET','POST'])
def novo():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        data_contrato = datetime.strptime(request.form['data_contrato'], '%Y-%m-%d') if request.form.get('data_contrato') else None
        cliente = request.form.get('cliente')
        numero = request.form.get('numero')
        tipo = request.form.get('tipo_contrato')
        garantia = request.form.get('garantia')
        valor = float(request.form['valor']) if request.form.get('valor') else None
        parcelas = int(request.form['parcelas']) if request.form.get('parcelas') else 0
        venc = datetime.strptime(request.form['vencimento_parcelas'], '%Y-%m-%d') if request.form.get('vencimento_parcelas') else None

        c = Contrato(cpf=cpf, data_contrato=data_contrato, cliente=cliente, numero=numero,
                     tipo_contrato=tipo, garantia=garantia, valor=valor,
                     parcelas=parcelas, parcelas_restantes=parcelas, vencimento_parcelas=venc)
        db.session.add(c)
        db.session.commit()
        if parcelas and valor and venc:
            valor_parc = round(valor/parcelas,2)
            for i in range(1, parcelas+1):
                v = venc + timedelta(days=30*(i-1))
                p = Parcela(contrato_id=c.id, numero=i, valor=valor_parc, vencimento=v)
                db.session.add(p)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/contrato/<int:id>', methods=['GET','POST'])
def ver_contrato(id):
    c = Contrato.query.get_or_404(id)
    if request.method == 'POST':
        pid = int(request.form['parcela_id'])
        p = Parcela.query.get(pid)
        if p and not p.quitada:
            p.quitada = True
            c.parcelas_restantes -= 1
            db.session.commit()
        return redirect(url_for('ver_contrato', id=id))
    return render_template('contrato.html', contrato=c, parcelas=c.parcelas_list)

@app.route('/exportar')
def exportar():
    rows = []
    for c in Contrato.query.all():
        rows.append({'CPF': c.cpf, 'Cliente': c.cliente, 'Contrato': c.numero,
                     'Tipo': c.tipo_contrato, 'Valor Contrato': c.valor,
                     'Valor Pago': sum(p.valor for p in c.parcelas_list if p.quitada)})
    df = pd.DataFrame(rows)
    path = os.path.join(base_dir,'export.xlsx')
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
