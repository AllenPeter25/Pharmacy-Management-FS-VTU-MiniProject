from flask import Flask, render_template,request,make_response,redirect,url_for
from datetime import date,datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.figure import Figure

app = Flask(__name__)

user = {"password": "1qaz"}

st_fle = r"C:\\Users\\User\\Desktop\\FS_proj\\stock.txt" 
sl_fle = r"C:\\Users\\User\\Desktop\\FS_proj\\sales.txt"
t_fle = r"C:\\Users\\User\\Desktop\\FS_proj\\temp.txt"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/menu',methods=["POST","GET"])
def menu():
    if(request.method == 'POST'):
        password = request.form.get('password')     
        if password != user['password']:
            return render_template('login.html',msg="Incorrect Password")
        return render_template("index.html")

@app.route('/menu_', methods=["POST","GET"])
def menu_():
    return render_template("index.html")

@app.route('/add',methods=["POST","GET"])
def add():
    text=''
    if request.method == "POST":
        name = request.form.get('name')
        stock = request.form.get('stock')
        text=str(name)+'|'+str(stock)+'#'
        with open(st_fle,"rt") as file:
            ch=file.read()
            file.close()
        leng=(ch.replace('|',' ').replace('#',' ')[:-1]).split(' ')
        if len(leng)>1 and name in leng:
            strt=ch.find(name)+len(name)
            end=strt
            while ch[end]!='#':end+=1
            num=int(ch[strt+1:end])+int(stock)
            ch=ch.replace(ch[strt+1:end],str(num))
            with open(st_fle,"w+") as file:
                file.write(ch)
                file.close()
        else:
            with open(st_fle,"a") as file:
                if str(name) != 'None' and str(stock) != 'None':
                    file.write(text)
                file.close()
        return render_template("add.html")
    
@app.route('/inventory', methods= ["POST","GET"])
def inventory():
        with open(st_fle,"rt") as file:
            a=file.read()
            file.close()
        a=(a.replace('|',' ').replace('#',' ')[:-1]).split(' ')
        keys=[(i) for i in a[0::2]]
        values=[(j) for j in a[1::2]]
        res = {keys[i]: int(values[i]) for i in range(len(keys))}
        return render_template("inventory.html",res=res,empty='')

def drpdwn():
    with open(st_fle,"rt") as file:
        b=file.read()
        file.close()
    tmp=b.replace('|',' ').replace('#',' ').split(' ')
    dropdown=[(j) for j in tmp[::2]][:-1]
    return dropdown

@app.route('/billing', methods=["POST","GET"])
def billing():
    if request.method == "POST":
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        amt = request.form.get('amt')
        if name== None :
            return render_template('billing.html' ,dropdown=drpdwn(),msg='',tab=[[],[]])
        else:
            with open(st_fle,"rt") as file: 
                a=file.read()
                file.close()
            a=(a.replace('|',' ').replace('#',' ')[:-1]).split(' ')
            keys=[(i) for i in a[0::2]]
            values=[(j) for j in a[1::2]]
            num=values[keys.index(name)]
            if int(quantity)>int(num):
                msg='Insufficient Stock, max quantity for '+str(name)+' is '+str(num)
                return render_template('billing.html' ,dropdown=drpdwn(),msg=msg,tab=matrix())
            else:
                price=int(quantity)*int(amt)
                text=name+'|'+str(quantity)+'|'+str(price)+'#'
                with open(t_fle,"a") as file:
                    if str(name) != None and str(quantity) != None:
                        file.write(text)
                    file.close()
                return render_template('billing.html' ,dropdown=drpdwn(),msg='',tab=matrix())
            
def matrix():
    with open(t_fle,"rt") as file: 
        a=file.read()
        file.close()
    a=(a.replace('|',' ').replace('#',' ')[:-1]).split(' ')
    return [a[i:i+3] for i in range(0, len(a), 3)]

def total():
    with open(t_fle,"rt") as file: 
        a=file.read()
        file.close()
    return sum([int(i) for i in (a.replace('|',' ').replace('#',' ').split(' ')[:-1])[2::3]])

@app.route('/receipt', methods=["POST","GET"])
def receipt():
    if request.method == "POST":
        with open(t_fle,"rt") as file:
            a = file.read()
            file.close()
        c_name= request.form.get('name')
        if len(a) == 0:
            return billing()
        elif c_name==None:
            return render_template('receipt.html',rno=(int(rno())+1),tab=matrix(),total=total())
        else:
            c_name= request.form.get('name')
            with open(t_fle,"rt") as file: 
                t=file.read()
                file.close()
            t=t.replace('#','|')[:-1]
            if c_name!= None:
                modify_stock(t)
                dte = date.today()
                text=str(int(rno())+1)+'|'+c_name+'|'+str(dte)+'|'+t+'|'+str(total())+'#'
                with open(t_fle, "w") as file:pass
                with open(sl_fle,"a") as file: 
                    file.write(text)
                    file.close()
                return render_template('index.html')
def rno():
    with open(sl_fle,"rt") as file: 
        t=file.read()
        file.close()
    if len(t)==0:return 100
    elif t.count('#')==1:
        return t.replace('|',' ').replace('#',' ').split(' ')[0]
    else:
        c=0
        a=[]
        for i in t[::]:
            c+=1
            if i== '#':
                a.append(c)
        end=a[-1]-1
        start=a[-2]
        return (t[start:end].split('|')[0])
    
def modify_stock(t):
    t=t.split('|')
    med_name=[(i) for i in t[0::3]]
    stock=[(i) for i in t[1::3]]
    x=[]
    for i in range(len(med_name)):
        y=[]
        y.append(med_name[i])
        y.append(stock[i])
        x.append(y)
    with open(st_fle,"rt") as file:
        a=file.read()
        file.close()
    a=(a.replace('|',' ').replace('#',' ')[:-1]).split(' ')
    for i in x:
        index=a.index(i[0])
        a[index+1]=int(a[index+1])-int(i[1])
    t=''
    counter=0
    for i in a:
        if counter%2==0:t+=str(i)+'|'
        else:t+=str(i)+'#'
        counter+=1
    print(t)
    with open(st_fle, "w") as file:file.write(t)
    

@app.route('/sales-report', methods=["POST","GET"])
def sales_report():
    dt=[]
    price=[]
    dt,price = monthly_df()
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(dt, price)
    axis.tick_params(axis='x', labelrotation = 20)
    canvas = FigureCanvas(fig)
    output = BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

def monthly_df():
    dt=[]
    price=[]
    buf=''  
    with open(sl_fle,"r") as file:
        while True:
            ch=file.read(1)
            if not ch:
                break
            if ch!='#':
                buf=buf+ch
            else:
                fields=buf.split('|')
                dt.append(fields[2])
                price.append(fields[-2])
                buf=''
    file.close()
    dt_obj = [datetime.strptime(j, '%Y-%m-%d').date() for j in dt] 
    pri = [int(i.replace("'",'')) for i in price]
    return dt_obj,pri

@app.route('/search_', methods=['post','get'])
def search():
    if request.method == "POST":
        no= request.form.get('no')
        if no==None:
            return render_template('search.html',tab=[],total='') 
        else:
            with open(sl_fle,"rt") as file: 
                a=file.read()
                file.close()
            a=a.split('#')
            find=str(no) 
            len_f = len(find)
            ans = []
            for i in a:
                if find == i[:len_f]:
                    ans = i
                    cpy = ans.split('|')[:4]
                    ans = ans.split('|')[3:]
                    tab = [ans[i:i+3] for i in range(0, len(ans), 3)]
                    return render_template('search.html',no=no,tab=tab[:-1],total='Total: '+str(tab[-1][0])+' Rs',
                                            date='Date: '+str(cpy[2]),name='Name:'+str(cpy[1]))
            return render_template('search.html',no=str(no)+' Not found',tab=[],total='',)

if __name__ == "__main__":
    app.run(debug=True)