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
    id              = db.Column(db.Integer, primary_key=True)
    cpf             = db.Column(db.String(14), nullable=True)
    data_contrato   = db.Column(db.Date, nullable=True)
    cliente         = db.Column(db.String(100), nullable=True)
    numero          = db.Column(db.String(50), nullable=True)
    tipo_contrato   = db.Column(db.String(50), nullable=True)
    garantia        = db.Column(db.String(100), nullable=True)
    valor           = db.Column(db.Float, nullable=True)
    parcelas        = db.Column(db.Integer, default=0)
    parcelas_restantes = db.Column(db.Integer, default=0)
    vencimento_parcelas = db.Column(db.Date, nullable=True)
    demais_info     = db.Column(db.Text, nullable=True)

class Parcela(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    contrato_id   = db.Column(db.Integer, db.ForeignKey('contrato.id'))
    numero        = db.Column(db.Integer)
    valor         = db.Column(db.Float)
    vencimento    = db.Column(db.Date)
    quitada       = db.Column(db.Boolean, default=False)
    contrato      = db.relationship('Contrato', backref=db.backref('parcelas_list', lazy=True))

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
        cpf_str = request.form.get('cpf') or None
        data_str = request.form.get('data_contrato')
        data_contrato = datetime.strptime(data_str, '%Y-%m-%d') if data_str else None
        cliente  = request.form.get('cliente') or None
        numero   = request.form.get('numero') or None
        tipo     = request.form.get('tipo_contrato') or None
        garantia = request.form.get('garantia') or None
        valor    = float(request.form.get('valor')) if request.form.get('valor') else None
        parcelas = int(request.form.get('parcelas')) if request.form.get('parcelas') else 0
        venc_str = request.form.get('vencimento_parcelas')
        venc_init = datetime.strptime(venc_str,'%Y-%m-%d') if venc_str else (data_contrato + timedelta(days=30) if data_contrato else None)

        contrato = Contrato(
            cpf=cpf_str,
            data_contrato=data_contrato,
            cliente=cliente,
            numero=numero,
            tipo_contrato=tipo,
            garantia=garantia,
            valor=valor,
            parcelas=parcelas,
            parcelas_restantes=parcelas,
            vencimento_parcelas=venc_init
        )
        db.session.add(contrato)
        db.session.commit()

        if parcelas and valor and venc_init:
            valor_parc = round(valor/parcelas,2)
            for i in range(1,parcelas+1):
                venc = venc_init + timedelta(days=30*(i-1))
                p = Parcela(contrato_id=contrato.id, numero=i, valor=valor_parc, vencimento=venc)
                db.session.add(p)
            db.session.commit()

        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/contrato/<int:id>')
def ver_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    parcelas = contrato.parcelas_list
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

@app.route('/contrato/<int:id>/info', methods=['GET','POST'])
def editar_info(id):
    contrato = Contrato.query.get_or_404(id)
    if request.method == 'POST':
        contrato.garantia = request.form.get('garantia') or None
        contrato.valor = float(request.form.get('valor')) if request.form.get('valor') else None
        contrato.demais_info = request.form.get('demais_info') or None
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('info.html', contrato=contrato)

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
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
