# Quiz Platform API — FastAPI + MySQL

## Cài đặt

```bash
# 1. Tạo virtual environment
python -m venv venv
venv\Scripts\activate        # Windows CMD
# hoặc: source venv/bin/activate   (Mac/Linux)

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Tạo file .env
copy .env.example .env
# Mở .env và điền DB_PASSWORD, JWT_SECRET_KEY

# 4. Tạo database MySQL (chạy trong MySQL Workbench hoặc cmd)
# CREATE DATABASE quiz_platform CHARACTER SET utf8mb4;

# 5. Tạo bảng
python create_tables.py

# 6. Seed dữ liệu mẫu
python seed.py

# 7. Chạy server
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

---

## Tài khoản mẫu (sau khi seed)

| Email             | Password    | Role    |
|-------------------|-------------|---------|
| admin@quiz.vn     | admin123    | admin   |
| teacher@quiz.vn   | teacher123  | teacher |
| student@quiz.vn   | student123  | student |
| student2@quiz.vn  | student123  | student |

---

## API Endpoints

### Auth
| Method | Endpoint              | Mô tả       |
|--------|-----------------------|-------------|
| POST   | /api/v1/auth/register | Đăng ký     |
| POST   | /api/v1/auth/login    | Đăng nhập   |
| POST   | /api/v1/auth/logout   | Đăng xuất   |

### Users
| Method | Endpoint              | Mô tả              |
|--------|-----------------------|--------------------|
| GET    | /api/v1/users/me      | Thông tin bản thân |
| PATCH  | /api/v1/users/me      | Cập nhật thông tin |

### Courses
| Method | Endpoint                        | Mô tả             |
|--------|---------------------------------|-------------------|
| GET    | /api/v1/courses                 | Danh sách môn học |
| POST   | /api/v1/courses                 | Tạo môn học       |
| POST   | /api/v1/courses/{id}/enroll     | Ghi danh SV       |

### Quizzes
| Method | Endpoint                                  | Mô tả              |
|--------|-------------------------------------------|--------------------|
| GET    | /api/v1/quizzes                           | Danh sách đề       |
| POST   | /api/v1/quizzes                           | Tạo đề mới         |
| GET    | /api/v1/quizzes/{id}                      | Chi tiết đề        |
| PATCH  | /api/v1/quizzes/{id}                      | Cập nhật đề        |
| DELETE | /api/v1/quizzes/{id}                      | Xóa đề             |
| POST   | /api/v1/quizzes/{id}/questions            | Thêm câu hỏi       |
| PATCH  | /api/v1/quizzes/{id}/questions/{qid}      | Sửa câu hỏi        |
| DELETE | /api/v1/quizzes/{id}/questions/{qid}      | Xóa câu hỏi        |
| POST   | /api/v1/quizzes/{id}/sort                 | Sắp xếp câu hỏi   |

### Attempts
| Method | Endpoint                        | Mô tả           |
|--------|---------------------------------|-----------------|
| POST   | /api/v1/attempts/start          | Bắt đầu làm bài |
| POST   | /api/v1/attempts/{id}/submit    | Nộp bài         |
| GET    | /api/v1/attempts/{id}           | Chi tiết bài    |

### Results
| Method | Endpoint                              | Mô tả                    |
|--------|---------------------------------------|--------------------------|
| GET    | /api/v1/results                       | Thống kê tổng            |
| GET    | /api/v1/results/me                    | Kết quả bản thân (SV)    |
| GET    | /api/v1/results/students/{id}         | Kết quả 1 sinh viên      |
| GET    | /api/v1/results/quizzes/{id}/stats    | Thống kê theo đề         |
