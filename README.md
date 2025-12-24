# VoteWeb (투표 웹사이트)

Django와 Docker(MySQL)를 기반으로 한 관리자 승인형 투표 시스템입니다.
세련된 UX/UI (Deep Space & Neon Theme)와 보안 기능(Rate Limit)을 포함하고 있습니다.

## 🛠️ 필수 요구사항 (Prerequisites)

이 프로젝트를 실행하기 위해서는 다음 프로그램들이 설치되어 있어야 합니다.

1. **Git**: 소스 코드 다운로드용
2. **Python (3.8 이상)**: 서버 실행용
3. **Docker Desktop**: 데이터베이스(MySQL) 실행용
   - 설치 후 반드시 실행 상태여야 합니다.

## 🚀 빠른 시작 가이드 (Quick Start)

어떤 컴퓨터에서도 아래 명령어들을 순서대로 입력하면 바로 서버를 실행할 수 있습니다. (PowerShell 기준)

### 1. 프로젝트 다운로드
```powershell
git clone https://github.com/movingmin/Votedjango.git
cd Votedjango
```

### 2. 가상환경 생성 및 패키지 설치
```powershell
# 가상환경 생성
python -m venv venv

# 패키지 설치
venv\Scripts\pip install -r requirements.txt
```

### 3. 환경변수 설정 (.env)
기본 제공되는 예제 파일을 복사하여 환경변수 파일을 생성합니다.
(PowerShell 명령어)
```powershell
copy .env.example .env
```
필요하다면 `.env` 파일을 열어 `SECRET_KEY` 등을 변경할 수 있습니다.

### 4. 데이터베이스 실행
Docker가 켜져 있는지 확인하고 실행하세요.
```powershell
docker-compose up -d
```

### 5. 데이터베이스 초기화 (Migrations)
Django 모델을 기반으로 데이터베이스 테이블을 생성합니다.
```powershell
venv\Scripts\python manage.py makemigrations
venv\Scripts\python manage.py migrate
```

### 6. 관리자 계정 생성 (최초 1회)
이 명령어를 통해 `root` 관리자 계정(비밀번호: `rootword`)을 생성합니다.
```powershell
venv\Scripts\python create_superuser.py
```

### 7. 서버 실행
```powershell
venv\Scripts\python manage.py runserver
```

---

## ✅ 접속 및 사용 방법

- **웹사이트 접속**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **관리자 페이지**: [http://127.0.0.1:8000/root](http://127.0.0.1:8000/root)
    - **ID**: `root`
    - **PW**: `rootword`

### 주요 기능
1. **관리자 승인 투표**: 사용자가 회원가입하면 관리자가 승인(권한 부여)해야 투표 가능.
2. **실시간 메시지**: 로그인 실패, 투표 완료 등의 알림이 화면 상단에 토스트 메시지로 표시됨.
3. **보안**: 분당 로그인 20회, 투표 1회로 제한됨 (Rate Limit).
4. **외부 접속 (Cloudflare Tunnel)**: 로컬호스트를 안전하게 외부로 공유 가능.

## 🌐 외부 배포 (Cloudflare Tunnel)

포트 포워딩 없이 안전하게 외부에서 로컬 서버에 접속할 수 있는 방법입니다.
프로젝트 폴더에 포함된 `cloudflared-windows.exe`를 사용합니다.

1. **Django 서버 실행**
   먼저 웹 서버가 8000번 포트에서 실행 중이어야 합니다.
   ```powershell
   venv\Scripts\python manage.py runserver
   ```

2. **터널 실행 (새 터미널 창)**
   새로운 PowerShell 창을 열고 아래 명령어를 실행하세요.
   ```powershell
   .\cloudflared-windows.exe tunnel --url http://127.0.0.1:8000
   ```

3. **URL 확인**
   터널 실행 로그에 나오는 `trycloudflare.com` 링크를 복사하여 공유하면 됩니다.
   (예: `https://popular-example-domain.trycloudflare.com`)

## 🗄️ 데이터베이스 관리 (MySQL)

Docker 컨테이너로 실행되는 MySQL 데이터베이스에 접근하는 방법입니다.

### 1. 터미널 접속 (CLI)
```powershell
docker exec -it voteweb_db mysql -u voteuser -pvotepassword voteweb_db
```
접속 후 SQL 쿼리를 직접 실행할 수 있습니다.
```sql
SHOW TABLES;
SELECT * FROM core_vote;
```

### 2. GUI 도구 연결 (DBeaver, Workbench 등)
- **Host**: `127.0.0.1` (localhost)
- **Port**: `3306`
- **User**: `voteuser`
- **Password**: `votepassword`
- **Database**: `voteweb_db`

### 3. 데이터베이스 테이블 구조 (Schema)

핵심 테이블의 구조와 컬럼 정보입니다.

#### A. 사용자 정보 (`auth_user` + `core_profile`)
Django 기본 `auth_user` 테이블과 1:1로 연결된 `core_profile` 테이블이 있습니다.

| Table | Column | Type | Description |
|---|---|---|---|
| `auth_user` | `id` | Integer | Primary Key |
| | `username` | Varchar | 아이디 |
| | `password` | Varchar | 해싱된 비밀번호 |
| | `first_name` | Varchar | 사용자 실명 |
| | `is_superuser` | Boolean | 관리자 여부 (`1`: Root) |
| `core_profile` | `user_id` | Integer | `auth_user`와 FK 연결 |
| | `can_vote` | Boolean | 투표 권한 여부 (`1`: 승인됨, `0`: 미승인) |

#### B. 투표 내역 (`core_vote`)
실제 투표 정보가 저장되는 테이블입니다.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary Key |
| `candidate` | TextField | 투표한 후보자 이름 |
| `created_at` | DateTime | 투표 일시 |
| `user_id` | Integer | 투표한 사용자 (`auth_user` FK) |

#### C. 시스템 설정 (`core_systemconfig`)
전역 설정을 저장하며, `id=1`인 단일 행만 사용합니다.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary Key (Always 1) |
| `message` | TextField | 투표 화면 상단 메시지 (ex: "OOO 선거") |

## ⚠️ 문제 해결 (Troubleshooting)

**Q. CSS가 깨져서 나와요 (하얀 배경).**
A. 서버를 정지(`Ctrl+C`)하고 다시 실행해 보세요. 정적 파일 경로 설정이 업데이트되었습니다.

**Q. 로그인이 안 돼요.**
A. `create_superuser.py`를 실행했는지 확인하세요. 그래도 안 되면 `db` 컨테이너를 삭제하고 다시 시작해 보세요.
```powershell
docker-compose down -v
docker-compose up -d
venv\Scripts\python manage.py migrate
venv\Scripts\python create_superuser.py
```