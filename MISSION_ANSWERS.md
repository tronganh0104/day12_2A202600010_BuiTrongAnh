# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Các anti-pattern tìm được

Trong file `01-localhost-vs-production/develop/app.py`, em tìm được nhiều hơn 5 vấn đề:

1. `OPENAI_API_KEY` bị hardcode trực tiếp trong source code.
2. `DATABASE_URL` cũng bị hardcode và còn chứa cả username/password.
3. Các cấu hình như `DEBUG`, `MAX_TOKENS` đặt thẳng trong code thay vì lấy từ environment variables.
4. Ứng dụng log ra secret qua dòng `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")`.
5. Sử dụng `print()` thay vì logging chuẩn, nên khó theo dõi trên môi trường production.
6. Không có endpoint `/health` để kiểm tra liveness.
7. Không có endpoint `/ready` để kiểm tra readiness.
8. Server bind vào `localhost` nên không nhận được kết nối từ container hoặc cloud platform.
9. Port bị cố định là `8000`, không đọc từ biến môi trường `PORT`.
10. `reload=True` luôn bật, đây là chế độ chỉ phù hợp cho development.
11. Không có graceful shutdown hoặc xử lý tín hiệu `SIGTERM`.
12. Endpoint `/ask` nhận `question: str` trực tiếp, không có validate request body theo JSON schema rõ ràng.

### Exercise 1.2: Nhận xét khi chạy bản basic

Bản basic vẫn chạy được trên máy local và trả về kết quả khi gọi API, nên nhìn qua có vẻ là ổn.

Tuy nhiên, bản này chưa production-ready vì làm lộ secrets, phụ thuộc vào cấu hình chỉ phù hợp trên máy local, không có health check, logging yếu, và không xử lý shutdown an toàn khi nền tảng deploy cần restart service.

### Exercise 1.3: Bảng so sánh basic và advanced

| Feature | Basic | Advanced | Tại sao quan trọng? |
|---------|-------|----------|---------------------|
| Config | Hardcode trong source code | Đọc từ environment variables qua `config.py` | Giúp cùng một codebase chạy được ở dev, staging và production mà không cần sửa code. |
| Secrets | API key và database URL viết trực tiếp trong code | Secrets lấy từ environment variables | Tránh lộ thông tin nhạy cảm trong Git, log hoặc khi chia sẻ mã nguồn. |
| Host binding | `localhost` | `0.0.0.0` | Cho phép ứng dụng nhận request từ bên ngoài container hoặc từ cloud platform. |
| Port | Cố định `8000` | Đọc từ biến môi trường `PORT` | Cần thiết vì Railway, Render và nhiều platform tự cấp port khi deploy. |
| Debug mode | `reload=True` luôn bật | Chỉ reload khi `DEBUG=true` | Tránh hành vi debug không an toàn và giảm overhead trong production. |
| Health check | Không có `/health` | Có `/health` | Giúp platform biết service còn sống để tự động restart khi cần. |
| Readiness | Không có `/ready` | Có `/ready` | Giúp load balancer chỉ gửi traffic khi ứng dụng đã sẵn sàng. |
| Logging | Dùng `print()` và log cả secret | Logging JSON có cấu trúc, không làm lộ secret | Dễ theo dõi, tìm kiếm và gom log trên môi trường production. |
| Shutdown | Tắt đột ngột | Graceful shutdown qua lifespan và `SIGTERM` | Cho phép request đang xử lý hoàn tất trước khi service tắt. |
| Validation | Validate rất ít | Kiểm tra request body và trả `422` nếu thiếu dữ liệu | Giảm lỗi đầu vào và làm API rõ ràng hơn. |
| CORS | Không cấu hình | Có middleware CORS cấu hình được | Quan trọng khi frontend gọi API từ trình duyệt. |
| Observability | Gần như chỉ có endpoint gốc | Có `/health`, `/ready`, `/metrics` và startup logs | Hỗ trợ monitoring, debugging và vận hành production tốt hơn. |

### Checkpoint 1

- Hardcode secrets rất nguy hiểm vì có thể làm lộ thông tin qua Git commit, log, ảnh chụp màn hình hoặc khi chia sẻ mã nguồn.
- Environment variables giúp cùng một ứng dụng dùng lại được ở nhiều môi trường khác nhau mà không cần sửa code.
- Health check endpoint giúp nền tảng deploy phát hiện service bị lỗi hoặc không còn hoạt động để tự restart.
- Graceful shutdown là cơ chế giúp ứng dụng nhận tín hiệu tắt, ngừng nhận request mới và cho các request đang chạy hoàn thành an toàn.

## Part 2: Docker Containerization

### Exercise 2.1: Dockerfile cơ bản

1. Base image là `python:3.11`.
2. Working directory là `/app`.
3. `COPY requirements.txt` trước để tận dụng Docker layer cache. Nếu source code thay đổi nhưng dependencies chưa đổi thì Docker không cần cài lại toàn bộ packages, giúp build nhanh hơn.
4. `CMD` là lệnh mặc định khi container start và có thể bị ghi đè dễ dàng khi chạy `docker run`. `ENTRYPOINT` thường dùng để cố định executable chính của container, còn `CMD` hay được dùng để truyền default arguments hoặc default command.

### Exercise 2.2: Build và run

Em đã kiểm tra môi trường và xác nhận máy có cài Docker CLI:

- Docker version: `29.4.0`
- Docker Compose version: `v5.1.1`

Ban đầu Docker daemon chưa chạy, nhưng sau khi mở Docker Desktop thì em đã build và run được bản `develop`.

Các lệnh đã chạy:

```bash
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker run -p 8000:8000 my-agent:develop
```

Kết quả thực tế:

- Build thành công image `my-agent:develop`
- Kích thước image: `1.66GB`

Test endpoint thực tế:

```bash
GET /            -> 200 OK
GET /health      -> 200 OK
POST /ask        -> 422 Unprocessable Entity (nếu gửi JSON body như tài liệu)
POST /ask?question=What%20is%20Docker%3F -> 200 OK
```

Response thực tế:

- `GET /` trả về: `{"message":"Agent is running in a Docker container!"}`
- `GET /health` trả về: `{"status":"ok","uptime_seconds":23.9,"container":true}`
- `POST /ask?question=What%20is%20Docker%3F` trả về câu trả lời hợp lệ từ mock agent

Nhận xét:

- Bản `develop` chạy được trong Docker.
- Tuy nhiên câu lệnh test trong tài liệu đang chưa khớp với code thực tế, vì code nhận `question` qua query parameter chứ không phải JSON body. Khi gửi JSON body sẽ bị lỗi `422`.

### Exercise 2.3: Multi-stage build

- Stage 1 (`builder`) dùng để cài dependencies và build các package cần công cụ biên dịch như `gcc`, `libpq-dev`.
- Stage 2 (`runtime`) chỉ giữ lại những gì cần để chạy ứng dụng, gồm Python slim, packages đã cài và source code.
- Image nhỏ hơn vì stage runtime không mang theo build tools, cache, và các thành phần chỉ phục vụ lúc build.

Ngoài ra, bản advanced còn có các điểm production tốt hơn:

- Dùng `python:3.11-slim` thay vì image Python đầy đủ
- Tạo `non-root user` để chạy container an toàn hơn
- Có `HEALTHCHECK`
- Chạy `uvicorn` với `--workers 2`

Khi build thử thực tế, repo hiện tại có một số điểm chưa khớp:

1. `02-docker/production/Dockerfile` yêu cầu file `02-docker/production/requirements.txt`, nhưng thư mục này hiện không có file đó.
2. `docker-compose.yml` trong `02-docker/production` dùng `build.context: .`, nghĩa là context là chính thư mục `production/`, nhưng Dockerfile lại `COPY 02-docker/production/...`, nên đường dẫn copy này không khớp với build context của Compose.

Lỗi build thực tế của bản advanced là:

`COPY 02-docker/production/requirements.txt .` -> `not found`

Vì vậy, theo trạng thái hiện tại của repo, bản advanced cần sửa lại trước khi build thành công.

### Exercise 2.4: Docker Compose stack

Kiến trúc của stack trong `02-docker/production/docker-compose.yml` gồm 4 service:

1. `agent`: ứng dụng FastAPI chính
2. `redis`: cache/session store, có thể dùng cho rate limiting hoặc lưu trạng thái tạm
3. `qdrant`: vector database phục vụ RAG
4. `nginx`: reverse proxy và load balancer đứng phía trước

Luồng giao tiếp:

- Client gọi vào `nginx`
- `nginx` chuyển request đến `agent`
- `agent` có thể kết nối tới `redis`
- `agent` có thể kết nối tới `qdrant`

Sơ đồ đơn giản:

```text
Client
  |
  v
Nginx
  |
  v
Agent
 /   \
v     v
Redis Qdrant
```

Vai trò của từng service:

- `nginx` nhận traffic từ ngoài vào cổng `80/443`, thêm security headers, rate limiting và proxy request
- `agent` xử lý API `/ask`, `/health`
- `redis` lưu cache hoặc session tạm thời
- `qdrant` lưu vector embeddings cho truy vấn ngữ nghĩa

Theo file compose:

- `agent` phụ thuộc vào `redis` và `qdrant` qua `depends_on`
- `nginx` phụ thuộc vào `agent`
- Tất cả service giao tiếp qua network nội bộ `internal`
- `redis_data` và `qdrant_data` là volumes để lưu dữ liệu bền vững

### Checkpoint 2

- Em hiểu cấu trúc cơ bản của Dockerfile: chọn base image, đặt working directory, copy dependencies, cài packages, copy source code, expose port và chạy lệnh khởi động.
- Em hiểu lợi ích của multi-stage build là giảm kích thước image và tách môi trường build khỏi môi trường runtime.
- Em hiểu Docker Compose dùng để orchestration nhiều service cùng lúc như app, cache, database và reverse proxy.
- Em biết cách debug container bằng các lệnh như `docker logs <container>`, `docker exec -it <container> sh`, `docker ps`, `docker compose ps`.

## Part 3: Cloud Deployment

### Exercise 3.1: Deploy Railway

Thư mục `03-cloud-deployment/railway` được chuẩn bị để deploy lên Railway khá nhanh. Từ các file trong repo, em xác định được:

- Ứng dụng đọc port từ biến môi trường `PORT` bằng `os.getenv("PORT", 8000)`, đây là yêu cầu quan trọng vì Railway tự inject port khi chạy.
- File `railway.toml` dùng `builder = "NIXPACKS"`, nghĩa là Railway sẽ tự nhận diện project Python và build mà không cần Dockerfile riêng.
- `startCommand` là:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

- Railway dùng `healthcheckPath = "/health"` để kiểm tra service còn hoạt động hay không.
- `restartPolicyType = "ON_FAILURE"` và `restartPolicyMaxRetries = 3` cho phép tự restart khi app crash.

Các biến môi trường cần set tối thiểu theo hướng dẫn:

- `PORT=8000`
- `AGENT_API_KEY=my-secret-key`

Ngoài ra, trong thực tế có thể cần thêm:

- `ENVIRONMENT=production`
- `OPENAI_API_KEY` nếu dùng model thật thay vì mock

Trạng thái thực tế:

- Em đã đọc và phân tích cấu hình Railway trong repo
- Chưa deploy thật lên Railway vì bước này cần tài khoản Railway, đăng nhập CLI và mạng ngoài
- Vì vậy hiện chưa có public URL thực tế để test bằng `curl`

### Exercise 3.2: Deploy Render

So sánh `render.yaml` với `railway.toml`:

**Giống nhau**

- Đều khai báo cách chạy ứng dụng trên cloud
- Đều có cấu hình start command
- Đều có health check
- Đều cần environment variables để chạy production an toàn

**Khác nhau**

1. `railway.toml` ngắn gọn hơn, tập trung vào build/deploy của một service chính.
2. `render.yaml` chi tiết hơn và mang tính Infrastructure as Code rõ hơn, vì có thể khai báo nhiều service trong cùng một file.
3. `render.yaml` cho phép mô tả luôn cả Redis service, region, pricing plan, auto deploy và env vars trong một cấu hình YAML.
4. Render gắn chặt với mô hình “Blueprint”, tức là đọc repo GitHub rồi tạo hạ tầng từ `render.yaml`.
5. Railway thường nhanh cho MVP/demo, còn Render cho cảm giác cấu hình hạ tầng rõ ràng hơn khi có nhiều thành phần đi kèm.

Những điểm quan trọng trong `render.yaml`:

- `type: web` cho service chính
- `runtime: python`
- `buildCommand: pip install -r requirements.txt`
- `startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT`
- `healthCheckPath: /health`
- `autoDeploy: true`
- Có thể khai báo Redis ngay trong cùng file bằng `type: redis`

Nhận xét:

- `render.yaml` mang tính khai báo hạ tầng đầy đủ hơn
- `railway.toml` đơn giản và nhanh hơn cho người mới bắt đầu

### Exercise 3.3: (Optional) GCP Cloud Run

Sau khi đọc `cloudbuild.yaml` và `service.yaml`, em hiểu pipeline CI/CD của Cloud Run như sau:

1. Chạy test trước bằng Python 3.11
2. Build Docker image và gắn tag theo commit SHA và `latest`
3. Push image lên Google Container Registry
4. Deploy image đó lên Cloud Run bằng `gcloud run deploy`

Ý nghĩa của từng file:

- `cloudbuild.yaml` mô tả pipeline CI/CD tự động
- `service.yaml` mô tả cấu hình service trên Cloud Run theo kiểu IaC

Những điểm production quan trọng em thấy trong cấu hình Cloud Run:

- `min-instances=1` để giảm cold start
- `max-instances=10` để giới hạn scale
- cấu hình CPU, RAM, timeout rõ ràng
- secrets được lấy từ Secret Manager thay vì hardcode
- có `livenessProbe` và `startupProbe`
- `containerConcurrency: 80` cho phép một instance xử lý nhiều request đồng thời

Điều này cho thấy Cloud Run phù hợp hơn cho production vì:

- có CI/CD rõ ràng
- quản lý secrets tốt hơn
- hỗ trợ autoscaling chi tiết
- có health checks và resource limits đầy đủ

### Checkpoint 3

- Em đã hiểu cách deploy cơ bản lên Railway, Render và Cloud Run thông qua các file cấu hình trong repo.
- Em hiểu cách set environment variables trên cloud và vì sao không được hardcode secrets.
- Em hiểu vai trò của health check, restart policy và public URL khi deploy dịch vụ.
- Em hiểu cách xem logs theo từng nền tảng: Railway logs qua CLI/dashboard, Render logs trên dashboard, Cloud Run logs qua Google Cloud Logging.

Lưu ý:

- Part 3 hiện mới hoàn thành ở mức đọc hiểu và phân tích cấu hình từ repo.
- Chưa deploy thật lên ít nhất 1 platform vì cần tài khoản cloud, đăng nhập và public URL thực tế.
