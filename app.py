# Requisitos:
# pip install -r requirements.txt

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
    return render_template('index.html', contratos=contratos)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        data_str = request.form.get('data_contrato')
        data_contrato = datetime.strptime(data_str, '%Y-%m-%d') if data_str else None
        cliente = request.form.get('cliente') or None
        numero = request.form.get('numero') or None
        tipo = request.form.get('tipo_contrato') or None
        garantia = request.form.get('garantia') or None
        valor = float(request.form.get('valor')) if request.form.get('valor') else None
        parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else 0
        vencimento_init_str = request.form.get('vencimento_parcelas')
        vencimento_init = datetime.strptime(vencimento_init_str, '%Y-%m-%d') if vencimento_init_str else (data_contrato + timedelta(days=30) if data_contrato else None)

        contrato = Contrato(
            data_contrato=data_contrato,
            cliente=cliente,
            numero=numero,
            tipo_contrato=tipo,
            garantia=garantia,
            valor=valor,
            parcelas=parcelas,
            parcelas_restantes=parcelas,
            vencimento_parcelas=vencimento_init
        )
        db.session.add(contrato)
        db.session.commit()

        if parcelas and valor and vencimento_init:
            valor_parc = round(valor / parcelas, 2)
            for i in range(1, parcelas + 1):
                venc = vencimento_init + timedelta(days=30*(i-1))
                p = Parcela(contrato_id=contrato.id, numero=i, valor=valor_parc, vencimento=venc)
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
                if val == '':
                    setattr(contrato, field, None)
                elif field in ['valor']:
                    setattr(contrato, field, float(val))
                elif field in ['parcelas', 'parcelas_restantes']:
                    setattr(contrato, field, int(val))
                elif field in ['data_contrato', 'vencimento_parcelas']:
                    setattr(contrato, field, datetime.strptime(val, '%Y-%m-%d'))
                else:
                    setattr(contrato, field, val)
        db.session.commit()
        return redirect(url_for('ver_contrato', id=id))

    return render_template('contrato.html', contrato=contrato, parcelas=parcelas)

@app.route('/parcela/<int:id>/quitar', methods=['POST'])
def quitar_parcela(id):
    p = Parcela.query.get_or_404(id)
    p.quitada = True
    cont = Contrato.query.get(p.contrato_id)
    if cont.parcelas_restantes > 0:
        cont.parcelas_restantes -= 1
    db.session.commit()
    return redirect(url_for('ver_contrato', id=p.contrato_id))

@app.route('/deletar', methods=['POST'])
def deletar():
    ids = request.form.getlist('ids')
    for i in ids:
        c = Contrato.query.get(int(i))
        if c:
            Parcela.query.filter_by(contrato_id=c.id).delete()
            db.session.delete(c)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/exportar')
def exportar():
    contratos = Contrato.query.all()
    data = []
    for c in contratos:
        d = c.__dict__.copy()
        d.pop('_sa_instance_state', None)
        data.append(d)
    df = pd.DataFrame(data)
    path = os.path.join(base_dir, 'export.xlsx')
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
