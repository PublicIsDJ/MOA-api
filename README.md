# PublicIs-Archive-web

# 가상환경 생성
```python
python -m venv venv
```

# 가상환경 활성화
| `MacOS` 기준
```python
source venv/bin/activate
```

| `window` 기준 
```python
.\venv\Scripts\activate
```

# 의존성 내보내기
| 패키지를 설치한 경우 아래 명령어 실행
```python
pip freeze > requirements.txt
```