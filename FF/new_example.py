import sqlite3

with sqlite3.connect('./old_data.db') as conn:
    # print('데이터베이스 연결 완료\n')
    cursor = conn.cursor()

    sql = 'select * from "old"'
    cursor.execute(sql)
    columns = list(map(lambda x: x[0], cursor.description))
    for x in cursor.description:
        print(x)
    records = cursor.fetchall()
    result = []
    
    for j in range(len(columns)-1):
        iterator = (records[i][j] if isinstance(records[i][j], int) else 0 if records[i][j] is None else int(records[i][j])
            for i in range(1, len(records))
        )
        result.append(sum(iterator))
        
    print(result)