# frontend

## 📁 프로젝트 구조
```sh
singleton-bungleton/
├── frontend/           # Vue 3 + TypeScript + Vite
│   ├── node_modules/   # npm으로 설치된 패키지, 모듈과 같은 3rd party 라이브러리가 모여있는 디렉터리
│   ├── public/         # 정적 리소스
│   ├── src/            # 실제 개발 디렉터리
│   │   ├── assets/     # 이미지, 폰트 등의 어플리케이션에서 사용하는 파일들이 모여있는 디렉터리
│   │   ├── components/    # vue의 컴포넌트 파일 디렉터리
│   │   ├── views/         # 페이지 컴포넌트
│   │   ├── router/        # 라우팅 설정
│   │   ├── stores/        # Pinia 상태관리
│   │   ├── App.vue        # 최상위(Root) 컴포넌트 vue
│   │   └── main.ts        # 가장 먼저 실행되는 typescript 파일, Vue 인스턴스를 생성 및 mount 하는 역할
│   └── package.json
├── backend/           # FastAPI + Python
└── README.md
```
- 출처: https://logs-jejustone.tistory.com/12

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
# backend

## How to run
```sh
cd backend
venv\Scripts\activate  # 가상환경 활성화
uvicorn main:app --reload --port 8000 # --reload: 코드 변경 시 자동 재시작
# http://localhost:8000 접속
```

# Project

## Commit Message
```sh
<type>: <subject>
```

### Type
- feat : 새로운 기능 추가, 기존의 기능을 요구 사항에 맞추어 수정
- fix : 기능에 대한 버그 수정
- build : 빌드 관련 수정
- chore : 패키지 매니저 수정, 그 외 기타 수정 ex) .gitignore
- ci : CI 관련 설정 수정
- docs : 문서(주석) 수정
- style : 코드 스타일, 포맷팅에 대한 수정
- refactor : 기능의 변화가 아닌 코드 리팩터링 ex) 변수 이름 변경
- test : 테스트 코드 추가/수정
- release : 버전 릴리즈