from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# ----------------------------
# 0) 형태소 분석기 + 사용자 단어 로드
# ----------------------------
okt = Okt()

# user_dict.txt : 한 줄에 단어 하나씩
# 예)
# 스타벅스
# 아메리카노
# 경향신문
# 이마트
# 영수증
# 카페영수증
try:
    with open("user_dict.txt", encoding="utf-8") as f:
        USER_WORDS = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    USER_WORDS = []
    print("[경고] user_dict.txt 파일이 없습니다. 사용자 단어 없이 진행합니다.")


# ----------------------------
# 1) 복합명사 생성
# ----------------------------
def create_compound_nouns(pos_result):
    """
    연속된 명사들을 결합해서 복합명사 생성
    예: [('스타벅스','Noun'), ('아메리카노','Noun')] -> '스타벅스아메리카노'
    """
    compounds = []
    buffer = []

    for word, tag in pos_result:
        if tag == "Noun":
            buffer.append(word)
        else:
            if len(buffer) >= 2:
                compounds.append("".join(buffer))
            buffer = []

    if len(buffer) >= 2:
        compounds.append("".join(buffer))

    return compounds


# ----------------------------
# 2) 토크나이즈(명사 + 사용자 단어 + 복합명사)
# ----------------------------
def tokenize_nouns(text: str):
    pos = okt.pos(text, norm=True, stem=True)

    # 명사만 추출 (2글자 이상만)
    nouns = [word for word, tag in pos if tag == "Noun" and len(word) >= 2]

    # 사용자 단어 강제 포함 (문장 안에 포함되면 후보로 추가)
    for w in USER_WORDS:
        if w in text:
            nouns.append(w)

    # 복합명사 생성해서 후보 확장
    compound_nouns = create_compound_nouns(pos)
    nouns.extend(compound_nouns)

    return nouns


# ----------------------------
# 3) TF 점수 (fallback용)
# ----------------------------
def calculate_tf_scores(tokens):
    """
    TF (Term Frequency) 기반 점수 계산
    문서가 1개거나 TF-IDF가 의미 없을 때 대비
    """
    counter = Counter(tokens)
    total = sum(counter.values()) if counter else 1

    tf_scores = {}
    for word, count in counter.items():
        tf_scores[word] = count / total

    return tf_scores


# ----------------------------
# 4) TF-IDF 우선, 안되면 TF로 fallback
# ----------------------------
def calculate_scores(doc_texts, tokens_for_single_doc):
    """
    doc_texts: 여러 문서(코퍼스) 텍스트 리스트
    tokens_for_single_doc: 지금 키워드 뽑고 싶은 '한 문서'의 토큰들
    """
    # 문서가 2개 이상이면 TF-IDF 시도
    if len(doc_texts) >= 2:
        try:
            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform(doc_texts)

            # 여기서는 첫 번째 문서(0번)의 점수를 뽑는 예시
            scores = tfidf.toarray()[0]
            words = vectorizer.get_feature_names_out()
            return dict(zip(words, scores))
        except Exception as e:
            print("[경고] TF-IDF 계산 실패. TF 방식으로 대체합니다.")
            print("원인:", e)

    # fallback: TF 방식
    return calculate_tf_scores(tokens_for_single_doc)


# ----------------------------
# 5) 키워드 추출 (최종)
# ----------------------------
def extract_keywords(text: str, corpus_texts=None, top_k=10):
    """
    text: 키워드 뽑을 대상 문서 원문
    corpus_texts: (선택) TF-IDF용 코퍼스(여러 문서 원문 리스트)
                 없으면 TF fallback이 적용될 수 있음
    """
    tokens = tokenize_nouns(text)

    # TF-IDF는 "여러 문서"가 있어야 의미가 생김
    if corpus_texts and len(corpus_texts) >= 2:
        # 코퍼스 문서들도 동일한 토크나이즈 방식으로 전처리해서 넣기
        doc_texts = [" ".join(tokenize_nouns(doc)) for doc in corpus_texts]
    else:
        doc_texts = [" ".join(tokens)]  # 문서 1개짜리 상황

    scores = calculate_scores(doc_texts, tokens)

    # 점수 높은 순으로 정렬
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranked = [(w, s) for w, s in ranked if s > 0]

    # 상위 top_k 반환
    return ranked[:top_k]


# ----------------------------
# 6) 테스트 실행
# ----------------------------
if __name__ == "__main__":
    # 샘플 문서들 (코퍼스)
    docs = [
        "2024년 1월 15일 스타벅스 아메리카노 4500원 결제했습니다.",
        "이마트에서 장을 봤고 총 금액은 27600원입니다. 영수증을 보관합니다.",
        "경향신문 경영 독립 관련 기사입니다. 기업과 시장에 대한 내용이 포함됩니다.",
    ]

    # (A) 코퍼스가 있을 때 TF-IDF(가능하면) 사용
    print("\n=== [A] 코퍼스(문서 3개) 기반 키워드 (첫 번째 문서) ===")
    keywords_a = extract_keywords(docs[0], corpus_texts=docs, top_k=10)
    for kw, sc in keywords_a:
        print(f"{kw}\t{sc:.4f}")

    # (B) 문서 1개만 있을 때: TF fallback 동작 확인
    print("\n=== [B] 문서 1개만 있을 때 키워드(TF fallback) ===")
    keywords_b = extract_keywords(docs[0], corpus_texts=None, top_k=10)
    for kw, sc in keywords_b:
        print(f"{kw}\t{sc:.4f}")
