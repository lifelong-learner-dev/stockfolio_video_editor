# 타임라인
## 2024/08/06 
- ffmpeg 관련 공부
- 주요 기능 및 기능별 구현 구조 확립

- 테스트 진행시 
- id : admin
- 비번 : ***


## 2024년 8월 7일

- 프로젝트 환경 설정**
  - Django 프로젝트와 앱 생성
  - `djangorestframework`와 `drf-yasg`를 사용하여 API 개발 환경 구축
  - `djangorestframework-simplejwt`를 사용하여 JWT 인증 설정 완료

- 모델 및 시리얼라이저 설정**
  - `Video`, `TrimCommand`, `ConcatCommand` 모델 정의
  - 모델에 대한 시리얼라이저 작성 (`VideoSerializer`, `TrimCommandSerializer`, `ConcatCommandSerializer`, `VideoUploadSerializer`)

- API 엔드포인트 구현**
  - `VideoViewSet`을 생성하여 비디오 업로드, 트림, 병합, 다운로드 기능 구현
  - 파일 업로드를 위해 `MultiPartParser`와 `FormParser` 추가
  - Celery를 사용하여 비디오 트림 및 병합 작업을 비동기로 처리

- Swagger 설정 및 디버깅**
  - `swagger_auto_schema`를 사용하여 Swagger 문서화 개선
  - Swagger UI에서 파일 업로드가 작동하지 않는 문제 해결 시도
  - 멀티파트 폼 데이터 처리와 관련된 오류 수정
  - 로깅 설정 추가하여 디버깅 과정 중 유용한 정보를 출력

- 테스트 케이스 작성 및 실행**
  - Django `TestCase`를 사용하여 API 테스트 케이스 작성
  - JWT 인증과 관련된 테스트 구현
  - 비디오 업로드, 트림 및 다운로드 기능의 테스트 성공 확인

- 버그 수정 및 최종 테스트**
  - Celery 작업에서 발생하는 예외 처리 추가
  - `ConcatCommand`와 `TrimCommand` 실행 중 발생하는 문제 해결
  - 최종적으로 Swagger UI에서 모든 엔드포인트가 예상대로 작동하는지 확인

## 프로젝트 주요 성과
- Django와 DRF를 사용하여 기본적인 비디오 편집 API를 구현
- JWT를 활용한 인증 및 권한 관리
- Swagger를 통해 API 문서화 및 테스트 환경 제공
- Celery를 통한 비동기 작업 처리