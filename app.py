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
    cooperado = db.Column(db.String(100))
    numero = db.Column(db.String(50))
    tipo = db.Column(db.String(50))
    garantia = db.Column(db.String(100))
    valor_contrato = db.Column(db.Float)
    baixa_48 = db.Column(db.Boolean, default=False)
    valor_abatido = db.Column(db.Float, default=0.0)
    ganho = db.Column(db.Float, default=0.0)
    custas = db.Column(db.Float, default=0.0)
    custas_deduzidas = db.Column(db.Float, default=0.0)
    protesto = db.Column(db.Boolean, default=False)
    protesto_deduzido = db.Column(db.Float, default=0.0)
    honorario = db.Column(db.Float, default=0.0)
    honorario_repassado = db.Column(db.Float, default=0.0)
    alvara = db.Column(db.Boolean, default=False)
    alvara_recebido = db.Column(db.Float, default=0.0)
    valor_entrada = db.Column(db.Float, default=0.0)
    vencimento_entrada = db.Column(db.Date)
    valor_parcela = db.Column(db.Float, default=0.0)
    parcelas = db.Column(db.Integer, default=0)
    parcelas_restantes = db.Column(db.Integer, default=0)
    vencimento_parcelas = db.Column(db.Date)
    boletos_emitidos = db.Column(db.Integer, default=0)
    valor_pg_boleto = db.Column(db.Float, default=0.0)
    data_pg_boleto = db.Column(db.Date)
    data_baixa = db.Column(db.Date)
    obs_contabilidade = db.Column(db.Text)
    obs_contas = db.Column(db.Text)
    valor_repassar = db.Column(db.Float, default=0.0)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    contratos = Contrato.query.all()
    pagos = {c.id: c.valor_contrato - (c.valor_abatido or 0) for c in contratos}
    return render_template('index.html', contratos=contratos, pagos=pagos)

@app.route('/novo', methods=['GET','POST'])
def novo():
    if request.method == 'POST':
        c = Contrato(
            cooperado=request.form.get('cooperado'),
            numero=request.form.get('numero'),
            tipo=request.form.get('tipo'),
            garantia=request.form.get('garantia'),
            valor_contrato=float(request.form.get('valor_contrato') or 0),
            baixa_48=('baixa_48' in request.form),
            valor_abatido=float(request.form.get('valor_abatido') or 0),
            ganho=float(request.form.get('ganho') or 0),
            custas=float(request.form.get('custas') or 0),
            custas_deduzidas=float(request.form.get('custas_deduzidas') or 0),
            protesto=('protesto' in request.form),
            protesto_deduzido=float(request.form.get('protesto_deduzido') or 0),
            honorario=float(request.form.get('honorario') or 0),
            honorario_repassado=float(request.form.get('honorario_repassado') or 0),
            alvara=('alvara' in request.form),
            alvara_recebido=float(request.form.get('alvara_recebido') or 0),
            valor_entrada=float(request.form.get('valor_entrada') or 0),
            vencimento_entrada=datetime.strptime(request.form.get('vencimento_entrada'), '%Y-%m-%d') if request.form.get('vencimento_entrada') else None,
            valor_parcela=float(request.form.get('valor_parcela') or 0),
            parcelas=int(request.form.get('parcelas') or 0),
            parcelas_restantes=int(request.form.get('parcelas') or 0),
            vencimento_parcelas=datetime.strptime(request.form.get('vencimento_parcelas'), '%Y-%m-%d') if request.form.get('vencimento_parcelas') else None,
            boletos_emitidos=int(request.form.get('boletos_emitidos') or 0),
            valor_pg_boleto=float(request.form.get('valor_pg_boleto') or 0),
            data_pg_boleto=datetime.strptime(request.form.get('data_pg_boleto'), '%Y-%m-%d') if request.form.get('data_pg_boleto') else None,
            data_baixa=datetime.strptime(request.form.get('data_baixa'), '%Y-%m-%d') if request.form.get('data_baixa') else None,
            obs_contabilidade=request.form.get('obs_contabilidade'),
            obs_contas=request.form.get('obs_contas'),
            valor_repassar=float(request.form.get('valor_repassar') or 0)
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/info/<int:id>', methods=['GET','POST'])
def info(id):
    c = Contrato.query.get_or_404(id)
    if request.method == 'POST':
        for field in ['ganho','custas','custas_deduzidas','protesto_deduzido','honorario',
                      'honorario_repassado','alvara_recebido','valor_entrada','boletos_emitidos',
                      'valor_pg_boleto','obs_contabilidade','obs_contas','valor_repassar']:
            setattr(c, field, request.form.get(field))
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('info.html', c=c)

@app.route('/exportar')
def exportar():
    df = pd.read_sql_table('contrato', db.engine)
    path = os.path.join(base_dir, 'export.xlsx')
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
