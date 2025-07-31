import os
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'credito.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contrato(db.Model):
    id                         = db.Column(db.Integer, primary_key=True)
    cpf                        = db.Column(db.String(14), nullable=True)
    data_contrato              = db.Column(db.Date, nullable=True)
    cliente                    = db.Column(db.String(100), nullable=True)
    numero                     = db.Column(db.String(50), nullable=True)
    tipo_contrato              = db.Column(db.String(50), nullable=True)
    garantia                   = db.Column(db.String(100), nullable=True)
    valor                      = db.Column(db.Float, nullable=True)
    parcelas                   = db.Column(db.Integer, default=0)
    parcelas_restantes         = db.Column(db.Integer, default=0)
    vencimento_parcelas        = db.Column(db.Date, nullable=True)

    baixa_acima_48_meses       = db.Column(db.Boolean, default=False)
    valor_abatido              = db.Column(db.Float, default=0.0)
    ganho                      = db.Column(db.Float, default=0.0)
    custas                     = db.Column(db.Float, default=0.0)
    custas_deduzidas           = db.Column(db.Float, default=0.0)
    protesto                   = db.Column(db.Float, default=0.0)
    protesto_deduzido          = db.Column(db.Float, default=0.0)
    honorario                  = db.Column(db.Float, default=0.0)
    honorario_repassado        = db.Column(db.Float, default=0.0)
    alvara                     = db.Column(db.Float, default=0.0)
    alvara_recebido            = db.Column(db.Float, default=0.0)
    valor_entrada              = db.Column(db.Float, default=0.0)
    vencimento_entrada         = db.Column(db.Date, nullable=True)
    quantidade_boletos_emitidos= db.Column(db.Integer, default=0)
    valor_pg_boleto            = db.Column(db.Float, default=0.0)
    data_pg_boleto             = db.Column(db.Date, nullable=True)
    data_baixa                 = db.Column(db.Date, nullable=True)
    obs_contabilidade          = db.Column(db.Text, nullable=True)
    obs_contas_receber         = db.Column(db.Text, nullable=True)
    valor_repassado_escritorio = db.Column(db.Float, default=0.0)

class Parcela(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    contrato_id  = db.Column(db.Integer, db.ForeignKey('contrato.id'))
    numero       = db.Column(db.Integer)
    valor        = db.Column(db.Float)
    vencimento   = db.Column(db.Date)
    quitada      = db.Column(db.Boolean, default=False)
    contrato     = db.relationship('Contrato', backref=db.backref('parcelas_list', lazy=True))

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
        c = Contrato(
            cpf=request.form.get('cpf'),
            data_contrato=datetime.strptime(request.form['data_contrato'],'%Y-%m-%d') if request.form.get('data_contrato') else None,
            cliente=request.form.get('cliente'),
            numero=request.form.get('numero'),
            tipo_contrato=request.form.get('tipo_contrato'),
            garantia=request.form.get('garantia'),
            valor=float(request.form['valor']) if request.form.get('valor') else None,
            parcelas=int(request.form['parcelas']) if request.form.get('parcelas') else 0,
            parcelas_restantes=int(request.form['parcelas']) if request.form.get('parcelas') else 0,
            vencimento_parcelas=datetime.strptime(request.form['vencimento_parcelas'],'%Y-%m-%d') if request.form.get('vencimento_parcelas') else None
        )
        db.session.add(c)
        db.session.commit()
        if c.parcelas and c.valor and c.vencimento_parcelas:
            valor_parc = round(c.valor/c.parcelas,2)
            for i in range(1,c.parcelas+1):
                dt = c.vencimento_parcelas + timedelta(days=30*(i-1))
                db.session.add(Parcela(contrato_id=c.id, numero=i, valor=valor_parc, vencimento=dt))
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/contrato/<int:id>', methods=['GET','POST'])
def ver_contrato(id):
    c = Contrato.query.get_or_404(id)
    if request.method=='POST':
        for fld in ['cpf','cliente','numero','tipo_contrato','garantia','valor',
                    'parcelas','parcelas_restantes']:
            if fld in request.form:
                val = request.form[fld]
                setattr(c, fld, (float(val) if fld=='valor' and val else int(val) if fld in ['parcelas','parcelas_restantes'] and val else val or None))
        for datefld in ['data_contrato','vencimento_parcelas','vencimento_entrada','data_pg_boleto','data_baixa']:
            if datefld in request.form and request.form[datefld]:
                setattr(c, datefld, datetime.strptime(request.form[datefld],'%Y-%m-%d'))
        bools = ['baixa_acima_48_meses']
        floats = ['valor_abatido','ganho','custas','custas_deduzidas','protesto','protesto_deduzido',
                  'honorario','honorario_repassado','alvara','alvara_recebido',
                  'valor_entrada','valor_pg_boleto','valor_repassado_escritorio']
        ints   = ['quantidade_boletos_emitidos']
        texts  = ['obs_contabilidade','obs_contas_receber']
        for fld in floats:
            if fld in request.form:
                c.__setattr__(fld, float(request.form[fld]) if request.form[fld] else 0.0)
        for fld in ints:
            if fld in request.form:
                c.__setattr__(fld, int(request.form[fld]) if request.form[fld] else 0)
        for fld in texts:
            if fld in request.form:
                c.__setattr__(fld, request.form[fld])
        for fld in bools:
            c.__setattr__(fld, request.form.get(fld)=='on')
        db.session.commit()
        return redirect(url_for('ver_contrato', id=id))
    return render_template('contrato.html', contrato=c)

@app.route('/parcela/<int:id>/quitar', methods=['POST'])
def quitar_parcela(id):
    p = Parcela.query.get_or_404(id)
    p.quitada = True
    p.contrato.parcelas_restantes -= 1
    db.session.commit()
    return redirect(url_for('ver_contrato', id=p.contrato_id))

@app.route('/exportar')
def exportar():
    df = pd.DataFrame([c.__dict__ for c in Contrato.query.all()])
    df = df.drop(columns=['_sa_instance_state'])
    path = os.path.join(base_dir,'export.xlsx')
    df.to_excel(path,index=False)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
