from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'credito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contrato(db.Model):
    id                       = db.Column(db.Integer, primary_key=True)
    cpf                      = db.Column(db.String(14),  nullable=True)
    cooperado                = db.Column(db.String(100), nullable=True)
    numero                   = db.Column(db.String(50),  nullable=True)
    tipo_contrato            = db.Column(db.String(50),  nullable=True)
    garantia                 = db.Column(db.String(100), nullable=True)
    valor                    = db.Column(db.Float,       nullable=True)
    parcelas                 = db.Column(db.Integer,     default=0)
    parcelas_restantes       = db.Column(db.Integer,     default=0)

class Parcela(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'))
    numero      = db.Column(db.Integer)
    valor       = db.Column(db.Float)
    vencimento  = db.Column(db.Date)
    quitada     = db.Column(db.Boolean, default=False)
    contrato    = db.relationship('Contrato', backref=db.backref('parcelas_list', lazy=True))

@app.before_request
def criar_tabelas():
    db.create_all()

@app.route('/')
def index():
    contratos = Contrato.query.all()
    pagos = {c.id: sum(p.valor for p in c.parcelas_list if p.quitada) for c in contratos}
    return render_template('index.html', contratos=contratos, valor_pago=pagos)

@app.route('/novo', methods=['GET','POST'])
def novo():
    if request.method == 'POST':
        form = request.form
        c = Contrato(
            cpf                = form.get('cpf'),
            cooperado          = form.get('cooperado'),
            numero             = form.get('numero'),
            tipo_contrato      = form.get('tipo_contrato'),
            garantia           = form.get('garantia'),
            valor              = float(form.get('valor') or 0),
            parcelas           = int(form.get('parcelas') or 0),
            parcelas_restantes = int(form.get('parcelas') or 0),
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/contrato/<int:id>', methods=['GET','POST'])
def ver_contrato(id):
    c = Contrato.query.get_or_404(id)
    if request.method=='POST':
        return redirect(url_for('ver_contrato', id=id))
    return render_template('contrato.html', contrato=c, parcelas=c.parcelas_list)

@app.route('/parcela/<int:id>/quitar', methods=['POST'])
def quitar_parcela(id):
    p = Parcela.query.get_or_404(id)
    p.quitada = True
    cont = Contrato.query.get(p.contrato_id)
    if cont.parcelas_restantes>0:
        cont.parcelas_restantes -= 1
    db.session.commit()
    return redirect(url_for('ver_contrato', id=p.contrato_id))

@app.route('/exportar')
def exportar():
    df = pd.DataFrame([{
        'CPF': c.cpf,
        'Cooperado': c.cooperado,
        'Contrato': c.numero,
        'Tipo': c.tipo_contrato,
        'Valor': c.valor,
        'Parcelas': c.parcelas,
        'Parcelas Rest.': c.parcelas_restantes
    } for c in Contrato.query.all()])
    path = os.path.join(base_dir, 'export.xlsx')
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
