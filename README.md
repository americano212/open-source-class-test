# FastAPI To-Do List

간단한 과제 제출용 To-Do List 앱입니다. FastAPI로 API와 화면을 같이 제공합니다.

## 프로젝트 구조

```text
FastApi_Todos/
├─ fastapi-app/
│  ├─ main.py
│  ├─ todo.json
│  ├─ requirements.txt
│  ├─ Dockerfile
│  └─ templates/
│     └─ index.html
└─ docker-compose.yml
```

## 로컬 실행

```bash
cd fastapi-app
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## Docker 실행

저장소 루트에서 아래 명령으로 컨테이너를 실행합니다.

```bash
docker compose up --build
```

실행 후 브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## 현재 기능

- 할 일 추가, 수정, 삭제
- 완료 상태 토글
- 전체/진행 중/완료 필터
- 전체, 완료, 진행 중 개수 요약

## 제출 이력

버전, 변경내역, 화면 캡처 누적 기록은 `docs/submission-history.md`에 정리합니다.
