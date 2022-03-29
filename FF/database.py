import sqlite3
from typing import Iterable, Union

def table_to_sum(database: str, table: str) -> tuple[dict, int]:
    """각 열의 총합을 구합니다.

    Args:
        database (str): 데이터베이스 path.
        table (int): 테이블 이름.

    Returns:
        tuple[dict, int]: 총합, 총 레코드 수.
    """
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()

        sql = 'select * from "%s"' % table
        cursor.execute(sql)
        columns = list(map(lambda x: x[0], cursor.description))

        records = cursor.fetchall()
        
        result = []
        for j in range(len(columns)):
            column_values = (records[i][j] for i in range(len(records)))    # j-열의 모든 데이터를 입력한다.
            result.append(sum(column_values))                               # j-열의 모든 데이터를 합한다.

    return dict(zip(columns, result)), len(records)

def to_score(record: dict[str, int]) -> tuple[Union[int, float]]:
    """문항(key)-응답번호(value)로 묶여있는 dictionary 객체를 받아 점수 tuple로 반환합니다.
    ex. to_score(dict(zip(columns, record))) -> tuple.
    
    Args:
        record (dict): 문항-응답번호로 묶여있는 dictionary 객체.

    Returns:
        tuple: 각 점수(A1, A2, B1, B2, C1, C2, C3).
    """
    # A1-A3
    A2_1 = 1 if (record['Q1A1'] == 1 or record['Q1A2'] == 1) else 0
    A2_2 = 1 if (
        record['Q2A11'] != 3 or record['Q2A2'] == 1 or record['Q2A3'] == 1
    ) else 0
    A1 = 1 if (record['Q3'] == 1 or A2_2 == 1) else 0
    A2 = A2_1 + A2_2
    
    # B1-B2
    B1, B2 = 0, 0
    for i in range(1, 8):
        if record['Q4A%d' % i] >= 3: B1 += 1
        if record['Q5A%d' % i] >= 3: B2 += 1
    
    # C1-C4
    # 조건이 이상함. 1점과 1.5점의 조건이 같음.
    # 아마도 '1 | 2, 3'으로 나누었을 때, 둘 다 1일 이상이면 1.5점, 둘 중 하나만 1일 이상이면 1점으로 계산
    if record['Q7'] == 1:   # 1번을 응답한 경우
        C1 = 1.5 if (
            record['Q7A1'] >= 1 and (record['Q7A2'] >= 1 or record['Q7A2'] >= 1)
        ) else 1
    else:                   # 2, 3번인 경우
        C1 = 0              # 0점
        
    C2 = 0
    for i in range(1, 5):   # 8번 문항
        if record['Q8A%d' % i] >= 3 or record['Q8B%d' % i] >= 3: C2 += 1
    for i in range(1, 6):   # 9번 문항
        if record['Q9A%d' % i] >= 3 or record['Q9B%d' % i] >= 3: C2 += 1
    for i in range(1, 5):   # 10번 문항
        if record['Q10A%d' % i] >= 3 or record['Q10B%d' % i] >= 3: C2 += 1
    
    C3_1 = 0
    for i in range(1, 3):   # 11번 문항
        if record['Q11A%d' % i] >= 3 or record['Q11B%d' % i] >= 3:
            C3_1 = 1        # 하나라도 3 or 4번을 선택하면 1점
            break
    C3_2 = 0
    for i in range(1, 3):   # 12번 문항
        if record['Q12A%d' % i] >= 3 or record['Q12B%d' % i] >= 3:
            C3_2 = 1        # 하나라도 3 or 4번을 선택하면 1점
            break
    C3_3 = 0
    for i in range(1, 5):   # 13번 문항
        if record['Q13A%d' % i] >= 3 or record['Q13B%d' % i] >= 3:
            C3_3 = 1        # 하나라도 3 or 4번을 선택하면 1점
            break
    C3_4 = 0
    for i in range(1, 5):   # 13번 문항
        if record['Q14A%d' % i] >= 3 or record['Q14B%d' % i] >= 3:
            C3_4 = 1        # 하나라도 3 or 4번을 선택하면 1점
            break
    C3 = C3_1 + C3_2 + C3_3 + C3_4
    
    return (A1, A2, B1, B2, C1, C2, C3)
    
def scores_to_db(database: str,
                 table: str,
                 records: Iterable[Iterable[Union[int, float]]],
                 ) -> None:
    """점수 데이터를 받아서 테이블을 만듭니다.

    Args:
        database (str): 데이터베이스 path.
        table (str): 테이블 이름.
        records (Iterable[Iterable[Union[int, float]]]): 각 요소가 (A1, A2, B1, B2, C1, C2, C3)로 된 2차원 자료형 점수 데이터.
    """
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute( # 테이블 생성
            """
            CREATE TABLE IF NOT EXISTS "%s" (
                A1 integer,
                A2 integer,
                B1 integer,
                B2 integer,
                C1 real,
                C2 integer,
                C3 integer
            );
            """ % table
        )
        
        sql = 'insert into "%s" (A1, A2, B1, B2, C1, C2, C3) values (?, ?, ?, ?, ?, ?, ?);' % table
        cursor.executemany(sql, records) # 점수 데이터를 새로운 테이블에 추가한다.
        
def rawdata_to_db(database: str, table: str) -> None:
    """설문 테이블에서 점수 테이블을 만듭니다.
    *새로운 테이블의 이름은 {table}_score.

    Args:
        database (str): 데이터베이스 path.
        table (str): 테이블 이름.
    """
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()

        sql = 'select * from "%s"' % table
        cursor.execute(sql)
        columns = tuple(map(lambda x: x[0], cursor.description))
        records = cursor.fetchall()
        
    new_records = []
    for record in records:
        int_record = [
            record[i] if isinstance(record[i], int) else    # 정수인 경우 그대로 쓴다.
            0 if record[i] is None else                     # 비어있는 경우 0으로 대체한다.
            int(record[i])                                  # 정수모양 문자열인 경우 정수로 바꿔준다.
            for i in range(len(columns) - 1)                # 끝 행(WT)은 제외하고 만든다.
        ]
        
        new_record = to_score(dict(zip(columns, int_record)))
        new_records.append(new_record)

    scores_to_db(database, table + '_score', new_records)
    
if __name__ == '__main__':
    db_path = './old.db'
    table = '2020DATA_1일반국민'
    rawdata_to_db(db_path, table)                           # 설문 데이터를 점수로 변환해서 점수 테이블을 만든다.
    score, total = table_to_sum(db_path, table + '_score')  # 점수 테이블에서 각 행의 합을 구한다.
    
    # 가중치 계산 방법
    # A1 = Q3 * 100                             | score['A1'] = Q3
    # A2 = (Q1+ Q2) * 1/2 *100                  | score['A2'] = Q1+ Q2
    # B1 = Q4 * 1/7 * 100                       | score['B1'] = Q4
    # B2 = Q5 * 1/7 * 100                       | score['B2'] = Q5
    # C1 = Q7 * 1/1.5 * 100                     | score['C1'] = Q7
    # C2 = Q8_10* 1/13 * 100                    | score['C2'] = Q8 + Q9 + Q10
    # C3 = (Q11 + Q12 + Q13 + Q14)* 1/4 * 100   | score['C3'] = Q11 + Q12 + Q13 + Q14
    
    # 가중치 적용
    A1 = score['A1'] * 100
    A2 = score['A2'] * 1/2 *100
    B1 = score['B1'] * 1/7 * 100
    B2 = score['B2'] * 1/7 * 100
    C1 = score['C1'] * 1/1.5 * 100
    C2 = score['C2'] * 1/13 * 100
    C3 = score['C3'] * 1/4 * 100
    
    # 각종 지수 계산
    A = ((A1 * 0.5) + (A2 * 0.5)) / total               # 접근지수
    B = ((B1 * 0.5) + (B2 * 0.5)) / total               # 역량지수
    C = ((C1 * 0.4) + (C2 * 0.4) + (C3 * 0.2)) / total  # 활용지수
    S = (A * 0.2) + (B * 0.4) + (C * 0.4)               # 종합지수
    
    print('\n*원점수')
    print('접근지수: {:.2f} 점'.format(A))
    print('역량지수: {:.2f} 점'.format(B))
    print('활용지수: {:.2f} 점'.format(C))
    print('종합지수: {:.2f} 점'.format(S))
    
    print('\n*상대지수') # 일반국민의 수준을 100으로 봤을 때 상대지수
    print('접근지수: {:.2f} %'.format(A / .9515))
    print('역량지수: {:.2f} %'.format(B / .6503))
    print('활용지수: {:.2f} %'.format(C / .6593))
    print('종합지수: {:.2f} %'.format(S / .7141))
    
    # 정확한 수치는 pdf 44-49