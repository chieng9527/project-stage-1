from collections import deque
print("=== Task 1 ===")
def find_and_print(messages, current_station):
    #  1. 定義捷運路線分段
    green_line_sections = [
        ["Xindian", "Xindian City Hall", "Qizhang"],
        ["Qizhang", "Xiaobitan"],  # 分支
        ["Qizhang", "Dapinglin", "Jingmei", "Wanlong", "Gongguan", "Taipower Building", "Guting"],
        ["Guting", "Chiang Kai-Shek Memorial Hall", "Ximen", "Beimen", "Zhongshan"],
        ["Zhongshan", "Songjiang Nanjing", "Nanjing Fuxing", "Taipei Arena", "Nanjing Sanmin", "Songshan"]
    ]

    #  2. 構建捷運鄰接表
    def build_graph(sections):
        graph = {}
        for section in sections:
            for i, station in enumerate(section):
                if station not in graph:
                    graph[station] = []
                if i > 0:
                    graph[station].append(section[i - 1])
                if i < len(section) - 1:
                    graph[station].append(section[i + 1])
        return graph

    green_line_graph = build_graph(green_line_sections)

    #  3. 找出每位朋友的捷運站
    def get_friend_stations(messages):
        stations = green_line_graph.keys()
        result = {}
        for name, message in messages.items():
            station = next((st for st in stations if st in message), None)
            if station:
                result[name] = station
        return result

    friend_stations = get_friend_stations(messages)

    #  4. 計算兩站最短距離
    def calculate_shortest_distance(graph, start, end):
        if start == end:
            return 0
        queue = deque([(start, 0)])
        visited = set()

        while queue:
            current, distance = queue.popleft()
            if current == end:
                return distance
            visited.add(current)
            for neighbor in graph[current]:
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
        return float('inf')

    #  5. 找出距離最近的朋友
    nearest_friend = None
    min_distance = float('inf')

    for name, station in friend_stations.items():
        distance = calculate_shortest_distance(green_line_graph, current_station, station)
        if distance < min_distance:
            min_distance = distance
            nearest_friend = name

    print(nearest_friend)  # 輸出最近的朋友名稱

messages={
    "Leslie":"I'm at home near Xiaobitan station.",
    "Bob":"I'm at Ximen MRT station.",
    "Mary":"I have a drink near Jingmei MRT station.",
    "Copper":"I just saw a concert at Taipei Arena.",
    "Vivian":"I'm at Xindian station waiting for you."
}

find_and_print(messages, "Wanlong")  # print Mary
find_and_print(messages, "Songshan")  # print Copper
find_and_print(messages, "Qizhang")  # print Leslie
find_and_print(messages, "Ximen")  # print Bob
find_and_print(messages, "Xindian City Hall")  # print Vivian

print("=== Task 2 ===")
#  1.將三個人的時間切成24等份，以 0 為初始值
schedule = {
    "John": [0] * 24,
    "Bob": [0] * 24,
    "Jenny": [0] * 24
}

def book(consultants, hour, duration, criteria):
    start = hour
    end = hour + duration
    #  2. 更新時間表，把指定時間段從 0 改為 1
    def occupy_time(designer, start, end):
        for i in range(start, end):
            schedule[designer][i] = 1
    #  3. 確認時間段是否空閒
    def is_available(designer, start, end):
        return all(schedule[designer][i] == 0 for i in range(start, end))
    #  4.檢查時間段是否有超過 2 位顧問已被占用
    overlapping = sum(
        1 for c in consultants if any(schedule[c["name"]][i] == 1 for i in range(start, end))
    )
    if overlapping >= len(schedule):
        print("No Service")
        return
    #  5. 找出所有時間空閒的顧問
    available_consultants = [c for c in consultants if is_available(c["name"], start, end)]
    if not available_consultants:
        print("No Service")
        return
    #  6. 比較顧問，根據需求選擇
    if criteria == "price":
        selected = min(available_consultants, key=lambda c: c["price"])
    else:
        selected = max(available_consultants, key=lambda c: c["rate"])
    #  7. 預約成功，更新時間表
    occupy_time(selected["name"], start, end)
    print(selected["name"])

consultants = [
    {"name": "John", "rate": 4.5, "price": 1000},
    {"name": "Bob", "rate": 3, "price": 1200},
    {"name": "Jenny", "rate": 3.8, "price": 800}
]

book(consultants, 15, 1, "price")  # Jenny
book(consultants, 11, 2, "price")  # Jenny
book(consultants, 10, 2, "price")  # John
book(consultants, 20, 2, "rate")   # John
book(consultants, 11, 1, "rate")   # Bob
book(consultants, 11, 2, "rate")   # No Service
book(consultants, 14, 3, "price")  # John

print("=== Task 3 ===")
def func(*data):
    middle_name_map = {}  # 儲存每個中間字與對應的名字
    excluded_names = set()  # 儲存需要排除的名字

    #  1. 提取中間名
    for name in data:
        if len(name) <= 2:
            # 名字只有兩個字，沒有中間名，直接排除
            excluded_names.add(name)
        else:
            # 去掉頭尾，只保留中間部分
            middle_chars = name[1:-1]  # 中間部分
            for char in middle_chars:
                if char not in middle_name_map:
                    middle_name_map[char] = []
                middle_name_map[char].append(name)  # 將名字與中間字對應

            # 如果中間部分有重複字，直接排除該名字
            if len(set(middle_chars)) < len(middle_chars):
                excluded_names.add(name)

    #  2. 遍歷中間名，檢查是否需要排除
    for char, names in middle_name_map.items():
        if len(names) > 1:
            # 如果某個中間字對應多個名字，這些名字都需要排除
            excluded_names.update(names)

    #  3. 找到未被排除的名字
    for name in data:
        if name not in excluded_names:
            print(name)  # 輸出未被排除的名字
            return

    print("沒有")  # 如果所有名字都被排除，輸出 "沒有"

func("彭大牆", "陳王明雅", "吳明")  # print 彭大牆
func("郭靜雅", "王立強", "郭林靜宜", "郭立恆", "林花花")  # print 林花花
func("郭宣雅", "林靜宜", "郭宣恆", "林靜花")  # print 沒有
func("郭宣雅", "夏曼藍波安", "郭宣恆")  # print 夏曼藍波安

print("=== Task 4 ===")
#  0,4,8,7,11,15,14,18,22,21,25,...
def get_number(index):
    total = 0
    for i in range(1, index + 1):
        if (i - 1) % 3 in [0, 1]:
            total += 4 #每組前兩步都是 +4
        else:
            total -= 1 #每組第三步是 -1
    print(total)

get_number(1)  # print 4
get_number(5)  # print 15
get_number(10)  # print 25
get_number(30)  # print 70

print("=== Task 5 ===")
def find(spaces, stat, n):
    best_car_index = -1  # 預設為 -1，表示沒有符合條件的車廂
    min_space = float('inf')  # 用於記錄符合條件的最小車廂空間

    for i in range(len(spaces)):
        if stat[i] == 1 and spaces[i] >= n:  # 車廂可用 目前座位可以坐
            if spaces[i] < min_space:  
                best_car_index = i
                min_space = spaces[i]

    print(best_car_index)

# 測試
find([3, 1, 5, 4, 3, 2], [0, 1, 0, 1, 1, 1], 2)  # print 5
find([1, 0, 5, 1, 3], [0, 1, 0, 1, 1], 4)        # print -1
find([4, 6, 5, 8], [0, 1, 1, 1], 4)              # print 2

