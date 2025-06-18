1. Giới thiệu bài toán
Bài toán: Cần xây dựng một hệ thống cho phép người dùng đăng nhập, gửi file dữ liệu cho nhau qua web, mỗi file đều được ký số nhằm đảm bảo tính xác thực (ai gửi), toàn vẹn (không bị sửa đổi) và có thể kiểm tra được nguồn gốc file.
2. Kỹ thuật công nghệ sử dụng
Ngôn ngữ & Framework:
Python 3
Flask (web server)
Thư viện mã hóa: rsa (mã hóa bất đối xứng, tạo/kiểm tra chữ ký số)
Quản lý tài khoản & file:
Dùng file JSON (users.json) để lưu thông tin tài khoản, public key từng user
File hệ thống (thư mục uploads/) để lưu trữ file dữ liệu và chữ ký số
Tạo/kiểm tra chữ ký số:
Từng user tự sinh cặp khóa RSA (public/private)
Khi gửi file, dùng private key để ký số; bên nhận dùng public key của người gửi để kiểm tra chữ ký số
3. Các chức năng chính
Đăng ký
Đăng ký tài khoản với tên đăng nhập, mật khẩu, upload public key (public.pem)
Đăng nhập/đăng xuất
Gửi file
Chọn tài khoản người nhận
Upload file dữ liệu + file chữ ký số tương ứng (file ký bằng private key của người gửi)
Xem lịch sử gửi/nhận file
Hiển thị danh sách file đã gửi, đã nhận (phân biệt người gửi/người nhận)
Tải file, chữ ký về
Kiểm tra chữ ký số online
Bên nhận kiểm tra tính hợp lệ của chữ ký số trên web: hệ thống tự động lấy public key của người gửi để xác thực file
4. Giao diện người dùng
Đơn giản, dễ sử dụng:
Đăng ký, đăng nhập: Form nhập liệu đơn giản, upload file public key khi đăng ký
Gửi file:
Dropdown chọn tài khoản người nhậ
Upload file và file chữ ký số
Lịch sử gửi/nhận:
Hiển thị rõ ràng các file đã gửi, các file đã nhận (từ ai, gửi cho ai
Mỗi file đều có nút tải file/chữ ký, nút kiểm tra chữ ký s
Thông báo (success/fail) khi kiểm tra chữ ký số hiển thị trực tiếp trên giao diện
5. Hoạt động tổng thể của hệ thống
Từng người dùng tự tạo cặp khóa RSA trên máy cá nhân
Dùng rsa.newkeys để sinh public.pem (dùng đăng ký) và private.pem (dùng ký số, giữ bí mật)
Đng ký tài khoản
Nhập username, password, upload public.pem (server lưu lại để kiểm tra sau này)
Gửi file
Người gửi đăng nhập, chọn người nhận, upload file dữ liệu và chữ ký số (signature tạo từ private key
Server lưu file và chữ ký, ghi nhận người gửi/nhận
Người hận đăng nhập
Xem danh sách file mình nhận được (từ ai gửi)
Tải về hoặc kiểm tra chữ ký số ngay trên web (server sẽ tự lấy public key của người gửi để xác thực chữ ký số của file)
Kiểm tra chữ ký số
Nếu chữ ký hợp lệ: Hiển thị thông báo chữ ký số hợp lệ, file do đúng người gửi ký
Nếu không hợp lệ: Hiển thị thông báo chữ ký không hợp lệ hoặc file bị chỉnh sửa

Tải file/chữ ký

Người nhận, hoặc bất kỳ ai có quyền đều có thể tải file và chữ ký về để kiểm tra độc lập

Tóm tắt ưu điểm
Đảm bảo toàn vẹn & xác thực dữ liệu: Không ai có thể giả mạo người gửi hoặc chỉnh sửa file mà không bị phát hiện

Phân quyền gửi/nhận rõ ràng: Có thể kiểm tra ai gửi, ai nhận, truy vết giao dịch

Thao tác, kiểm tra chữ ký số dễ dàng ngay trên web
