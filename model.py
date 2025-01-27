import openai
import pandas as pd
openai.api_key = ""

file_path = '/root/orio/cr_data301.csv'
df = pd.read_csv(file_path)

def review(row_index):
    date = df.iloc[row_index]['date']
    title = df.iloc[row_index]['title']
    content = df.iloc[row_index]['content']
    sympathy = df.iloc[row_index]['sympathy']

    return f"다음은 다양한 리뷰 데이터입니다. 각 리뷰는 넘버링으로 구별되어 있습니다.: 1. 제목: {title}, 내용: {content}, 작성일: {date}, 공감 수: {sympathy}"

example_output = """
{"요약": "황금돼지집은 신선한 생고기와 소고기 육회로 인기 있는 합정역 맛집입니다.",
    "상세 정보": {
        "분위기": "깔끔하고 현대적인 인테리어로 편안한 분위기를 제공합니다.",
        "서비스": "직접 구워주는 서비스가 있어 초보자도 걱정 없이 즐길 수 있어요.",
        "가격대": "1인당 30000원대의 프리미엄 고기 집입니다.",
        "대표 메뉴": ["육회 비빔밥", "생고기 모듬"],
        "주차": "매장 앞 전용 주차 공간이 마련되어 있어 편리해요."}
"""
example_output2 = """
{"요약": "원조소금구이는 양념고기와 껍대기으로 유명한 목동역 핫플입니다.",
    "상세 정보": {
        "분위기": "넓고 탁 트인 매장으로, 쾌적한 식사 환경을 제공합니다.",
        "서비스": "라면이 무제한으로 제공해요!",
        "가격대": "20000원대의 합리적인 가격으로 즐길 수 있어요.",
        "대표 메뉴": ["소금 구이 모듬"],
        "주차": "주차 공간이 협소하니 방문 전 전화 예약을 추천드려요."}
"""
############################################################################################################

multi_file_path = '/root/orio/cr_data301.csv'
multi_df = pd.read_csv(multi_file_path)

#preprocess
columns_to_check = ['title', 'content']
for col in columns_to_check:
    multi_df = multi_df[(multi_df[col].notna()) & (multi_df[col] != 'unknown')]

def multi_review(row_index):
    res_name = multi_df[multi_df['id'] == row_index]['restaurant_name'].iloc[0]
    df = multi_df[multi_df['restaurant_name'] == res_name]
    
    # 광고 비율 계산 및 제거
    ad_o_ratio = round((df['광고'] == 'O').mean() * 100, 2)
    df = df[df['광고'] != 'O']
    
    reviews = f"다음은 다양한 리뷰 데이터입니다. 각 리뷰는 넘버링으로 구별되어 있습니다.:"
    for i in range(df.shape[0]):
        title = df.iloc[i]['title']
        content = df.iloc[i]['content']
        tags = df.iloc[i]['tags']
        reviews += f" {i+1}. 제목: {title}, 내용: {content}, 테그: {tags}"

    return ad_o_ratio, reviews

response = openai.chat.completions.create(
    model= "gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an assistant who summarizes user reviews."},
        {"role": "user", "content": "다양한 리뷰에서 나타난 내용을 종합하여 다음 카테고리 형식으로 출력해 주세요. 각 항목에서 해당 항목에 해당하는 내용이 없을 경우, 그 카테고리 항목은 출력에 포함하지 마세요. 카테고리 항목에 알맞는 내용만 포함되어야 합니다. 가격대는 가능하다면 대표메뉴를 참고해 주세요. 카테고리: 1) 분위기 2) 서비스 3) 손님 나이대 4) 음식의 가격대 5) 대표 메뉴 6) 주차 7) 위생. 이 카테고리는 반드시 모두 포함될 필요는 없습니다.구체적인 정보가 없는 카테고리는 해당 카테고리를 포함한 모든 출력을 생략해 주세요. 또한, 요약은 반드시 포함되어야 하며 1~2문장 정도로 간단하게 요약해 주세요. 모두 한국어로 출력해 주세요. 출력은 반드시 리뷰의 내용을 근거로 출력해야 합니다, 말투의 끝은 해요 좋아요 등 친절하게 해주세요"},
        {"role": "user", "content": review(1)},
        {"role": "assistant", "content": example_output},
        {"role": "user", "content": review(11)},
        {"role": "assistant", "content": example_output2},
        {"role": "user", "content": multi_review(100)[1]}
    ]
)
print(response.choices[0].message.content)