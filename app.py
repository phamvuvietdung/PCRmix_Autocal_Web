from flask import Flask, render_template, request, jsonify
import os
import pandas as pd  # 🔹 Bổ sung import Pandas
from pyngrok import ngrok # ngrok để chạy local tunnel

app = Flask(__name__)

# Định nghĩa thư mục lưu database
DATABASE_FOLDER = "database"
if not os.path.exists(DATABASE_FOLDER):
    os.makedirs(DATABASE_FOLDER)

# Trang chính (Mix phản ứng)
@app.route("/")
def mix_page():
    return render_template("mix.html")

# Hàm lấy danh sách file CSV trong thư mục database
def get_csv_files():
    return [f.replace(".csv", "") for f in os.listdir(DATABASE_FOLDER) if f.endswith(".csv")]

# API load danh sách chỉ tiêu
@app.route("/get_chi_tieu", methods=["GET"])
def get_chi_tieu():
    list_database = get_csv_files()
    return jsonify(list_database)

# API load dữ liệu từ file CSV
@app.route("/load_data", methods=["POST"])
def load_data():
    try:
        chi_tieu = request.json.get("chi_tieu")
        so_pu = request.json.get("so_pu", 1)  # Mặc định 1 nếu không có giá trị
        so_pu_ic = request.json.get("so_pu_ic", 1)  # Mặc định 1 nếu không có giá trị

        # Kiểm tra đầu vào hợp lệ
        if not chi_tieu:
            return jsonify({"status": "error", "message": "Tên chỉ tiêu không hợp lệ!"})

        # Kiểm tra file CSV có tồn tại không
        file_path = os.path.join(DATABASE_FOLDER, f"{chi_tieu}.csv")
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "Không tìm thấy file dữ liệu!"})

        # Đọc dữ liệu từ file CSV
        df = pd.read_csv(file_path).fillna("-")  # Thay thế NaN bằng "-"

        # 🔹 Kiểm tra số cột nếu 2 cột thì chỉ nhân cột B, còn 3 cột thì nhân cột B và C
        if df.shape[1] < 3:
            # return jsonify({"status": "error", "message": "File không đúng định dạng!"})
            df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0) * float(so_pu)  # Nhân cột B với số phản ứng

        # 🔹 Thực hiện tính toán mastermix:
        else:
            df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0) * float(so_pu)  # Nhân cột B với số phản ứng
            df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2], errors="coerce").fillna(0) * float(so_pu_ic)  # Nhân cột C với số PU IC

        # 🔹 Lấy danh sách tên cột động
        column_names = df.columns.tolist()
        
        # Chuyển kết quả thành danh sách để gửi về frontend
        data = df.values.tolist()

        return jsonify({"status": "success", "columns": column_names, "data": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Trang "Thêm chỉ tiêu"
@app.route("/add")
def add_page():
    return render_template("add.html")

if __name__ == "__main__":
    app.run(debug=True)
    
    # Chạy Ngrok
    public_url = ngrok.connect(5000)
    print(f"Ngrok URL: {public_url}")