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


## 2024년 8월 8일

### 비디오 병합 작업 요약

### 개요
이 문서는 Django 환경에서 Celery를 사용하여 FFmpeg로 비디오 파일을 병합하는 작업과 관련된 문제 해결을 위해 수행된 작업과 진단 단계를 요약

### 수행된 작업
- **비디오 병합**: 여러 가지 명령 옵션과 Python 스크립트를 사용하여 FFmpeg로 두 개의 MP4 비디오 파일을 병합하려고 시도

### 문제 해결 단계
1. **FFmpeg 명령어 검증**: 터미널에서 직접 FFmpeg 명령어를 실행하여 문법과 매개변수가 올바른지 확인하였습니다. 이는 Django 환경으로부터 문제를 분리하는 데 도움이 되었습니다.

2. **코드 조정**: 비디오 병합을 처리하는 Python 스크립트를 여러 차례 조정하여 모든 경로와 명령이 정확하게 설정되었는지 확인하였습니다.

3. **파일 속성 일관성**: 입력 비디오 파일이 코덱, 프레임 레이트, 해상도에서 일관성을 유지하도록 확인하여 병합 과정 중 문제를 방지하였습니다.

4. **명령줄 직접 테스트**: 스크립트 오류를 우회하고 기본 FFmpeg 기능이 예상대로 작동하는지 검증하기 위해 명령줄에서 직접 FFmpeg 명령어를 실행하였습니다.

5. **오류 처리 및 로깅 개선**: 디버깅 목적으로 보다 자세한 정보를 캡처하고 기록하기 위해 스크립트 내의 오류 처리 및 로깅을 개선했습니다.

## 사용된 FFmpeg 병합 명령어

ffmpeg -f concat -i input.txt -c copy output.mp4

# 직접 명령어 작성시 작동하였고 작동하였던 명령어를 통해 tasks.py 코드 수정
# 수정 후 작동 완료