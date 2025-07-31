from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import pandas as pd

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'credito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=True)
    cliente = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(50), nullable=True)
    tipo_contrato = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Float, nullable=True)
    parcelas = db.Column(db.Integer, default=0)
    parcelas_restantes = db.Column(db.Integer, default=0)
    vencimento_parcelas = db.Column(db.Date, nullable=True)
    # ... outros campos ...

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
    pagos = {c.id: sum(p.valor for p in c.parcelas_list if p.quitada) for c in contratos}
    return render_template('index.html', contratos=contratos, valor_pago=pagos)

@app.route('/novo', methods=['GET','POST'])
def novo():
    if request.method == 'POST':
        # lógica de criação...
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/parcela/<int:id>/quitar', methods=['POST'])
def quitar_parcela(id):
    # lógica...
    return redirect(url_for('index'))

@app.route('/info/<int:id>')
def info(id):
    contrato = Contrato.query.get_or_404(id)
    return render_template('info.html', contrato=contrato)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
