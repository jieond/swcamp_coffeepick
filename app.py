from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

# mac에서 에러가 나는 경우 >> 사용하고 있는 인터넷 환경에 따라 보안 관련 추가 설정 2가지 필요
# 1) certifi 패키지 설치 및 임포트
import certifi
ca = certifi.where()

# 내 mogoDB 정보 가져오기 - 패스워드, 클러스터 이름 커스텀
# 2) tlsCAFile=ca 추가
client = MongoClient('mongodb+srv://test:sparta@cluster0.xcdajnw.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.sparta

@app.route('/')
def main():
   return render_template('main.html')

@app.route('/order/<order_num>')
def move_to_order(order_num):
    return render_template('order.html', order_num=order_num)


@app.route("/main", methods=["POST"])
def web_main_post():
    order_name_receive = request.form['order_name_give']
    due_receive = request.form['due_give']
    cafe_name_receive = request.form['cafe_name_give']

    if order_name_receive == "" or due_receive == "" or cafe_name_receive == "-- 매장 선택 --" or cafe_name_receive == "준비중":
        return jsonify({'msg': '모든 값을 입력해주세요','order_num':"0"})
    else:
        order_num = db.main.count_documents({})+1

        doc = {
            'order_num': order_num,
            'order_name': order_name_receive,
            'due': due_receive,
            'cafe_name': cafe_name_receive
        }

        db.main.insert_one(doc)

        # ret = db.orders.insert_one(doc)


        return jsonify({'msg': '주문서 생성 완료!','order_num':order_num})

@app.route("/main_cafe_list", methods=["GET"])
def web_main_cafe_list_get():
    cafe_list = list(db.cafe_list.find({}, {'_id':False}))
    return jsonify({'cafe_list': cafe_list})

@app.route("/main_order", methods=["GET"])
def web_main_order_get():
    order_list = list(db.main.find({}, {'_id': False}))
    return jsonify({'orders':order_list})

@app.route("/order_cafe_list", methods=["GET"])
def web_order_cafe_list_get():
    cafe_list = list(db.cafe_list.find({}, {'_id': False}))
    return jsonify({'orders': cafe_list})

@app.route("/order", methods=["POST"])
def web_order_post():
    num_receive = request.form['num_give']    # 주문번호_링크 맨 뒷자리
    name_receive = request.form['name_give']  # 정선영
    menu_receive = request.form['menu_give']  # 아메리카노
    type_receive = request.form['type_give']  # ICE
    size_receive = request.form['size_give']  # M

    if name_receive == "" or menu_receive == "-- 골라보세요 --" or type_receive == "-- ICE/HOT --" or size_receive == "-- S/M/L --":
        return jsonify({'msg': '모든 값을 입력해주세요'})
    else:
        doc = {
            'order_num': num_receive,
            'user_name': name_receive,
            'menu': menu_receive,
            'ondo_type': type_receive,
            'size': size_receive
        }
        db.order.insert_one(doc)

        existing_record = db.order_count.find_one({'order_num': num_receive, 'menu': menu_receive, 'size': size_receive, 'ondo_type': type_receive})

        if existing_record is not None:
            db.order_count.update_one({'_id': existing_record['_id']}, {'$inc': {'count': 1}})
        else:
            db.order_count.insert_one({'order_num': num_receive, 'menu': menu_receive, 'size': size_receive, 'ondo_type': type_receive, 'count': 1})

        return jsonify({'msg': 'coffee 주문 완료!'})

@app.route("/order", methods=["GET"])
def web_order_get():
    order_list = list(db.order.find({}, {'_id': False}))
    return jsonify({'orders': order_list})

@app.route("/order", methods=["GET"])
def order_get():
    order_list = list(db.orders.find({},{'_id':False}))
    return jsonify({'orders':order_list})

#### 경록 주문 집계 GET ####

@app.route('/order_count', methods=['GET'])
def get_order_count():
    order_counts = list(db['order_count'].find({},{'_id':False}))
    return jsonify({"order_counts": order_counts})

#### 경록 주문 삭제 ####

@app.route('/delete-item', methods=['DELETE'])
def delete_item():
    order_collection = db["order"]

    name = request.args.get("user_name")
    size = request.args.get("size")
    ondo_type = request.args.get("ondo_type")
    menu = request.args.get("menu")

    order_collection.delete_one({
        "user_name": name,
        "size": size,
        "ondo_type": ondo_type,
        "menu": menu
    })

    return jsonify({"result": "success"})



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)