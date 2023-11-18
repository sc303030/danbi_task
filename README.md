![python](https://img.shields.io/badge/python-3.11-blue)
![django](https://img.shields.io/badge/django-4.2.7-orange)
![Static djangorestframework](https://img.shields.io/badge/djangorestframework-3.14.0-red)
# 🚀 백엔드 개발 과제
**업무(Task)를 위한 API**
## 🔖 **사용 방법**
### 1️⃣ 가상환경 생성 & 패키지 설치
#### **Step 1: 가상환경 생성**
```python
python -m venv <가상환경이름>
```
- ex) `python -m venv venv`
#### **Step 2: 가상환경 실행**
```
# macOS / Linux
source <가상환경이름>/bin/activate

# Windows
<가상환경이름>\Scripts\activate
```
#### **Step 3: 가상환경 실행 후 requirements.txt 설치**
```
pip install -r requirements.txt
```
### 2️⃣ 객체 생성
- migrations과 migrate후 진행하기
#### **Step 1: Team 객체 생성**

- `User`모델이 team 필드를 가져야 하기에 먼저 `Team` 객체를 생성합니다.
```python
python manage.py create_team_object
```
#### **Step 2: User 객체 생성**
- 모든 API는 인증을 기본으로 하고 있습니다. 테스트를 위해 단비팀원과 다래 팀원을 생성합니다.
```python
python manage.py create_user_object
```
### 3️⃣ API 사용하기
#### **Step 1: API 문서 참고**
➡️ **[API 문서 보러가기](https://documenter.getpostman.com/view/14425036/2s9YXpWegq#4fb7658a-74bf-4a83-994b-60fd50b12ccb)**

### 4️⃣ 테스트
#### **Step 1: pytest 실행**
```python
pytest
```
- print 같이 출력하기
    ```python
  pytest -s
  ```
- 특정 파일만 실행
    ```python
  pytest task/tests/test_task.py
  ```
- 특정 함수만 실행
    ```python
  pytest task/tests/test_task.py::test_fail_authentication
  ```
