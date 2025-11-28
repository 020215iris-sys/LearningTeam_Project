# LearningTeam_Project
사용자 사진을 입력하면 Mediapipe로 눈동자와 피부 색을 추출하고, KNN ML을 이용해 계절별 퍼스널컬러를 예측 후, 그에 맞는 립 제품을 추천합니다.

# Python 버전
3.11.14
중복 설치 주의 & 설정 어려울 경우 파이썬 재설치 보다는 가상환경 사용 추천

# 설치 방법 
1. 프로젝트 클론 (PC에 복제)
2. 가상환경 생성 및 활성화
3. 라이브러리 설치(requirement.txt에 버전 정리 해둠) 
4. 설치 코드 pip install -r requirements.txt
5. 문제 시 주요 라이브러리만 설치 → pip install opencv-python numpy scikit-image mediapipe pandas

# 작업 방식
clone → branch → commit → pull → rebase(fetch) → push
콜라보레이터 권한으로 포크 없이 클론만으로 직접 풀리퀘스트 가능

# 참고 사항
- Repository 자체에 gitignore 룰 적용 완료　→　업로드 시 개인정보 파일은 자동 필터링(venv 등)
- 혹시 모르니 업로드 전에 .gitignore 파일 내부 리스트에 본인 파일포함 되어있는지 확인하고 업로드 할 것

