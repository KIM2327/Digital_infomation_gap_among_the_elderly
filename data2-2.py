import sqlite3

conn = sqlite3.connect('old.db')
print('데이터베이스 연결 완료')

cursor =conn.cursor()

# 디지털정보화 접근수준 Q1A1~Q3 field: 3~9
accessQ1 = 'field3,field4' 
accessQ2 = 'field5,field7,field8'#field6은 null값이므로 제외
# 3번문항은 논의가 필요할 것 같아 제외

# 디지털정보화 역량 수준 Q4A1~Q5A7 field: 10~23
abilityQ4 = 'field10,field11,field12,field13,field14,field15,field16'

sql = "select "+accessQ1+','+accessQ2+','+abilityQ4+" from old"

cursor.execute(sql)
result =cursor.fetchall()


# 디지털정보화 접근수준 점수 총합

# print(result[1:]) 인덱스 0번지는 데이터 없음

# Q1번 점수 총합
# accessQ1_data[x][y] 값 = str, int로 변환이 안돼서 float사용
# 산출방식: 기기에 관계없이 ①=1점, ②=0점
sql = 'select '+accessQ1+' from old'
cursor.execute(sql)
accessQ1_data =cursor.fetchall()

sum_accessQ1 = 0
for x in range(1,len(accessQ1_data)):
    for y in range(len(accessQ1_data[x])):
        if float(accessQ1_data[x][y]) ==2:
            sum_accessQ1+=0           
        else:
            sum_accessQ1+= 1

# Q2번 점수 총합
# 산출방식 : 기기에 관계없이 1개 이상 ①=1점, ②=0점(피처폰 제외)
# 2020DATA_7고령층_파일설계서.xlsx의 변수값Sheet에서 피쳐폰이 응답번호②라고 나와있음
# 값이 3인 경우에만 0점으로 계산
sql = 'select '+accessQ2+' from old'
cursor.execute(sql)
accessQ2_data =cursor.fetchall()

sum_accessQ2 = 0
for x in range(1,len(accessQ2_data)):
    for y in range(len(accessQ2_data[x])):
        if float(accessQ2_data[x][y]) <= 2 :
            sum_accessQ2+=1  
        else:
            sum_accessQ2+= 0


# 디지털정보화 역량 수준 점수 총합
# Q4총합
# 산출방식: ①or②=0점, ③or④=1점 만점 7점
sql = 'select '+abilityQ4+' from old'
cursor.execute(sql)
abilityQ4_data =cursor.fetchall()

sum_abilityQ4 = 0
for x in range(1,len(abilityQ4_data)):
    for y in range(len(abilityQ4_data[x])):
        if float(abilityQ4_data[x][y]) >= 3:
            sum_abilityQ4+=1
        else:
            sum_abilityQ4+=0



print(sum_accessQ1)
print(sum_accessQ2)
print(sum_abilityQ4)






conn.close()