# ssook — Future Works: Vision AI All-in-One 완성 로드맵

> 현재 ssook은 Object Detection 중심으로 개발되어 있으며, 진정한 Vision AI All-in-One 도구가 되기 위해 아래 기능들이 추가되어야 합니다.

---

## 1. 모델 태스크 확장

### 1.1 Object Tracking (MOT)
- **현황**: 미지원
- **필요 기능**:
  - ByteTrack, SORT, DeepSORT, BoT-SORT 등 트래커 통합
  - 비디오 입력 시 실시간 트래킹 오버레이 (ID 표시, 궤적 시각화)
  - 트래킹 평가 메트릭: MOTA, MOTP, IDF1, HOTA, ID Switch 수
  - Multi-Object Tracking 결과 내보내기 (MOTChallenge 포맷)

### 1.2 Pose Estimation (키포인트 검출)
- **현황**: 미지원
- **필요 기능**:
  - YOLO-Pose, HRNet, ViTPose 등 ONNX 모델 지원
  - 키포인트 + 스켈레톤 실시간 시각화
  - 평가 메트릭: OKS (Object Keypoint Similarity), PCK, AP
  - 키포인트별 정확도 히트맵
  - 포즈 비교 (A/B 모델)

### 1.3 Instance Segmentation 강화
- **현황**: Semantic Segmentation만 지원 (C×H×W 마스크)
- **필요 기능**:
  - YOLO-Seg, Mask R-CNN 등 인스턴스 세그멘테이션 모델 지원
  - 인스턴스별 마스크 오버레이 + 클래스 라벨
  - 평가 메트릭: Mask AP, Mask AR, 인스턴스별 IoU
  - Panoptic Segmentation 지원 (PQ, SQ, RQ 메트릭)

### 1.4 OCR (텍스트 검출 + 인식)
- **현황**: 미지원
- **필요 기능**:
  - Text Detection 모델 (CRAFT, DBNet 등 ONNX)
  - Text Recognition 모델 (CRNN, TrOCR 등 ONNX)
  - Detection + Recognition 파이프라인 연결
  - 검출된 텍스트 영역 시각화 + 인식 결과 오버레이
  - 평가 메트릭: Detection (IoU, Precision/Recall), Recognition (CER, WER, Accuracy)

### 1.5 Depth Estimation (단안 깊이 추정)
- **현황**: 미지원
- **필요 기능**:
  - MiDaS, Depth Anything 등 ONNX 모델 지원
  - 깊이맵 컬러맵 시각화 (viridis, plasma 등)
  - 원본 이미지와 깊이맵 나란히 비교
  - 상대/절대 깊이 스케일 조정

### 1.6 VLM (Vision-Language Model)
- **현황**: CLIP Zero-Shot만 지원, 범용 VLM 미지원
- **필요 기능**:
  - Visual Question Answering (VQA) — 이미지 + 질문 → 답변
  - Image Captioning — 이미지 → 설명 텍스트 생성
  - Visual Grounding — 텍스트 설명 → 이미지 내 영역 지정
  - Open-Vocabulary Detection (Grounding DINO 등) 지원
  - 멀티턴 대화형 이미지 분석

### 1.7 Image Generation / Diffusion
- **현황**: 미지원
- **필요 기능**:
  - Stable Diffusion, SDXL 등 ONNX 파이프라인 지원
  - Text-to-Image, Image-to-Image, Inpainting
  - 생성 결과 갤러리 + 프롬프트 히스토리
  - 생성 품질 메트릭: FID, CLIP Score

### 1.8 Video Understanding
- **현황**: 프레임 단위 Detection만 지원
- **필요 기능**:
  - Action Recognition (행동 인식) — 비디오 클립 분류
  - Temporal Action Detection — 시간 구간별 행동 검출
  - Video Classification 모델 지원
  - 비디오 요약 (key frame extraction)

### 1.9 Anomaly Detection (시각적 이상 탐지)
- **현황**: 라벨 이상 탐지만 지원 (Label Anomaly Detector)
- **필요 기능**:
  - 비지도 학습 기반 시각적 이상 탐지 (PatchCore, PaDiM 등)
  - 정상 이미지 학습 → 이상 영역 히트맵 시각화
  - 평가 메트릭: AUROC, AUPRO, F1-max
  - 산업용 결함 검출 시나리오 지원

### 1.10 Super Resolution
- **현황**: 미지원
- **필요 기능**:
  - ESRGAN, Real-ESRGAN 등 ONNX 모델 지원
  - 원본 vs 업스케일 비교 뷰어
  - 배율 선택 (2x, 4x, 8x)
  - 품질 메트릭: PSNR, SSIM, LPIPS

### 1.11 Face Detection & Recognition
- **현황**: 미지원
- **필요 기능**:
  - Face Detection (RetinaFace, SCRFD 등)
  - Face Landmark Detection (5점, 68점, 98점)
  - Face Recognition / Verification (ArcFace 등)
  - 평가 메트릭: TAR@FAR, ROC 곡선, 1:1 Verification, 1:N Identification

### 1.12 3D Vision
- **현황**: 미지원
- **필요 기능**:
  - Point Cloud 시각화 (3D 뷰어)
  - 3D Object Detection (PointPillars 등)
  - Stereo Depth Estimation
  - 3D BEV (Bird's Eye View) 시각화

### 1.13 Optical Flow
- **현황**: 미지원
- **필요 기능**:
  - RAFT, FlowNet 등 ONNX 모델 지원
  - 플로우 필드 시각화 (화살표, 컬러 코딩)
  - 비디오 프레임 간 모션 분석

---

## 2. 벤치마크 & 프로파일링 강화

### 2.1 태스크별 벤치마크 확장
- **현황**: Detection 중심 벤치마크 (FPS, Latency)
- **필요 기능**:
  - Classification 벤치마크 (throughput, batch별 latency)
  - Segmentation 벤치마크 (마스크 디코딩 시간 포함)
  - Pose Estimation 벤치마크
  - 각 태스크별 전처리/추론/후처리 단계 분리 측정

### 2.2 모델 프로파일링
- **현황**: 미지원
- **필요 기능**:
  - 레이어별 실행 시간 프로파일링 (ONNX Runtime profiling)
  - FLOPs / MACs 계산
  - 파라미터 수 표시
  - 메모리 사용량 프로파일링 (피크 메모리, 메모리 타임라인)
  - 병목 레이어 자동 식별 및 시각화

### 2.3 ONNX 모델 인스펙터
- **현황**: 미지원
- **필요 기능**:
  - 모델 그래프 시각화 (Netron 스타일)
  - Input/Output 텐서 shape, dtype 표시
  - Opset 버전, IR 버전 정보
  - 지원 EP (Execution Provider) 호환성 체크
  - 모델 메타데이터 표시

### 2.4 양자화 비교
- **현황**: 양자화 가이드 문서만 존재
- **필요 기능**:
  - FP32 vs FP16 vs INT8 모델 정확도/속도 자동 비교
  - 양자화 전후 정확도 드롭 시각화
  - 양자화 추천 (정확도 손실 허용 범위 기반)
  - 앱 내 양자화 실행 (ONNX quantization tool 통합)

### 2.5 멀티 디바이스 벤치마크
- **현황**: CPU/GPU 사용률 모니터링만 지원
- **필요 기능**:
  - CPU vs CUDA vs TensorRT vs OpenVINO vs DirectML 비교
  - NPU (Neural Processing Unit) 지원
  - 디바이스별 최적 배치 사이즈 자동 탐색
  - 디바이스 호환성 매트릭스 표시

### 2.6 에너지 효율 벤치마크
- **현황**: 미지원
- **필요 기능**:
  - 추론당 전력 소비 측정 (가능한 환경에서)
  - FPS/Watt 효율 지표
  - 엣지 디바이스 시뮬레이션 (리소스 제한 모드)

---

## 3. 데이터 관리 확장

### 3.1 어노테이션 도구 (라벨링)
- **현황**: 미지원 (외부 도구 필요)
- **필요 기능**:
  - Bounding Box 어노테이션 (드래그 & 드롭)
  - Polygon / Freehand 세그멘테이션 마스크 어노테이션
  - 키포인트 어노테이션
  - 클래스 라벨 관리 (추가/삭제/색상 지정)
  - 단축키 기반 빠른 라벨링 워크플로우
  - 어노테이션 히스토리 (Undo/Redo)

### 3.2 Auto-Labeling (자동 라벨링)
- **현황**: 미지원
- **필요 기능**:
  - 로드된 모델을 사용한 자동 라벨 생성
  - 자동 라벨 → 수동 검수 워크플로우
  - Confidence 기반 자동 라벨 필터링
  - SAM (Segment Anything Model) 통합 — 클릭/박스 기반 자동 세그멘테이션

### 3.3 Active Learning
- **현황**: 미지원
- **필요 기능**:
  - 불확실성 기반 샘플 추천 (라벨링 우선순위)
  - 모델 예측 엔트로피 시각화
  - 라벨링 → 재학습 → 재평가 루프 지원
  - 데이터 효율성 곡선 (라벨 수 vs 성능)

### 3.4 세그멘테이션 데이터 관리
- **현황**: Detection 포맷 변환만 지원 (YOLO ↔ COCO ↔ VOC)
- **필요 기능**:
  - 세그멘테이션 포맷 변환 (COCO Seg ↔ 마스크 이미지 ↔ Polygon JSON)
  - 마스크 시각화 + 편집
  - 인스턴스 세그멘테이션 데이터 탐색기
  - Panoptic 포맷 지원

### 3.5 키포인트 데이터 관리
- **현황**: 미지원
- **필요 기능**:
  - COCO Keypoint 포맷 지원
  - 키포인트 시각화 + 편집
  - 스켈레톤 정의 커스터마이징

### 3.6 비디오 어노테이션
- **현황**: 미지원
- **필요 기능**:
  - 프레임 단위 어노테이션
  - 트래킹 ID 할당 + 보간 (interpolation)
  - 시간 구간 라벨링 (Action Detection용)
  - 비디오 → 프레임 추출 + 자동 라벨링

### 3.7 데이터셋 버전 관리
- **현황**: 미지원
- **필요 기능**:
  - 데이터셋 스냅샷 / 버전 태깅
  - 버전 간 diff (추가/삭제/변경된 이미지 및 라벨)
  - 버전별 평가 결과 비교
  - DVC (Data Version Control) 연동 (선택적)

### 3.8 클래스 불균형 분석 & 리밸런싱
- **현황**: Smart Sampler에서 부분적 지원
- **필요 기능**:
  - 클래스별 샘플 수 / 박스 수 불균형 시각화
  - 자동 오버샘플링 / 언더샘플링 제안
  - 클래스 가중치 계산 (학습용 weight 파일 생성)
  - 불균형 해소 전후 분포 비교

### 3.9 데이터 증강 파이프라인
- **현황**: Augmentation Preview만 지원 (미리보기)
- **필요 기능**:
  - 증강 파이프라인 정의 → 실제 데이터셋 생성
  - 증강 결과 저장 (이미지 + 변환된 라벨)
  - 증강 전략 프리셋 (Detection용, Classification용, Segmentation용)
  - Copy-Paste Augmentation (인스턴스 세그멘테이션용)

### 3.10 멀티모달 데이터 지원
- **현황**: 이미지/비디오만 지원
- **필요 기능**:
  - 이미지 + 텍스트 페어 데이터 관리 (VLM/CLIP 학습용)
  - 이미지 + 캡션 데이터셋 탐색기
  - Point Cloud 데이터 로더 (3D Vision용)

---

## 4. 평가 & 분석 확장

### 4.1 Tracking 평가
- **현황**: 미지원
- **필요 기능**:
  - MOTA, MOTP, IDF1, HOTA 메트릭
  - ID Switch 시각화 (타임라인)
  - 트래킹 궤적 시각화 (전체 비디오)
  - GT 트래킹 데이터 로드 (MOTChallenge 포맷)

### 4.2 Pose Estimation 평가
- **현황**: 미지원
- **필요 기능**:
  - OKS (Object Keypoint Similarity) 기반 AP
  - PCK (Percentage of Correct Keypoints)
  - 키포인트별 정확도 히트맵
  - 예측 vs GT 스켈레톤 오버레이 비교

### 4.3 Cross-Domain 평가
- **현황**: 미지원
- **필요 기능**:
  - 도메인 시프트 분석 (학습 데이터 vs 테스트 데이터 분포 비교)
  - 환경별 성능 분석 (주간/야간, 실내/실외, 날씨 등)
  - 데이터 서브셋별 성능 브레이크다운

### 4.4 Robustness 테스트
- **현황**: 미지원
- **필요 기능**:
  - 이미지 corruption 테스트 (노이즈, 블러, 날씨 효과 등)
  - Corruption 수준별 성능 저하 곡선
  - Adversarial robustness 테스트 (기본적인 수준)
  - 입력 해상도별 성능 변화 분석

### 4.5 Fairness & Bias 분석
- **현황**: 미지원
- **필요 기능**:
  - 속성별 성능 분석 (객체 크기, 종횡비, 밀도 등)
  - 클래스 간 혼동 행렬 (Confusion Matrix) 시각화
  - 오분류 패턴 분석

### 4.6 모델 해석 (Explainability)
- **현황**: Tensor Heatmap만 지원
- **필요 기능**:
  - Grad-CAM / Grad-CAM++ 시각화
  - SHAP 기반 특성 중요도
  - Attention Map 시각화 (Transformer 기반 모델)
  - 클래스별 활성화 영역 비교

### 4.7 리포트 생성
- **현황**: CSV/Excel 내보내기만 지원
- **필요 기능**:
  - PDF/HTML 평가 리포트 자동 생성
  - 차트, 테이블, 샘플 이미지 포함
  - 커스텀 리포트 템플릿
  - 모델 카드 (Model Card) 생성

---

## 5. 인프라 & UX 개선

### 5.1 모델 허브 통합
- **현황**: 수동 모델 다운로드만 지원
- **필요 기능**:
  - ONNX Model Zoo 브라우저
  - Hugging Face Hub 연동 (ONNX 모델 검색 & 다운로드)
  - 인기 모델 원클릭 다운로드 (YOLOv8/v11, SAM, CLIP 등)
  - 모델 메타데이터 자동 파싱 (클래스 이름, 입력 크기 등)

### 5.2 모델 변환 도구
- **현황**: ONNX 모델만 지원, 변환 도구 없음
- **필요 기능**:
  - PyTorch (.pt) → ONNX 변환 (앱 내)
  - TensorFlow (.pb, SavedModel) → ONNX 변환
  - ONNX → TensorRT 엔진 변환
  - ONNX → OpenVINO IR 변환
  - 변환 옵션 (opset, dynamic axes, simplify)

### 5.3 실험 추적 (Experiment Tracking)
- **현황**: 미지원
- **필요 기능**:
  - 평가 실행 히스토리 자동 저장
  - 실험 간 비교 대시보드
  - 태그, 메모 기능
  - MLflow / W&B 연동 (선택적)

### 5.4 플러그인 시스템
- **현황**: 미지원
- **필요 기능**:
  - 커스텀 전처리/후처리 파이프라인 플러그인
  - 커스텀 메트릭 플러그인
  - 커스텀 시각화 플러그인
  - 플러그인 마켓플레이스 (커뮤니티)

### 5.5 원격 추론 (Remote Inference)
- **현황**: 로컬 추론만 지원
- **필요 기능**:
  - 원격 서버 연결 (SSH / REST API)
  - 클라우드 GPU 활용 추론
  - Triton Inference Server 연동
  - 분산 벤치마크 (여러 디바이스 동시 측정)

### 5.6 배치 처리 & 자동화
- **현황**: 부분적 지원
- **필요 기능**:
  - CLI 기반 배치 평가 (headless 모드)
  - 평가 파이프라인 스크립트 (YAML/JSON 정의)
  - 스케줄링 (주기적 자동 평가)
  - CI/CD 통합 (GitHub Actions 등에서 모델 평가)

### 5.7 다국어 지원 강화
- **현황**: 한국어/영어 부분 지원
- **필요 기능**:
  - 일본어, 중국어 등 추가
  - 커뮤니티 번역 기여 시스템

### 5.8 접근성 & 테마
- **현황**: 기본 테마만 지원
- **필요 기능**:
  - 다크/라이트 테마 전환
  - 고대비 모드
  - 키보드 네비게이션 완전 지원
  - 화면 리더 호환성

---

## 6. 우선순위 로드맵 (제안)

### Phase 1 — 핵심 태스크 확장 (High Priority)
| 기능 | 난이도 | 영향도 |
|------|--------|--------|
| Instance Segmentation 강화 | ★★☆ | ★★★ |
| Pose Estimation 지원 | ★★★ | ★★★ |
| Object Tracking (MOT) | ★★★ | ★★★ |
| VLM 확장 (VQA, Captioning) | ★★★ | ★★★ |
| ONNX 모델 인스펙터 | ★★☆ | ★★★ |
| 모델 프로파일링 | ★★☆ | ★★★ |

### Phase 2 — 데이터 워크플로우 (Medium Priority)
| 기능 | 난이도 | 영향도 |
|------|--------|--------|
| 어노테이션 도구 | ★★★ | ★★★ |
| Auto-Labeling (SAM 통합) | ★★★ | ★★★ |
| 세그멘테이션 포맷 변환 | ★★☆ | ★★☆ |
| 데이터 증강 파이프라인 | ★★☆ | ★★☆ |
| 클래스 불균형 분석 | ★☆☆ | ★★☆ |
| 리포트 생성 (PDF/HTML) | ★★☆ | ★★☆ |

### Phase 3 — 고급 분석 & 인프라 (Lower Priority)
| 기능 | 난이도 | 영향도 |
|------|--------|--------|
| Grad-CAM / Explainability | ★★★ | ★★☆ |
| 양자화 비교 도구 | ★★☆ | ★★☆ |
| 모델 허브 통합 | ★★☆ | ★★☆ |
| 모델 변환 도구 | ★★★ | ★★☆ |
| 실험 추적 | ★★☆ | ★★☆ |
| Robustness 테스트 | ★★★ | ★★☆ |

### Phase 4 — 확장 & 생태계
| 기능 | 난이도 | 영향도 |
|------|--------|--------|
| OCR 지원 | ★★★ | ★★☆ |
| Depth Estimation | ★★☆ | ★☆☆ |
| Anomaly Detection | ★★★ | ★★☆ |
| 플러그인 시스템 | ★★★ | ★★☆ |
| 원격 추론 | ★★★ | ★☆☆ |
| 3D Vision | ★★★ | ★☆☆ |

---

## 7. 현재 지원 현황 요약

| 카테고리 | 지원됨 ✅ | 미지원 ❌ |
|----------|----------|----------|
| **태스크** | Detection, Classification, Semantic Seg, CLIP Zero-Shot, Embedding | Tracking, Pose, Instance Seg, OCR, Depth, VLM, Generation, Action Recognition, Anomaly Detection, Super Resolution, Face, 3D, Optical Flow |
| **벤치마크** | FPS/Latency (Detection 중심) | 태스크별 벤치마크, 모델 프로파일링, 모델 인스펙터, 양자화 비교, 멀티디바이스, 에너지 효율 |
| **데이터** | Explorer, Splitter, Converter (Det), Remapper, Merger, Sampler, Quality Check, Duplicate, Anomaly Label | 어노테이션, Auto-Label, Active Learning, Seg 포맷, Keypoint 데이터, 비디오 어노테이션, 버전 관리, 증강 파이프라인, 멀티모달 |
| **분석** | FP/FN, Conf Optimizer, Embedding Viz, Tensor Heatmap | Tracking 평가, Pose 평가, Cross-Domain, Robustness, Fairness, Grad-CAM, 리포트 생성 |
| **인프라** | 로컬 추론, CSV/Excel 내보내기, i18n (KO/EN) | 모델 허브, 모델 변환, 실험 추적, 플러그인, 원격 추론, 배치 자동화 |
