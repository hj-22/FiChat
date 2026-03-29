# FiChat


## 협업을 위한 Github Branch 규칙

효율적인 협업 경험과 사용 방식에 익숙해지기 위해 다음 사항을 지키도록 해 봅시다

### 1. 브랜치 구조
- `main`: 최종 배포용! (작동하는것만)
- `develop`: 기능 통합, 테스트용 (각자 작업물을 합치는 곳)
- `feat`: 각자 담당 기능 개발용
  - `feat/guranteed`: 보장형 @kchykchy
  - `feat/non-guranteed`: 비보장형 @foreverOyeong
  - `feat/ui-db`: @hj-22

### 2. 작업 프로세스

* 각자 코드 작성은 `feat/~` 아래에서 합니다 
  * Github Desktop 기준 current branch 누르면 New branch 만들 수 있음
  * based on ~ 은 `develop`으로 선택하고 이름을 `feature/(자기기능)` 으로 지으면 됩니다
* 작업 다 했으면 commit -> publish branch
* 깃허브로 돌아와서 pull request(아마 초록색 버튼 뜰 거임) 클릭
  * base: `develp`, compare: `feature/(작업한거)` 선택
  * create pull request -> merge pull request -> confirm merge
* 다됐으면 작업했던 `feature/~` 브랜치 삭제하고 Github Desktop에서도 삭제(우클릭하면 보임)
* `develop`브랜치로 돌아오면 브랜치 표시 옆 fetch origin -> pull origin 하면 됨
