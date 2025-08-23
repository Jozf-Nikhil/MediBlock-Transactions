import os
from doctest import debug
from flask import Flask, render_template, request, session, redirect, flash, send_file
from flask.sessions import SecureCookieSession

from werkzeug.utils import secure_filename
from DBConnection import Db
from datetime import datetime
from collections import OrderedDict

import binascii

import Crypto

import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


app = Flask(__name__, template_folder='template', static_url_path='/static/')
UPLOAD_FOLDER = './static/image'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "asdff"


@app.route('/')
def ind():
    return render_template("HomePage.html")


@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")


@app.route('/Login')
def login():
    return render_template("login.html")


@app.route('/Adminhome')
def Adminhome():
    return render_template("AdminHome.html")


@app.route('/distributerhome')
def distributerhome():
    return render_template("distributor/distributorhome.html")



@app.route('/LogOut')
def logOut():
    return render_template("LogOut.html")


@app.route('/login1', methods=['post'])
def login1():
    name = request.form['un']
    password = request.form['pass']
    session['lid'] = name
    qry = "select * from login where admin_id='" + name + "' and password='" + password + "'"
    ob = Db()
    res = ob.selectOne(qry)
    if res is not None:
        return Adminhome()
    qry = "select * from manufacturer where idmanufacturer='" + name + "' and password='" + password + "' and status='approve'"
    ob = Db()
    res = ob.selectOne(qry)
    if res is not None:
        return distributorhome()
    qry = "select * from user_register where user_id='" + name + "' and password='" + password + "' and status='approve' "
    ob = Db()
    res = ob.selectOne(qry)
    if res is not None:
        qry = "select * from coins where user_id='" + name + "' "
        res = ob.selectOne(qry)
        co=res['coins']
        print(co)
        session['coins']=co
        return redirect('userhome')
    return "<script>alert('invalid');window.location='/';</script>"


# ---------------------------------------Admin------------------------#
@app.route('/LinkAddDistributor')
def LinkAddDistributor():
    return render_template("AddDistributor.html")


@app.route('/AddDistributor', methods=['post'])
def AddDistributor():
    did = request.form['TxtDid']
    name = request.form['TxtName']
    address = request.form['TxtAddress']
    phone = request.form['TxtPhone']
    email = request.form['TxtEmail']
    password = request.form['TxtPassword']
    fname = ''
    file = request.files['TxtPhoto']
    if file:
        filename = secure_filename(file.filename)
        fname = filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    ob = Db()
    q = "insert into manufacturer values('" + did + "','" + name + "','" + address + "','" + phone + "','" + email + "','" + password + "','" + fname + "','request')"
    ob.insert(q)
    return render_template("HomePage.html")


@app.route('/view_request')
def view_request():
    ob = Db()
    data = None
    res = ob.select("select * from manufacturer where status='request'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewRequest.html', data=res)


@app.route('/view_image')
def view_image():
    id = request.args.get('id')
    return render_template('view_image.html', img_path=id)


@app.route('/view_image_user')
def view_image_user():
    id = request.args.get('id')
    return render_template('user/view_image.html', img_path=id)



@app.route('/ViewUserRequest')
def ViewUserRequest():
    ob = Db()
    data = None
    res = ob.select("select * from user_register where status='request'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewUserRegister.html', data=res)



@app.route('/ApprovedUserRequest')
def ApprovedUserRequest():
    ob = Db()
    data = None
    res = ob.select("select * from user_register where status='approve'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ApprovedUserRegister.html', data=res)




@app.route('/ViewDistributor')
def ViewDistributor():
    ob = Db()
    data = None
    res = ob.select("select * from manufacturer where status='approve'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewDistributor.html', data=res)


@app.route('/LinkEditDistributor')
def LinkEditDistributor():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from manufacturer where idmanufacturer='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('EditDistributor.html', data=res)




@app.route('/EditDistributor', methods=['post'])
def EditDistributor():
    did = request.form['id']
    name = request.form['TxtName']
    address = request.form['TxtAddress']
    phone = request.form['TxtPhone']
    email = request.form['TxtEmail']
    password = request.form['TxtPassword']
    ob = Db()
    q = "update manufacturer set name='" + name + "',address='" + address + "',phone='" + phone + "',email='" + email + "',password='" + password + "' where idmanufacturer='" + did + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"


@app.route('/DeleteDistributor')
def DeleteDistributor():
    id = request.args.get('id')
    ob = Db()
    q = "delete from manufacturer where idmanufacturer='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"



@app.route('/approve_request')
def approve_request():
    id = request.args.get('id')
    ob = Db()
    q = "update manufacturer set status='approve' where idmanufacturer='" + id + "'"
    ob.update(q)
    return "<script>alert('Approved successfully');window.location='/Adminhome';</script>"



@app.route('/delete_user_request')
def delete_user_request():
    id = request.args.get('id')
    ob = Db()
    q = "delete from user_register where user_id='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted successfully');window.location='/Adminhome';</script>"


@app.route('/approve_user_request')
def approve_user_request():
    id = request.args.get('id')
    ob = Db()
    q = "update user_register set status='approve' where user_id='" + id + "'"
    ob.update(q)
    return "<script>alert('Approved successfully');window.location='/Adminhome';</script>"



@app.route('/approve_item_link')
def approve_item_link():
    id = request.args.get('id')
    ob = Db()
    q = "update item_details set status='approve' where iditem_details='" + str(id) + "'"
    ob.update(q)
    return "<script>alert('Approved successfully');window.location='/Adminhome';</script>"


@app.route('/no_item_stock')
def no_item_stock():
    id = request.args.get('id')
    ob = Db()
    q = "update item_details set stock_status='not available' where iditem_details='" + str(id) + "'"
    ob.update(q)
    return "<script>alert('Approved successfully');window.location='/distributerhome';</script>"


@app.route('/available_item_stock')
def available_item_stock():
    id = request.args.get('id')
    ob = Db()
    q = "update item_details set stock_status='available' where iditem_details='" + str(id) + "'"
    ob.update(q)
    return "<script>alert('Approved successfully');window.location='/distributerhome';</script>"


@app.route('/ViewOrders')
def ViewOrders():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from order_master where idmanufacturer='" + id + "' and status='paid'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewOrders.html', data=res)


@app.route('/OrderedItem')
def OrderedItem():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select(
        "select id.*,oi.* from order_items as oi join item_details as id on id.iditem_details=oi.iditem_details where oi.idorder_master='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('OrderedItem.html', data=res)


@app.route('/LinkAddItem')
def LinkAddItem():
    id = request.args.get('id')
    name = request.args.get('name')
    return render_template('AddItem.html',cid=id,cname=name)


@app.route('/AddItem', methods=['post'])
def AddItem():
    manu_id= session['lid']
    name = request.form['TxtName']
    desc = request.form['TxtDescription']
    price = request.form['TxtPrice']
    model = request.form['TxtModel']
    Batch = request.form['Batch']
    exp_date = request.form['Expiry']
    Category = request.form['Category_id']

    ob = Db()
    q = "insert into item_details values(null,'" + name + "','" + desc + "','" + price + "','" + model + "','no image','" + Batch + "','" + exp_date + "','" + Category + "','"+manu_id+"','request','available' )"
    ob.insert(q)
    return "<script>alert('Inserted successfully');window.location='/distributerhome';</script>"


@app.route('/ViewItemAdmin')
def ViewItemAdmin():
    ob = Db()

    data = None
    res = ob.select("select i.*,c.category,m.name from item_details as i join category AS c JOIN manufacturer AS m on i.category_id=c.category_id AND i.idmanufacturer=m.idmanufacturer where   i.status='request' ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/AdminHome';</script>"
    return render_template('ViewItemAdmin.html', data=res)




@app.route('/ViewItem')
def ViewItem():
    ob = Db()
    manu_id = session['lid']
    data = None
    res = ob.select("select i.*,c.category from item_details as i join category as c on i.category_id=c.category_id where i.idmanufacturer='"+manu_id+"' ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/distributerhome';</script>"
    return render_template('ViewItemD.html', data=res)


@app.route('/LinkViewItem')
def LinkViewItem():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select i.*,c.category from item_details as i join category as c on i.category_id=c.category_id where i.category_id='"+str(id)+"' ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/distributerhome';</script>"
    return render_template('ViewItem.html', data=res)




@app.route('/LinkEditItem')
def LinkEditItem():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from item_details where iditem_details='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('EditItem.html', data=res)


@app.route('/linkRegisterCategory')
def linkRegisterCategory():
    return render_template('AddCategory.html')


@app.route('/registerCategory', methods=['post'])
def registerCategory():
    Category = request.form['Category']

    ob = Db()
    q = "insert into category values(null,'" + Category + "' )"
    ob.insert(q)
    return "<script>alert('Inserted successfully');window.location='/Adminhome';</script>"


@app.route('/deleteCategory')
def deleteCategory():
    id = request.args.get('id')
    ob = Db()
    data = None
    ob.delete("delete from category where category_id='" + id + "'")
    return "<script>alert('Deleted');window.location='/Adminhome';</script>"


@app.route('/viewCategory')
def viewCategory():
    ob = Db()
    data = None
    res = ob.select("select * from category ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewCategory.html', data=res)



@app.route('/ViewCategoryDist')
def ViewCategoryDist():
    ob = Db()
    data = None
    res = ob.select("select * from category ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/distributerhome';</script>"
    return render_template('ViewCategoryDist.html', data=res)



@app.route('/view_secure_key_link')
def view_secure_key_link():
    id = request.args.get('id')
    session['select_id'] = id
    ob = Db()
    data = None
    res = ob.select(
        "SELECT item_details.name,secure_key.idsecure_key,secure_key.key_value FROM  secure_key join item_details on secure_key.iditem_details=item_details.iditem_details where secure_key.iditem_details='" + str(
            id) + "'")
    print(res)
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewKey.html', data=res)


@app.route('/confirm_user_key')
def confirm_user_key():
    id = request.args.get('id')
    print(id)
    ob = Db()
    session['key_data'] = id
    print(session['select_id'])
    itm = session['select_id']
    userid = session['lid']
    ob.insert("insert into user_order_with_key values(null,'" + userid + "','" + str(id) + "','" + itm + "' )")
    print("update secure_key set status='assigned' where key_value='" + itm + "' ")
    ob.update("update secure_key set status='assigned' where key_value='" + id + "' ")

    return "<script>alert('Secure Key Assigned...');window.location='/ViewItemsU';</script>"


@app.route('/select_user_key')
def select_user_key():
    id = request.args.get('id')
    session['select_id'] = id
    ob = Db()
    data = None
    res = ob.select(
        "SELECT item_details.name,secure_key.idsecure_key,secure_key.key_value FROM  secure_key join item_details on secure_key.iditem_details=item_details.iditem_details where secure_key.iditem_details='" + str(
            id) + "'")
    print(res)
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('user/ViewUserKey.html', data=res)


import uuid


@app.route('/add_secure_key_link')
def add_secure_key_link():
    id = request.args.get('id')
    print(uuid.uuid4())
    k = uuid.uuid4()
    ob = Db()
    q = "insert into secure_key values(null,'" + id + "','" + str(k) + "','pending') "
    ob.insert(q)
    return "<script>alert('Secure Key Generated');window.location='/ViewItem';</script>"


@app.route('/EditItem', methods=['post'])
def EditItem():
    id = request.form['id']
    name = request.form['TxtName']
    desc = request.form['TxtDescription']
    price = request.form['TxtPrice']
    model = request.form['TxtModel']
    ob = Db()
    q = "update item_details set name='" + name + "',item_description='" + desc + "',price='" + price + "',model='" + model + "' where iditem_details='" + id + "' "
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"


@app.route('/DeleteItem')
def DeleteItem():
    id = request.args.get('id')
    ob = Db()
    q = "delete from item_details where iditem_details='" + id + "' "
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"


@app.route('/LinkUploadImage')
def LinkUploadImage():
    id = request.args.get('id')
    session['itemid'] = id
    return render_template("UploadImage.html")


@app.route('/LinkUploadImageMedicine')
def LinkUploadImageMedicine():
    id = request.args.get('id')
    session['itemid'] = id
    return render_template("UploadImageMedicine.html")




@app.route('/UploadImage', methods=['post'])
def UploadImage():
    itemid = session['itemid']
    file = request.files['TxtPhoto']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    ob = Db()
    q = "update item_details set img_path='" + filename + "' where iditem_details='" + itemid + "'"
    ob.update(q)
    return ViewItem()



@app.route('/UploadImageMedicine', methods=['post'])
def UploadImageMedicine():
    itemid = session['itemid']
    file = request.files['TxtPhoto']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    ob = Db()
    q = "update item_details set model='" + filename + "' where iditem_details='" + itemid + "'"
    ob.update(q)
    return ViewItem()


# -----------------------distributor----------------------------------------------------------#
@app.route('/distributorhome')
def distributorhome():
    return render_template('distributor/distributorhome.html')


@app.route('/ViewItemD')
def ViewItemD():
    ob = Db()
    data = None
    res = ob.select("select * from item_details")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/distributorhome';</script>"
    return render_template('distributor/ViewItemD.html', data=res)


@app.route('/ViewOrdersD')
def ViewOrdersD():
    id = session['lid']
    ob = Db()
    data = None
    res = ob.select("select * from order_master where idmanufacturer='" + id + "' and status='paid'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/distributorhome';</script>"
    return render_template('distributor/ViewOrdersD.html', data=res)


@app.route('/OrderedItemD')
def OrderedItemD():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select(
        "select id.*,oi.* from order_items as oi join item_details as id on id.iditem_details=oi.iditem_details where oi.idorder_master='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/distributorhome';</script>"
    return render_template('distributor/OrderedItemD.html', data=res)


@app.route('/ShipItem')
def ShipItem():
    id = request.args.get('id')
    ob = Db()
    q = "update order_items set status='shipped' where idorder_items='" + id + "' "
    ob.update(q)
    return "<script>alert('Item Shipped succesfully');window.location='/distributorhome';</script>"


# ------------------------user----------------------------------#
@app.route('/LinkAddUserRegister')
def LinkAddUserRegister():
    return render_template("AddUserRegister.html")


@app.route('/UserRegister', methods=['post'])
def UserRegister():
    uid = request.form['TxtUserid']
    name = request.form['TxtName']
    address = request.form['TxtAddress']
    phone = request.form['TxtPhone']
    email = request.form['TxtEmail']
    password = request.form['TxtPassword']
    ob = Db()
    q = "insert into user_register values('" + uid + "','" + password + "','" + name + "','" + address + "','" + phone + "','" + email + "','request')"
    ob.insert(q)

    q = "insert into coins values(null,'" + uid + "',1 )"
    ob.insert(q)
    return "<script>alert('Register successfully');window.location='/Login';</script>"


@app.route('/userhome')
def userhome():
    orid = ""
    s = "start"
    userid = session['lid']
    ob = Db()
    data = None
    res = ob.selectOne(
        "select max(om.idorder_master) as oid from order_master as om join order_items as oi on om.idorder_master=oi.idorder_master where oi.status='carted' and om.status!='paid' and om.user_id='" + userid + "'")
    if res:
        data = res

    if (data['oid']) == None:
        session['orid'] = s
        return render_template("user/Userhome.html")
    else:
        orid = str(data['oid'])
        session['orid'] = orid
    return render_template("user/Userhome.html")


@app.route('/ViewDistributorU')
def ViewDistributorU():
    ob = Db()
    data = None
    res = ob.select("select * from manufacturer where status='approve'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template('user/ViewDistributorU.html', data=res)


@app.route('/SearchViewItemsU', methods=['post'])
def SearchViewItemsU():
    name = request.form['txtName']
    ob = Db()
    data = None
    res = ob.select("select i.*,c.category from item_details as i join category as c on i.category_id=c.category_id where i.stock_status='available' and i.name like '%"+name+"%'  ")
    print("select i.*,c.category from item_details as i join category as c on i.category_id=c.category_id where i.stock_status='available' and i.name like '%"+name+"%'  ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template('user/SearchResult.html', data=res)


@app.route('/ViewItemsU')
def ViewItemsU():
    id = request.args.get('id')
    session['did'] = id
    ob = Db()
    data = None
    res = ob.select("select i.*,c.category from item_details as i join category as c on i.category_id=c.category_id where i.stock_status='available' ")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template('user/ViewItemsU.html', data=res)


@app.route('/LinkAddToCart')
def LinkAddToCart():
    ob = Db()
    id = request.args.get('id')
    uid = session['lid']
    pid = request.args.get('p')
    img = request.args.get('img')
    session['img'] = img
    session['pid'] = pid
    uid = session['lid']
    did = session['did']
    did='abc'
    print(session['orid'] )
    session['itemid'] = id
    if session['orid'] == "start":
        q = "insert into order_master values(null,'" + uid + "','pending','pending','" + did + "','Viewed')"
        ob.insert(q)
        ob = Db()
        data = None
        res = ob.selectOne("select max(idorder_master) as oid from order_master where user_id='" + uid + "'")
        if res:
            data = res
            oid = res['oid']
            session['orid'] = oid
        if data == None:
            return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template("user/AddToCart.html")


@app.route('/AddToCart', methods=['post'])
def AddToCart():
    itemid = str(session['itemid'])
    quantity = request.form['TxtQuantity']
    pid = str(session['pid'])
    oid = str(session['orid'])

    total = int(quantity) * int(pid)
    ob = Db()
    q = "insert into order_items values(null,'" + itemid + "','" + quantity + "','" + str(
        total) + "','" + oid + "','carted',curdate())"
    print(q)
    ob.insert(q)
    ob = Db()
    q = "update order_master set status='carted',order_date=curdate() where idorder_master='" + oid + "'"
    ob.update(q)
    return "<script>alert('Carted succesfully');window.location='/userhome';</script>"


@app.route('/ViewCart')
@app.route('/ViewCart')
def ViewCart():
    userid = session['lid']
    ob = Db()
    data = None
    sum = 0

    # Fetch carted items
    res = ob.select(
        "select oi.*,id.name,id.price,id.model,om.idmanufacturer,id.img_path,om.idorder_master from order_items as oi "
        "join item_details as id join order_master as om "
        "on id.iditem_details=oi.iditem_details and om.idorder_master=oi.idorder_master "
        "where om.status='carted' and om.user_id='" + userid + "' and oi.status='carted'"
    )

    # Fetch total sum of carted items
    tot = ob.selectOne(
        "SELECT SUM(oi.total) as total FROM order_items as oi "
        "join order_master as om on om.idorder_master=oi.idorder_master "
        "where om.user_id='" + userid + "' and oi.status='Carted'"
    )

    # Store query results
    if res:
        data = res
    if tot:
        sum = tot
    else:
        sum = {'total': 0}  # Default to 0 if no matching rows

    # Process totals
    if sum and sum['total'] is not None:
        total = int(sum['total'])  # Convert to integer
        session['final_amt'] = total
        c = int(session.get('coins', 0))  # Default coins to 0 if not found
        if c >100:
            total -= c
        nc = 1
        if total > 10000:
            nc = total / 5000
            nc=nc*10
        session['new_coin'] = nc
        session['total'] = total
        print(total)
    else:
        session['final_amt'] = 0
        session['total'] = 0
        session['new_coin'] = 10

    # Return response
    if not data:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template("user/ViewCart.html", data=res)


@app.route('/ViewOrdersUser')
def ViewOrderuser():
    userid = session['lid']
    ob = Db()
    data = None
    res = ob.select(
        "select oi.*,id.name,id.price,id.model,om.idmanufacturer,id.img_path,om.idorder_master from order_items as oi join item_details as id join order_master as om on id.iditem_details=oi.iditem_details and om.idorder_master=oi.idorder_master where om.status='paid'and om.user_id='" + userid + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template('user/viewusertransactions.html', data=res)


@app.route('/LinkModifyCart')
def LinkModifyCart():
    id = request.args.get('id')
    session['itemid'] = id
    iditem = request.args.get('iditem')
    session['iditem'] = iditem
    price = request.args.get('price')
    session['price'] = price
    ob = Db()
    data = None
    res = ob.selectOne(
        "select oi.*,id.name,id.price from order_items as oi join item_details as id on id.iditem_details=oi.iditem_details where oi.order_item_id='" + id + "'")
    if res:
        data = res
        qu = res['quantity']
        session['qu'] = qu
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template("user/SelectOrderItem.html", data=res)


@app.route('/EditCart', methods=['post'])
def EditCart():
    itemid = session['itemid']
    quantity = request.form['TxtQuantity']
    price = session['price']
    itemprice = int(quantity) * int(price)

    ob = Db()
    q = "update order_items set quantity='" + quantity + "',total='" + str(itemprice) + "' where order_item_id='" + str(
        itemid) + "' "
    ob.update(q)

    return ViewCart()


@app.route('/send_feedback_link', methods=['get'])
def send_feedback_link():
    return render_template("user/SendFeedback.html")



@app.route('/send_feedback', methods=['post'])
def send_feedback():
    feed = request.form['txtFeed']
    user_id=session['lid']
    ob = Db()
    q = "insert into feedback  values(null,'" + user_id + "','" + feed + "',curdate(),'no reply ')"
    ob.insert(q)
    return render_template("user/Userhome.html")


@app.route('/deleteCart')
def deleteCart():
    id = request.args.get('id')
    ob = Db()
    q = "delete from order_items where order_item_id='" + id + "' "
    ob.delete(q)
    return ViewCart()



@app.route('/view_feedback')
def view_feedback():
    ob = Db()
    data = None
    res = ob.select("select * from feedback")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template('/ViewFeedback.html', data=res)



@app.route('/ChangeDistributor')
def ChangeDistributor():
    ob = Db()
    data = None
    res = ob.select("select * from idmanufacturer")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/userhome';</script>"
    return render_template('user/ViewDistributorUs.html', data=res)


@app.route('/Distributorchange')
def Distributorchange():
    id = request.args.get('id')
    mid = session['orid']
    ob = Db()
    q = "update order_master set idmanufacturer='" + id + "' where idorder_master='" + mid + "' "
    ob.update(q)
    return ViewCart()


@app.route('/wallet')
def wallet():
    return render_template("user/index.html")


@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()
    response = {
        'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    }
    session['public'] = response['public_key']
    session['private'] = response['private_key']
    return jsonify(response), 200


@app.route('/card_link')
def card_link():
    return render_template('user/card_details.html')


@app.route('/card_action', methods=['POST'])
def card_action():
    txt_card_no = request.form['txt_card_no']
    txt_cvv = request.form['txt_cvv']
    txt_year = request.form['txt_year']
    txt_name = request.form['txt_name']
    data = None
    ob = Db()
    q = "select * from card_details where card_no='" + txt_card_no + "' and cvv='" + txt_cvv + "'  and expiry_year='" + txt_year + "' and card_holder_name='" + txt_name + "'  "
    res = ob.selectOne(q)
    if res:
        data = res
        coin= session['new_coin']
        userid = session['lid']

        q =  "UPDATE coins SET coins = coins + "+ str(coin) +" WHERE user_id ='"+userid+"' "
        ob.update(q)

    if data == None:
        return "<script>alert('Invalid Card Details');window.location='/card_link';</script>"
    return render_template('user/make_transaction.html')


@app.route('/make/transaction')
def make_transaction():
    return render_template('user/make_transaction.html')


@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
    sender_address = request.form['sender_address']
    sender_private_key = request.form['sender_private_key']
    recipient_address = request.form['recipient_address']
    value = request.form['amount']
    order_id = session['orid']
    userid = session['lid']

    transaction = Transaction(sender_address, sender_private_key, recipient_address, value)

    response = {'transaction': transaction.to_dict(), 'signature': transaction.sign_transaction()}
    ob = Db()
    q = "insert into payment values(null,'" + sender_address + "','" + recipient_address + "','" + value + "','" + order_id + "','" + userid + "')"
    ob.insert(q)
    ob = Db()
    q = "update order_master set status='paid',total_amount='" + value + "' where idorder_master='" + order_id + "'"
    ob.update(q)
    ob = Db()
    q = "update order_items set status='ordered' where idorder_master='" + order_id + "'"
    ob.update(q)
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)

    app.run(debug=True)
