# 별이 운세 릴스 매일 운영 절차 (2026-11-21 ~ 2026-12-04)

계정: @byeori.fortune_ (Windsor instagram, account 17841458138744444)
저장소: tjdwoqmdlqmdl-sketch/byeori-reels2 → 로컬 /home/claude/byeori-reels2 (없으면 `git clone --depth 1` 후 사용)
기획 문서(규칙 원본): claude.ai 프로젝트 문서 `claude/별이운세_릴스기획.md`

## 규칙
- **24시간 안에 3편**: 매일 08:00 / 12:30 / 21:00 (KST)
- 15초, 2027 정미년 신년운세 기반, 매번 새 주제 (plan/backlog.md에서 고르고 사용 표시)
- 첫 프레임부터 훅 문구 노출 (평균 시청 2~3초 → 이탈 방지)
- 엔딩: 팔로우 + 프로필 링크 유도 (kit 기본값), 캡션 CTA는 build_day.py가 자동으로 붙임
- 커버: 공통 템플릿 (cover.py), 핵심 요소는 가운데 3:4 안
- DM 유도 금지, 공포 조장 금지, "※ 재미로 보는 운세" 표기
- 사주 근거는 plan/backlog.md의 십성·합충 표를 따른다. 확신 없는 주장은 쓰지 않는다
- 게시가 끝난 영상(reels/<id>.mp4)은 저장소에서 삭제 (커버·posts json은 남김)

## 매일 22:30 운영 (예약 메시지로 실행)
1. **보고**: Windsor get_data (instagram)
   - 게시물: media_id, timestamp, media_type, media_views, media_reach, media_like_count, media_comments_count, media_saved, media_shares, media_reel_avg_watch_time (date_preset last_3dT)
   - 팔로워: followers_count / 댓글: comment_id, comment_text, comment_timestamp
   - 오늘 게시물 성과, 최고·최저 편, 평균 시청 시간, 팔로워 변화, 새 댓글 중 질문·불만·피드백, 게시 실패·오류를 SendUserMessage로 짧게 보고 + 내일 개선점 1~2개
   - 데이터는 Windsor 캐시라 몇 시간 늦을 수 있음을 감안
2. **기획**: 다음 날 3슬롯 중 비어 있는 슬롯 수만큼 backlog에서 주제 선택 (전날 성과가 좋은 유형 우선)
3. **제작**: plan/<다음날>.json 작성 → `cd kit && python3 -I build_day.py ../plan/<날짜>.json ..` (2개씩 병렬 가능: 4번째 인자로 id 지정)
   - 프레임 몇 장 뽑아 글자 넘침·겹침 확인
4. **업로드**: reels/ covers/ posts/ plan/ 커밋 후 `git -c push.negotiate=true push origin HEAD:main`
5. **게시 예약**: 슬롯마다 send_later (아래 게시 메시지 형식)
6. **문서 갱신**: backlog 사용 표시(push), 프로젝트 문서의 게시 계획 갱신
7. **다음 운영 예약**: 마지막 운영(12/03 22:30) 전까지 다음 날 22:30에 같은 운영 메시지 send_later. 12/04 22:30에는 2주 종합 보고만.

## 게시 메시지 형식 (send_later)
"[게시] posts/<id>.json 읽고 instagram create_video_post(video_url, cover_url, caption, share_to_feed true). cover_url 실패 시 cover_url 빼고 thumb_offset 1000. 게시 후 create_comment(json의 comment). 그다음 저장소에서 git rm reels/<id>.mp4 → 커밋 → push. 결과(media id 또는 오류)를 사용자에게 한 줄 보고."
