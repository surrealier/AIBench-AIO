# ssook: AI 모델 추론/평가/분석/데이터 관리 올인원 데스크탑 툴킷

## 만들게 된 이유

비전 AI 하다 보면 모델 학습은 어떻게든 하는데, 그 이후가 진짜 문제다. 학습 끝나고 나면 이 모델이 진짜 잘 되는건지 확인해야 하잖아? 그래서 inference 돌려보고, mAP 계산하고, FP/FN 분석하고, confidence threshold 조절하고,, 이걸 매번 코드 짜서 하고 있었다.

근데 이게 한두 번이면 괜찮은데 모델 바꿀 때마다, 데이터셋 바꿀 때마다 반복하니까 너무,,, 비효율적이었다. 그리고 데이터셋 관리도 문제였다. YOLO 포맷을 COCO로 바꿔야 할 때도 있고, train/val/test 분할도 해야 하고, 클래스 매핑도 바꿔야 하고, 중복 이미지도 찾아야 하고,, 이런 것들을 전부 각각의 스크립트로 돌리고 있었음;;

그래서 이참에 하나로 다 합쳐버리자 싶어서 만들었다. **코드 한 줄 안 짜고** 모델 추론부터 평가, 분석, 데이터 관리까지 전부 할 수 있는 툴.

## 이게 뭔데

**ssook**은 ONNX 모델 기반의 올인원 데스크탑 툴킷이다. FastAPI 백엔드에 웹 UI를 올려서 브라우저에서 쓸 수 있다. pywebview 설치하면 네이티브 윈도우로도 뜬다.

쉽게 말하면 이런거다.

- 모델 올리고 영상/이미지 열면 실시간 추론 결과가 보임
- 모델 여러 개 올려서 mAP, Precision, Recall, F1 비교 가능
- FP/FN 자동 분류해서 어디서 틀렸는지 분석
- confidence threshold를 클래스별로 sweep해서 최적값 찾아줌 (PR curve도 그려줌)
- t-SNE / UMAP / PCA로 임베딩 시각화
- 벤치마크 돌려서 FPS, 레이턴시, CPU/GPU 사용량 측정
- 데이터셋 탐색, 분할, 포맷 변환, 클래스 매핑, 병합, 샘플링, 품질 검사 등등

**전부 하나의 창에서 된다.** 코드 필요 없음.

## 지원하는 모델

Detection은 YOLO v5/v8/v9/v11, CenterNet(Darknet), 커스텀 ONNX 다 된다. Classification은 2D 출력 ONNX, Segmentation은 C×H×W 출력 ONNX, CLIP은 이미지+텍스트 인코더 ONNX, Embedder는 feature extractor ONNX.

fixed-batch 모델(예: batch=4)도 자동 감지해서 처리한다. 이거 은근 귀찮은 부분인데 알아서 해줌.

## 주요 기능 좀 더 자세히

### 추론 & 평가

뷰어 탭에서 모델 올리고 영상이나 이미지 열면 바로 실시간 추론이 된다. 박스 두께, 라벨 크기, confidence threshold 같은건 설정 탭에서 조절 가능하고, 클래스별로 색상이나 두께도 따로 설정할 수 있다.

평가 탭에서는 모델 여러 개를 동시에 올려서 비교할 수 있다. mAP@50, mAP@50:95, Precision, Recall, F1 다 나온다. 모델 A/B 비교도 되는데, 같은 이미지에 두 모델 결과를 슬라이더로 왔다갔다 하면서 볼 수 있다.

### 분석

여기가 좀 핵심인데, 오탐/미탐 분석이 된다. FP/FN을 자동으로 분류해주고, 크기별(S/M/L), 위치별로 나눠서 보여준다. 어디서 틀리는지 한눈에 보임.

Confidence Optimizer는 클래스별로 threshold를 sweep해서 F1이 최대가 되는 지점을 찾아준다. 각 클래스별 PR curve도 그려주니까 어떤 threshold에서 precision/recall이 어떻게 변하는지 볼 수 있다. 이거 원래 매번 코드 짜서 했었는데 이제 버튼 하나로 됨.

임베딩 뷰어는 모델 타입 선택 없이 ONNX 세션을 직접 로드해서 임베딩을 추출한다. 그래서 아무 feature extractor ONNX나 넣으면 t-SNE/UMAP/PCA 2D scatter plot이 나온다.

임베더 평가에서는 폴더 구조(class_name/image.jpg)로 된 데이터셋을 넣으면 Retrieval@1, Retrieval@K, 코사인 유사도를 계산해준다. 이미지 여러 장 선택해서 유사도 행렬 비교하는 기능도 있다.

### 데이터 관리

이 부분이 은근 많이 쓰게 되는데, 탐색기에서 데이터셋을 로드하면 이미지별 박스 목록이 나온다. 더블클릭하면 바운딩 박스가 오버레이된 이미지가 크게 보인다. 보기 방식도 5가지가 있다.

- 파일 목록 (기본)
- 클래스 분포 — 박스 단위 (person이 10개면 10으로 카운트)
- 클래스 분포 — 이미지 단위 (person이 10개 있어도 1로 카운트)
- 박스 크기 분포 (Small/Medium/Large)
- 종횡비 분포

필터도 클래스 다중 선택이 되고, 박스 개수로 >=, =, <= 필터링도 된다. 예를 들어 "박스가 0개인 이미지만 보기" 이런게 가능함.

분할은 랜덤이랑 층화 분할(Stratified) 중에 선택할 수 있다. 비율을 0으로 설정하면 그 폴더는 건너뛴다. 예를 들어 train 0.8 / val 0.2 / test 0 이렇게 하면 test 폴더는 안 만들어짐.

포맷 변환은 YOLO ↔ COCO JSON ↔ Pascal VOC XML 배치 변환이 된다. 이거 D-Fine 학습할 때 COCO 포맷 변환하느라 고생했었는데,, 그때 이게 있었으면 좋았을텐데 싶다.

클래스 매핑, 데이터셋 병합, 스마트 샘플링, 라벨 이상 탐지, 이미지 품질 검사, 근접 중복 탐지, 누수 분할 탐지 등등 전부 있다. 그리고 이것들 전부 하위 폴더 포함(Recursive) 옵션이 있어서 폴더 구조가 복잡해도 된다.

병합할 때는 dHash로 중복 탐지를 하는데, dHash는 이미지의 지각적 해시(perceptual hash)다. threshold 값이 낮을수록 더 유사한 이미지만 중복으로 판단한다. 0이면 완전 동일, 10이 기본값, 64가 최대.

### 기타

벤치마크는 FPS, 레이턴시(P50/P95/P99), CPU/GPU 사용량을 측정해주고 시스템 정보 export도 된다. 세그멘테이션 평가는 mIoU, mDice, 클래스별 IoU/Dice. CLIP Zero-Shot은 이미지+텍스트 인코더 올려서 zero-shot classification 평가. 배치 추론은 폴더 통째로 넣으면 YOLO txt / JSON / CSV로 export. 증강 미리보기는 Mosaic, flip, rotate, Albumentations 적용 전에 미리 볼 수 있다.

## 설치 & 실행

릴리즈에서 exe 받으면 Python 없이도 된다. Windows는 msi 설치 파일이나 zip 포터블, macOS는 dmg.

소스에서 돌리려면 Python 3.10+ 필요하고,

```bash
git clone https://github.com/surrealier/ssook.git
cd ssook
pip install -r requirements-web.txt
python run_web.py
```

이러면 끝이다. `--port 9000`으로 포트 바꿀 수도 있고, `--browser`로 브라우저 모드 강제할 수도 있다.

GPU 가속 쓰려면 `pip install onnxruntime-gpu` 하면 되는데, DirectML로 통일하고 싶으면 `onnxruntime-directml`을 쓰면 된다. 다만 DirectML은 CUDA 대비 80~90% 수준이라 성능 차이가 좀 있긴 하다..

## 한/영 지원

한국어/영어 전환이 된다. 사이드바에서 언어 바꾸면 UI 전체가 바뀜. i18next 같은 라이브러리 안 쓰고 자체 구현했는데, 문자열 150개 수준에 2개 언어라서 굳이 외부 라이브러리 쓸 필요가 없었다.

## 마무리

비전 AI 하면서 매번 반복하던 작업들을 하나로 합쳐놓은거다. 모델 평가할 때마다 스크립트 짜고, 데이터셋 정리할 때마다 코드 복붙하고,, 이런거 안 해도 된다. 그냥 열고 클릭하면 됨.

GitHub: https://github.com/surrealier/ssook
