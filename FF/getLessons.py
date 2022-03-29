import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 3가지 설치
# pip install requests
# pip install beautifulsoup4
# pip install lxml

# 부산광역시_구군 정보화교육 정보: https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15034019

def getLessons(numOfRows=30, pageNo=1, target=[], sort='eduSdate', reverse=True, finished=True) -> list:
    """교육일정을 가져옵니다.

    Args:
        numOfRows (int, optional): 추출 개수. Defaults to 30.
        pageNo (int, optional): 페이지 숫자. Defaults to 1.
        target (list): 스크래핑할 정보 순서.
        sort (str, optional): 정렬 기준. Defaults to 'eduSdate'.
        reverse (bool, optional): 역순 정렬. Defaults to True.
        finished (bool, optional): 이미 끝난 교육 추출 여부. (duFdate 필수) Defaults to True.

    Returns:
        list[list]: 교육일정 리스트.
    """

    url = 'http://apis.data.go.kr/6260000/BusanTblIeduScedService/getTblIeduScedInfo'                   # 요청주소
    apikey = 'MpC7WqyRJIO+os3yFCAZpLpKyH3+xQjy2CPLwDk0pKtg4uiEqLJWOv2IqrD8/mL5Jx/sySaL6EdkCl+AohORXQ==' # api키 - 1일 1만 번 호출 제한
    params = {
        'serviceKey' : apikey,
        'pageNo' : pageNo,          # 가져올 페이지 숫자
        'numOfRows' : numOfRows,    # 한 페이지 당 (numOfRows)개 추출
        # 'resultType' : 'json',    # xml 추출 (default값 - xml)
    }

    res = requests.get(url, params=params)  # respose 객체 호출
    soup = BeautifulSoup(res.text, 'xml')   # xml 파싱 (lxml 설치 필요)
    raw_data = soup.find_all('item')        # 각 교육일정 스크래핑
    lessons = [[lesson.find(info_type).text for info_type in target] for lesson in raw_data] # 2차원 리스트로 변환
    
    # 정렬 기준 인덱스를 구한다.
    if sort in target:
        index = target.index(sort)
    else:
        index = 0
    sorted_lessons = sorted(lessons, key=lambda x: x[index], reverse=reverse)  # 정렬한다.
    
    # 이미 끝난 교육은 제거한다. - 참고. 코딩도장 p.729 / datetime 모듈
    if finished == False and 'eduSdate' in target:
        today = datetime.today()
        index = target.index('eduSdate')
        for lesson in lessons:
            date_end = lesson[index]
            if date_end == '':   # 항시 교육은 삭제하지 않고
                continue        # 그냥 넘어간다.
            else:
                date_end = map(int, date_end.split('-'))
                delta = datetime(*date_end) - today     # 두 날짜의 차를 구한다.
                if str(delta)[0] == '-':                # 이미 지난 교육이면
                    sorted_lessons.remove(lesson)       # 해당 교육은 리스트에서 삭제한다.
                
    return sorted_lessons
    
if __name__ == '__main__':
    infoes = [ # 정보 종류
        'dataDay', 'eduTime', 'gugun', 'tel', 'lng', 'addr', 'period', 'people', 'roadAddr', 
        'eduFdate', 'eduSdate', 'months', 'days', 'eduLoc', 'target', 'eduExp', 'eduNm', 'lat',
        # 'dataDay', 'eduTime', 'gugun', 'tel', 'lng', 'period', 'people', 'roadAddr', 
        # 'eduFdate', 'eduSdate', 'eduLoc', 'target', 'eduExp', 'eduNm', 'lat',
    ]
        
    # # 필요한 정보를 순서대로 입력한다.
    # target = ['eduNm', 'eduLoc', 'eduExp', 'target', 'eduSdate', 'eduFdate', 'roadAddr', 'gugun', 'period', 'tel', 'lat', 'lng']
    # # 200개 중 끝난 강의를 제외하고 가져온다.
    # lessons = getLessons(200, finished=False, target=target)
    # for i, lesson in enumerate(lessons, start=1):
    #     print(lesson)
    # print('추출 강의 수: %d' % i)
    import math
    loc = 'on'
    pg = 1
    
    target = [
        'eduNm', 'eduLoc', 'eduExp', 'target', 'eduSdate',
        'eduFdate', 'roadAddr', 'gugun', 'period', 'tel',
    ]
    # 200개 중 신청 가능한 강의를 제외하고 가져온다.
    lessons = getLessons(400, finished=False, target=target, sort='eduSdate')
    
    # 해당 지역의 강의만 가져온다.
    index1 = target.index('eduLoc')
    index2 = target.index('roadAddr')
    if loc == 'yeongdo':
        eduLoc = '영도'
    elif loc == 'sasang':
        eduLoc = '사상'
    elif loc == 'hae-un':
        eduLoc = '해운대'
    else:
        eduLoc = '온라인'
        
    filtered_lessons = list(filter(lambda x: eduLoc in x[index1] or eduLoc in x[index2], lessons))
    
    context = {
        'target': target,
        'lessons': filtered_lessons[(pg-1)*12:pg*12],
        'pg' : range(1, math.ceil(pg / 10) + 1),
        'loc': loc
    }
    print(len(filtered_lessons))
    print(filtered_lessons[(pg-1)*10:pg*10])
    print(range(1, math.ceil(pg / 10) + 1))
    
    # for x in lessons:
    #     print(x[1], '//', x[6])