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
- Chưa deploy thật lên Railway vì em chọn Render để hoàn thành Part 3
- Tuy nhiên app đang deploy trên Render dùng code từ thư mục `03-cloud-deployment/railway`, nên response vẫn ghi `platform: "Railway"`

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

Kết quả deploy thật:

- Platform đã deploy: Render
- Public URL: `https://ai-agent-iwug.onrender.com`
- Test `GET /health` thành công, trả về:
  `{"status":"ok","uptime_seconds":275.1,"platform":"Railway","timestamp":"2026-04-17T08:35:46.006008+00:00"}`
- Test `POST /ask` thành công, trả về:
  `{"question":"Hello from Render","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","platform":"Railway"}`

Kết luận:

- Em đã deploy thành công lên ít nhất 1 platform như yêu cầu của Checkpoint 3.
- Em đã có public URL hoạt động thật và test thành công từ bên ngoài.

## Part 4: API Security

### Exercise 4.1: API Key authentication

Trong file `04-api-gateway/develop/app.py`, API key được kiểm tra trong hàm `verify_api_key()`.

Cách hoạt động:

- Ứng dụng đọc key từ biến môi trường `AGENT_API_KEY`
- FastAPI dùng `APIKeyHeader(name="X-API-Key")` để lấy giá trị từ header
- Endpoint `/ask` gắn dependency `Depends(verify_api_key)` nên chỉ ai có key hợp lệ mới gọi được

Điều gì xảy ra nếu sai key:

- Nếu không gửi API key: trả về `401`
- Nếu gửi sai API key: trả về `403`

Rotate key như thế nào:

- Chỉ cần đổi giá trị của biến môi trường `AGENT_API_KEY`
- Sau đó restart service để service dùng key mới
- Không nên hardcode key trong source code vì sẽ khó rotate và dễ lộ thông tin nhạy cảm

Nhận xét:

- Đây là cách bảo vệ đơn giản, phù hợp cho internal API, MVP hoặc hệ thống ít người dùng
- Điểm yếu là không có phân quyền theo user, mọi client dùng chung một secret

### Exercise 4.2: JWT authentication (Advanced)

Trong `04-api-gateway/production/auth.py`, luồng JWT hoạt động như sau:

1. User gọi `POST /auth/token` với `username` và `password`
2. Hàm `authenticate_user()` kiểm tra tài khoản trong `DEMO_USERS`
3. Nếu hợp lệ, hàm `create_token()` tạo JWT chứa:
   - `sub`: username
   - `role`: vai trò user/admin
   - `iat`: thời điểm phát hành token
   - `exp`: thời điểm hết hạn token
4. Khi gọi `/ask`, client phải gửi:
   `Authorization: Bearer <token>`
5. Hàm `verify_token()` giải mã JWT, kiểm tra chữ ký và hạn dùng
6. Nếu token hợp lệ, server lấy được thông tin `username` và `role` để xử lý tiếp

Nếu token lỗi:

- Thiếu token: `401`
- Token hết hạn: `401`
- Token không hợp lệ: `403`

Ưu điểm của JWT:

- Stateless, không cần query database ở mỗi request
- Có thể nhúng role vào token để phân quyền
- Phù hợp hơn API key khi cần nhiều user với quyền khác nhau

### Exercise 4.3: Rate limiting

Trong `04-api-gateway/production/rate_limiter.py`, thuật toán được dùng là:

- `Sliding Window Counter`

Cách hoạt động:

- Mỗi user có một `deque` chứa timestamps của các request gần nhất
- Khi có request mới, hệ thống xóa các timestamp đã quá window 60 giây
- Nếu số request còn lại trong window đã đạt ngưỡng thì trả về `429 Too Many Requests`

Giới hạn hiện tại:

- User thường: `10 req/phút`
- Admin: `100 req/phút`

Bypass hoặc nới limit cho admin như thế nào:

- Ở `production/app.py`, hệ thống chọn limiter theo role:
  - `rate_limiter_user` cho user
  - `rate_limiter_admin` cho admin
- Vì vậy muốn bypass hoặc tăng limit cho admin thì sửa `rate_limiter_admin`
- Ví dụ: tăng `max_requests`, hoặc trong logic `ask_agent()` có thể bỏ qua bước `limiter.check()` nếu role là `admin`

Khi hit limit, response sẽ:

- trả `429`
- có `Retry-After`
- có các header như `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Exercise 4.4: Cost guard

Trong `04-api-gateway/production/cost_guard.py`, cost guard được thiết kế để tránh vượt ngân sách LLM.

Logic hiện tại:

- Mỗi user có budget theo ngày là `$1.0`
- Toàn hệ thống có global budget theo ngày là `$10.0`
- Hệ thống ước lượng chi phí dựa trên số input tokens và output tokens
- Trước khi gọi LLM, hàm `check_budget(user_id)` kiểm tra user còn budget hay không
- Sau khi gọi LLM xong, hàm `record_usage()` cộng usage vào bản ghi hiện tại

Nếu vượt budget:

- Vượt budget user: trả `402 Payment Required`
- Vượt budget toàn hệ thống: trả `503 Service temporarily unavailable`

Hệ thống cũng có cảnh báo:

- Khi user dùng vượt `80%` budget thì ghi warning log

Nếu implement theo yêu cầu đề bài `check_budget(user_id, estimated_cost)` với Redis, em sẽ làm như sau:

```python
import redis
from datetime import datetime

r = redis.Redis()

def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"

    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False

    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)
    return True
```

Giải thích:

- Mỗi user có một key riêng theo tháng
- Nếu cộng chi phí dự kiến mà vượt `$10/tháng` thì chặn
- Nếu chưa vượt thì cộng dồn chi phí và đặt thời gian sống cho key

### Checkpoint 4

- Em đã hiểu và đọc được cách implement API key authentication trong bản develop.
- Em đã hiểu luồng JWT authentication trong bản production, bao gồm login, tạo token và verify token.
- Em đã hiểu cách implement rate limiting bằng thuật toán sliding window.
- Em đã hiểu logic cost guard và cách có thể chuyển sang Redis để dùng trong production thực tế.

Lưu ý:

- Em đã xác minh phần lớn bằng cách đọc trực tiếp code trong repo.
- Việc chạy test local tự động bị vướng lỗi môi trường PowerShell khi khởi chạy background process, nên phần trả lời của Part 4 chủ yếu dựa trên phân tích code thay vì log test thực tế.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks

Trong `05-scaling-reliability/develop/app.py`, ứng dụng đã implement đủ 2 endpoint quan trọng:

1. `GET /health`
2. `GET /ready`

Ý nghĩa:

- `/health` là liveness probe, dùng để trả lời câu hỏi: tiến trình còn sống không?
- `/ready` là readiness probe, dùng để trả lời câu hỏi: instance đã sẵn sàng nhận traffic chưa?

Điểm em quan sát được trong code:

- `/health` trả về:
  - `status`
  - `uptime_seconds`
  - `version`
  - `environment`
  - `timestamp`
  - `checks`
- `/ready` kiểm tra biến `_is_ready`
- Nếu `_is_ready = False` thì trả `503`
- Nếu app đã startup xong thì trả `{"ready": True, "in_flight_requests": ...}`

Ngoài ra, `/health` còn kiểm tra memory thông qua `psutil` nếu package này có sẵn. Điều này tốt hơn kiểu health check quá đơn giản chỉ trả `{"status":"ok"}`.

### Exercise 5.2: Graceful shutdown

Phần graceful shutdown trong `develop/app.py` được làm theo 2 lớp:

1. Dùng `lifespan()` để xử lý startup và shutdown
2. Bắt tín hiệu `SIGTERM` và `SIGINT` bằng `signal.signal(...)`

Luồng shutdown:

- Khi app chuẩn bị tắt, `_is_ready` được đặt về `False`
- App ghi log `"Graceful shutdown initiated..."`
- App chờ các request đang xử lý hoàn tất thông qua biến `_in_flight_requests`
- Thời gian chờ tối đa là `30 giây`
- Sau đó log `"Shutdown complete"`

Như vậy, graceful shutdown giúp:

- không nhận thêm request mới trong lúc đang tắt
- cho request đang chạy hoàn tất trước khi process dừng
- giảm nguy cơ mất dữ liệu hoặc trả lỗi ngẫu nhiên khi redeploy

### Exercise 5.3: Stateless design

Trong `05-scaling-reliability/production/app.py`, ý tưởng chính là:

- không giữ session/conversation history trong memory của từng instance
- lưu session vào Redis để instance nào cũng đọc được

Tại sao cần stateless:

- Nếu chỉ lưu state trong RAM của một instance, request sau có thể đi vào instance khác và mất context
- Khi scale ngang nhiều instance, state nội bộ sẽ gây bug không nhất quán

Giải pháp trong code:

- `save_session()` lưu session vào Redis
- `load_session()` đọc session từ Redis
- `append_to_history()` thêm message vào history và lưu lại
- session có TTL mặc định là `3600 giây`

Nếu Redis không có:

- app fallback sang `_memory_store`
- nhưng code cũng ghi rõ đây là chế độ “not scalable”

Đây là một điểm rất đúng với production thực tế: app phải stateless, còn state phải được đưa ra hệ thống dùng chung như Redis hoặc database.

### Exercise 5.4: Load balancing

Trong `05-scaling-reliability/production/docker-compose.yml` và `nginx.conf`, kiến trúc load balancing là:

```text
Client -> Nginx -> Agent instances -> Redis
```

Vai trò từng thành phần:

- `nginx` là reverse proxy và load balancer
- `agent` là các instance xử lý request
- `redis` lưu session dùng chung

Điểm quan trọng em rút ra:

- `nginx.conf` khai báo `upstream agent_cluster`
- `proxy_pass http://agent_cluster`
- Nginx thêm header `X-Served-By` để dễ quan sát request đi vào upstream nào
- `proxy_next_upstream error timeout http_503` giúp retry sang upstream khác nếu instance lỗi

Trong `docker-compose.yml`, service `agent` được thiết kế để scale lên nhiều instance. Ý tưởng bài lab là chạy:

```bash
docker compose up --scale agent=3
```

Như vậy, traffic sẽ được phân phối qua nhiều instance thay vì dồn vào một tiến trình duy nhất.

### Exercise 5.5: Test stateless

File `05-scaling-reliability/production/test_stateless.py` dùng để chứng minh hệ thống vẫn giữ được session khi scale.

Kịch bản test:

1. Tạo session mới
2. Gửi 5 request liên tiếp cùng một `session_id`
3. Quan sát trường `served_by`
4. Lấy history của session ra để kiểm tra toàn bộ hội thoại

Ý nghĩa:

- Nếu `served_by` cho thấy nhiều instance khác nhau đã xử lý request, nhưng history vẫn đầy đủ
- thì chứng minh session không nằm trong RAM của một instance riêng lẻ
- mà đang được chia sẻ qua Redis

Đây chính là bằng chứng cho stateless design hoạt động đúng khi scale.

### Checkpoint 5

- Em hiểu vai trò của `GET /health` và `GET /ready`.
- Em hiểu graceful shutdown là quá trình ngừng nhận traffic mới và chờ request đang chạy hoàn tất trước khi tắt.
- Em hiểu vì sao stateless design quan trọng khi scale nhiều instance.
- Em hiểu vai trò của Redis trong việc lưu session dùng chung.
- Em hiểu cách Nginx load balance traffic qua nhiều agent instances.

Lưu ý:

- Part 5 hiện được hoàn thành chủ yếu bằng phân tích code trong repo.
- Em chưa chạy demo Docker scaling thật ở phần này.
- Ngoài ra, em thấy `docker-compose.yml` đang tham chiếu `05-scaling-reliability/advanced/Dockerfile`, nhưng trong thư mục hiện tại không có path đó. Nhiều khả năng repo còn một chỗ chưa đồng bộ, nên nếu muốn chạy demo thật thì cần sửa lại đường dẫn build trước.

## Part 6: Final Project

### Objective

Mục tiêu của Part 6 là xây dựng một production-ready AI agent, kết hợp toàn bộ các khái niệm đã học từ Part 1 đến Part 5 vào một project hoàn chỉnh.

Sau khi đọc thư mục `06-lab-complete`, em thấy project này đúng là phiên bản tổng hợp của toàn bộ lab, bao gồm:

- config theo nguyên tắc 12-factor
- API key authentication
- rate limiting
- cost guard
- health check và readiness check
- graceful shutdown
- logging có cấu trúc
- Docker multi-stage
- cấu hình deploy cho Railway và Render

Trong quá trình kiểm tra thực tế, em đã phát hiện và sửa 2 lỗi quan trọng để project final chạy được độc lập:

1. Thư mục `06-lab-complete` chưa có `utils/mock_llm.py`, nên app không import được khi chạy độc lập.
2. Middleware đang dùng `response.headers.pop("server", None)`, nhưng `MutableHeaders` không hỗ trợ `pop`, làm app lỗi ở runtime.

Sau khi bổ sung `utils/mock_llm.py` và sửa middleware, project final đã import và chạy test nội bộ thành công.

### Đánh giá theo requirements

#### Functional requirements

- Agent trả lời câu hỏi qua REST API: **Đạt**
- Support conversation history: **Chưa thể hiện đầy đủ**
- Streaming responses: **Không có, nhưng đây là optional**

Giải thích:

- `app/main.py` có endpoint `POST /ask` để nhận câu hỏi và trả lời
- Tuy nhiên project final hiện không lưu conversation history theo user/session như mô tả lý tưởng ở Part 5
- Vì vậy nếu chấm rất sát theo requirement “support conversation history” thì phần này chưa hoàn chỉnh bằng bản stateless demo ở Part 5

#### Non-functional requirements

- Dockerized với multi-stage build: **Đạt**
- Config từ environment variables: **Đạt**
- API key authentication: **Đạt**
- Rate limiting: **Đạt**
- Cost guard: **Đạt**
- Health check endpoint: **Đạt**
- Readiness check endpoint: **Đạt**
- Graceful shutdown: **Đạt**
- Stateless design (state trong Redis): **Chưa đạt hoàn toàn**
- Structured JSON logging: **Đạt**
- Deploy lên Railway hoặc Render: **Đạt về mặt cấu hình**
- Public URL hoạt động: **Có thể đạt nếu deploy thực tế từ thư mục này**

### Architecture

Kiến trúc hiện tại của `06-lab-complete` gần với mô hình sau:

```text
Client
  |
  v
FastAPI Agent
  |
  +-- API Key Authentication
  +-- Rate Limiting
  +-- Cost Guard
  +-- Health/Ready endpoints
  |
  v
Mock LLM / OpenAI

Docker Compose
  |
  +-- agent
  +-- redis
```

Điểm khác với kiến trúc lý tưởng trong đề:

- Compose hiện chỉ có `agent + redis`
- Không có Nginx load balancer ở final project này
- Code final cũng chưa thực sự dùng Redis để lưu state hội thoại

### Step-by-step analysis

#### Step 1: Project setup

Project đã có đầy đủ các file chính:

- `app/main.py`
- `app/config.py`
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.env.example`
- `.dockerignore`
- `railway.toml`
- `render.yaml`

#### Step 2: Config management

`app/config.py` đã làm tốt phần config management:

- đọc `HOST`, `PORT`, `ENVIRONMENT`, `DEBUG`
- đọc `OPENAI_API_KEY`, `LLM_MODEL`
- đọc `AGENT_API_KEY`, `JWT_SECRET`, `ALLOWED_ORIGINS`
- đọc `RATE_LIMIT_PER_MINUTE`
- đọc `DAILY_BUDGET_USD`
- đọc `REDIS_URL`

Ngoài ra còn có `validate()` để fail fast trong production nếu:

- `AGENT_API_KEY` vẫn là giá trị mặc định
- `JWT_SECRET` vẫn là giá trị mặc định

#### Step 3: Main application

`app/main.py` đã tích hợp hầu hết thành phần chính:

- request validation bằng Pydantic
- API key auth
- rate limiting
- cost guard
- structured JSON logging
- security headers
- CORS
- `/health`
- `/ready`
- `/metrics`
- graceful shutdown bằng `SIGTERM`

Điểm tốt:

- code khá rõ ràng và có tính production hơn nhiều phần trước
- `/metrics` được bảo vệ bằng API key
- readiness được điều khiển bởi lifecycle của app

#### Step 4: Authentication

Authentication đang dùng `X-API-Key` thay vì JWT trong project final.

Điều này vẫn hợp lý vì:

- đề yêu cầu API key authentication
- API key đơn giản hơn cho MVP và internal service

Tuy nhiên, README lại mô tả cả `auth.py` và `JWT`, trong khi thư mục final hiện không có `app/auth.py`. Vì vậy tài liệu mô tả và mã nguồn final chưa khớp hoàn toàn.

#### Step 5: Rate limiting

Rate limiting đã được implement trực tiếp trong `app/main.py` bằng cấu trúc:

- `defaultdict(deque)`
- xóa các request cũ ngoài cửa sổ 60 giây
- nếu vượt limit thì trả `429`

Điểm cần lưu ý:

- logic hoạt động đúng cho một instance
- nhưng đang là in-memory, nên nếu scale nhiều instance thì mỗi instance sẽ giữ limit riêng
- vì vậy đây chưa phải cách tốt nhất cho production phân tán

#### Step 6: Cost guard

Cost guard cũng được implement trực tiếp trong `app/main.py`:

- tính chi phí từ input/output tokens
- reset theo ngày
- chặn khi vượt `daily_budget_usd`

Điểm mạnh:

- có budget guard thật
- có endpoint `/metrics` để theo dõi usage

Điểm hạn chế:

- state chi phí đang lưu in-memory
- nếu restart app hoặc scale nhiều instance thì dữ liệu budget không còn đồng nhất

#### Step 7: Dockerfile

Dockerfile final làm khá tốt:

- multi-stage build
- dùng `python:3.11-slim`
- tạo non-root user
- copy dependency từ builder sang runtime
- có `HEALTHCHECK`
- chạy bằng `uvicorn`

Đây là một Dockerfile production-ready đúng tinh thần bài học.

#### Step 8: Docker Compose

`docker-compose.yml` hiện có:

- `agent`
- `redis`

Ưu điểm:

- có healthcheck cho agent và redis
- có `env_file`
- có `depends_on` theo tình trạng healthy

Hạn chế:

- `redis` mới chỉ được khai báo ở mức hạ tầng
- code final hiện chưa tận dụng Redis để làm stateless conversation state

#### Step 9: Test locally

Repo cung cấp script `check_production_ready.py` để tự đánh giá project cuối.

Trước đó, em đã chạy script này và kết quả là:

- `20/20 checks passed`
- `100%`
- trạng thái: `PRODUCTION READY`

Điều này cho thấy project final đạt tốt theo bộ tiêu chí kiểm tra tự động của repo.

Ngoài checker, em còn test nội bộ trực tiếp bằng `FastAPI TestClient` sau khi sửa lỗi runtime và thu được kết quả:

- `GET /health` trả `200 OK`
- `GET /ready` trả `200 OK` khi app đã chạy qua startup lifecycle
- `POST /ask` với API key hợp lệ trả về câu trả lời hợp lệ
- `GET /metrics` với API key hợp lệ trả về thống kê usage

Ví dụ kết quả thực tế:

- `/health`: trạng thái `ok`
- `/ready`: `{"ready": true}`
- `/ask`: trả về `question`, `answer`, `model`, `timestamp`
- `/metrics`: trả về `uptime_seconds`, `total_requests`, `error_count`, `daily_cost_usd`

Như vậy, phần final project không chỉ pass code checker mà còn hoạt động được ở mức endpoint chính sau khi sửa 2 lỗi runtime nêu trên.

#### Step 10: Deploy

Project final đã có sẵn:

- `railway.toml`
- `render.yaml`

Nghĩa là về mặt cấu hình, project sẵn sàng để deploy lên cloud.

### Kết luận tổng hợp

`06-lab-complete` là một project final tốt và gần như hoàn chỉnh để nộp bài, vì nó đã kết hợp được hầu hết các ý chính của cả lab:

- 12-factor config
- authentication
- rate limiting
- cost guard
- health/readiness
- graceful shutdown
- Docker multi-stage
- deploy config

Tuy nhiên, nếu đánh giá rất chặt theo mô tả lý tưởng của Part 6 thì vẫn còn vài điểm chưa khớp hoàn toàn:

1. Chưa có conversation history thực sự
2. Chưa dùng Redis để lưu state hội thoại
3. Rate limiting và cost guard vẫn là in-memory
4. README mô tả có `auth.py`, `rate_limiter.py`, `cost_guard.py`, nhưng code final đang gộp các phần đó vào `app/main.py`
5. Chưa có Nginx/load balancer trong final project

### Final assessment

Theo em, project final này:

- **Đủ tốt để nộp bài** theo tinh thần của lab
- **Đạt rất cao** nếu chấm theo checklist kỹ thuật tự động
- **Đã chạy được thực tế ở mức local verification**
- **Chưa hoàn hảo tuyệt đối** nếu chấm sát theo kiến trúc production phân tán đầy đủ

Nếu cần cải thiện để bài đẹp hơn trước khi nộp, em sẽ ưu tiên:

1. Tách `auth`, `rate_limiter`, `cost_guard` ra file riêng
2. Dùng Redis thật cho rate limiting và session state
3. Bổ sung conversation history
4. Cập nhật README để khớp với code hiện tại
