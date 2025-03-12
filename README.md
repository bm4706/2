# 🌐 Django 커뮤니티 프로젝트

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)

Django 프레임워크를 사용하여 구현한 커뮤니티 웹 애플리케이션입니다. 사용자 관리, 게시글 작성, 댓글, 좋아요, 팔로우 등 다양한 소셜 기능을 포함하고 있습니다.


## 📋 목차

- [구현 기능](#-구현-기능)
- [개발 타임라인](#-개발-타임라인)
- [기여자](#-기여자)

## ✨ 구현 기능

### 👤 사용자 관리 (Users 앱)

#### 회원가입 및 인증
- **커스텀 사용자 모델**: `AbstractBaseUser`를 상속받아 이메일 기반 로그인 구현
- **회원가입**: 이메일, 닉네임, 비밀번호를 입력받아 사용자 등록
- **로그인/로그아웃**: Django 인증 시스템 활용
- **이메일 인증**: 랜덤 코드 생성 및 이메일 발송, 인증 처리

#### 프로필 관리
- **프로필 정보 조회**: 사용자 정보, 작성 게시글, 작성 댓글 확인
- **프로필 정보 수정**: 닉네임, 프로필 이미지 변경
- **비밀번호 변경**: 기존 비밀번호 확인 후 변경
- **비밀번호 재설정**: 이메일 인증을 통한 비밀번호 재설정 기능

#### 계정 관리
- **회원 탈퇴**: 비밀번호 확인 후 계정 삭제

### 📝 게시글 관리 (Posts 앱)

#### 게시글 CRUD
- **게시글 목록**: 최신순 정렬, 검색 기능
- **게시글 상세**: 제목, 내용, 작성자, 작성일 표시
- **게시글 작성**: 제목, 내용 입력
- **게시글 수정/삭제**: 작성자 권한 확인

#### 댓글
- **댓글 작성**: 게시글에 댓글 추가
- **댓글 목록**: 게시글별 댓글 표시

#### 좋아요/싫어요
- **GenericForeignKey 활용**: 게시글, 댓글 모두에 적용 가능한 통합 모델
- **좋아요/싫어요 토글**: 중복 방지 (한 번 더 클릭 시 취소)
- **개수 표시**: 게시글과 댓글의 좋아요/싫어요 개수 표시

### 🔍 검색 기능

- **통합 검색**: 제목, 내용, 작성자를 포함한 전체 검색
- **세부 검색**: 제목만, 내용만, 작성자만 검색 가능
- **검색 결과 표시**: 검색어, 검색 유형, 결과 개수 표시

### 👥 팔로우/팔로잉 기능

- **팔로우/언팔로우**: 다른 사용자 팔로우 및 취소
- **팔로워 목록**: 나를 팔로우하는 사용자 목록
- **팔로잉 목록**: 내가 팔로우하는 사용자 목록
- **프로필 연동**: 프로필에서 팔로워/팔로잉 수 표시
- **게시글 연동**: 게시글 상세 페이지에서 작성자 팔로우 가능

## 📅 개발 타임라인

### 2025년 2월
- **2월 24일**: 
  - 회원 탈퇴 기능 구현
  - 게시판 기능 구현
- **2월 25일**: 댓글 기능 및 좋아요/싫어요 기능 구현
- **2월 27일**: 개인 작성글 및 댓글 확인 기능 구현
- **2월 28일**: 비밀번호 재설정 기능 구현

### 2025년 3월
- **3월 4일**: 게시글 검색 기능 구현
- **3월 5일**: 팔로우/팔로잉 기능 구현
- **3월 6일**: 
  - 팔로우 리스트 뷰 추가
  - README 작성 및 수정
- **3월 10일**: 네비게이션바 구현
- **3월 11일**: 게시글 이미지 업로드 기능 구현
- **3월 12일**: 북마크 기능 구현

## 👨‍💻 기여자

- 조호진 - 기본 기능 구현 및 백엔드(Django) 개발

## 📞 문의

질문이나 제안이 있으시면 이슈를 열거나 다음 연락처로 문의해 주세요:
- 이메일: bm4706@gmail.com