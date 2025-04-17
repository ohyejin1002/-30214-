import json

class Aircraft:
    def __init__(self, data):
        self.model = data["model"]
        self.destination = data["destination"]
        self.passengers = data["passengers"]
        self.cargo_weight = data["cargo_weight"]
        self.fuel_weight = data["fuel_weight"]
        self.empty_weight = data["empty_weight"]
        self.tare_weight = data["tare_weight"]
        self.mtow = data["mtow"]
        self.mldw = data["mldw"]
        self.nose_wheel_weight = data["nose_wheel_weight"]
        self.distance_d = data["distance_d"]
        self.distance_l = data["distance_l"]
        self.cg_limit_range = data["cg_limit_range"]
        self.thrust_n = data["thrust_n"]
        self.drag_n = data["drag_n"]
        self.wing_area_m2 = data["wing_area_m2"]
        self.cl = data["cl"]
        self.passenger_weight = self.passengers * 75  # 평균 승객 무게 (kg)

    def get_payload(self):
        return self.passenger_weight + self.cargo_weight

    def get_useful_load(self):
        return self.get_payload() + self.fuel_weight

    def get_zfw(self):
        return self.empty_weight + self.get_payload()

    def get_total_weight(self):
        return self.empty_weight + self.tare_weight + self.cargo_weight + self.fuel_weight

    def calculate_cg(self):
        total_weight = self.get_total_weight()
        if total_weight == 0:
            return None
        cg = (self.distance_d + (self.nose_wheel_weight * self.distance_l)) / total_weight
        cg *= 10  # 단위 보정
        return float(f"{cg:.3f}")
    
    def is_cg_safe(self):
        cg = self.calculate_cg()
        return cg is not None and self.cg_limit_range[0] <= cg <= self.cg_limit_range[1]

    def is_within_limits(self):
        total_weight = self.get_total_weight()
        return total_weight <= self.mtow and total_weight <= self.mldw

    def check_limits(self):
        total_weight = self.get_total_weight()
        zfw = self.get_zfw()
        cg = self.calculate_cg()

        return {
            "기종": self.model,
            "목적지": self.destination,
            "총 중량(kg)": total_weight,
            "ZFW (영연료무게)": zfw,
            "MTOW 초과 여부": "초과함" if total_weight > self.mtow else "초과하지 않음",
            "MLDW 초과 여부": "초과함" if total_weight > self.mldw else "초과하지 않음",
            "무게중심(C.G)": cg,
            "무게중심 적정 여부": "적정 범위" if self.is_cg_safe() else "부적정 범위"
        }

    def show_info(self):
        report = self.check_limits()
        print("\n===== 항공기 상태 리포트 =====")
        for key, value in report.items():
            print(f"{key}: {value}")

# 경고 출력 함수
def print_warning(msg):
    print(f"[경고] {msg}")

# 결과 분석 + 경고 출력 함수
def analyze_result(aircraft):
    result = aircraft.check_limits()
    warnings = []

    if result["MTOW 초과 여부"] == "초과함":
        warnings.append("총 중량이 MTOW(이륙 최대중량)를 초과했습니다.")
    if result["MLDW 초과 여부"] == "초과함":
        warnings.append("총 중량이 MLDW(착륙 최대중량)를 초과했습니다.")
    if result["무게중심 적정 여부"] == "부적정 범위":
        warnings.append("무게중심(C.G)이 적정 범위를 벗어났습니다.")

    if warnings:
        print("\n===== 위험 분석 결과 =====")
        for w in warnings:
            print_warning(w)
        print("===================================")
    else:
        print("\n중량 및 무게중심 모두 적정 상태입니다.")

# 항공기 데이터 수정 함수
def modify_aircraft_data(aircraft):
    try:
        print(f"\n[{aircraft.model}] 데이터 수정 모드입니다. 빈칸으로 두면 기존 값을 유지합니다.")

        cargo_input = input(f"현재 화물 무게: {aircraft.cargo_weight}kg ➝ 새 화물 무게 입력 (kg): ")
        if cargo_input.strip():
            aircraft.cargo_weight = float(cargo_input)

        fuel_input = input(f"현재 연료 무게: {aircraft.fuel_weight}kg ➝ 새 연료 무게 입력 (kg): ")
        if fuel_input.strip():
            aircraft.fuel_weight = float(fuel_input)

        passenger_input = input(f"현재 승객 수: {aircraft.passengers}명 ➝ 새 승객 수 입력: ")
        if passenger_input.strip():
            aircraft.passengers = int(passenger_input)
            aircraft.passenger_weight = aircraft.passengers * 75

        print("데이터가 성공적으로 수정되었습니다!")

    except Exception as e:
        print_warning(f"데이터 수정 중 오류 발생: {e}")
        
#이륙 거리 추정 함수
def estimate_takeoff_distance(model_name, weight_kg, thrust_n, drag_n, wing_area_m2, cl, air_density=1.225, gravity=9.81):
    print("\n==============================")
    print(f"비행기 모델명: {model_name}")
    print("==============================")
    print("입력값 요약:")
    print(f" - 중량: {weight_kg} kg")
    print(f" - 추력: {thrust_n} N")
    print(f" - 항력: {drag_n} N")
    print(f" - 날개 면적: {wing_area_m2} m²")
    print(f" - 양력 계수 (Cl): {cl}")
    print(f" - 공기 밀도: {air_density} kg/m³")
    print(f" - 중력가속도: {gravity} m/s²")

    if thrust_n <= drag_n:
        print("\n[이륙 불가] 추력보다 항력이 크거나 같아 이륙이 불가능합니다.")
        return None

    weight_n = weight_kg * gravity
    numerator = weight_n ** 2
    denominator = gravity * air_density * wing_area_m2 * cl * (thrust_n - drag_n)

    takeoff_distance = numerator / denominator

    print("\n계산 결과:")
    print(f" - 예상 이륙 거리: {takeoff_distance:.2f} m")

    # 이륙 조건 해석
    thrust_margin = thrust_n - drag_n
    thrust_to_drag_ratio = thrust_n / drag_n

    print("\n이륙 조건 해석:")
    if thrust_to_drag_ratio >= 2.0:
        print(f" - 추력이 항력의 {thrust_to_drag_ratio:.2f}배로 넉넉합니다. 짧은 활주로에서도 이륙 가능성이 높습니다.")
    elif thrust_to_drag_ratio >= 1.2:
        print(f" - 추력이 항력보다 약간 큽니다 ({thrust_to_drag_ratio:.2f}배). 평범한 길이의 활주로가 필요합니다.")
    else:
        print(f" - 추력 여유가 부족합니다 ({thrust_to_drag_ratio:.2f}배). 긴 활주로나 무게 감소가 필요할 수 있습니다.")

    print("==============================\n")
    return takeoff_distance
        

# 항공기 데이터 로드
with open("aircraft_data.json", "r", encoding="utf-8") as f:  # 확장자 수정
    aircraft_list = json.load(f)

# 항공기 객체 생성
aircraft_db = {}
for data in aircraft_list:
    aircraft = Aircraft(data)
    aircraft_db[aircraft.model.upper()] = aircraft
    
    
while True:
    user_input = input("\n항공기 종류를 입력하세요 (예: B737, A380, A330, B777, CESSNA 172) 또는 '종료'를 입력하세요: ").upper()
    
    if user_input == "종료":
        print("프로그램을 종료합니다.")
        break
    elif user_input in aircraft_db:
        aircraft = aircraft_db[user_input]
        aircraft.show_info()  # 항공기 정보 출력
        analyze_result(aircraft)  # 분석 결과 출력

        # 이륙 거리 추정
        takeoff_distance = estimate_takeoff_distance(
            model_name=user_input,
            weight_kg=aircraft.get_total_weight(),
            thrust_n=aircraft.thrust_n,
            drag_n=aircraft.drag_n,
            wing_area_m2=aircraft.wing_area_m2,
            cl=aircraft.cl
        )

        # 이륙 거리 출력
        if takeoff_distance is not None:
            print(f"이륙 예상 거리: {takeoff_distance:.2f} m")

        modify = input("데이터를 수정하시겠습니까? (Y/N): ").strip().upper()
        if modify == "Y":
            modify_aircraft_data(aircraft)
            aircraft.show_info()  # 수정된 항공기 정보 출력
            analyze_result(aircraft)  # 수정 후 분석 결과 출력

            # 수정된 후 이륙 거리 재추정
            takeoff_distance = estimate_takeoff_distance(
                model_name=user_input,
                weight_kg=aircraft.get_total_weight(),
                thrust_n=aircraft.thrust_n,
                drag_n=aircraft.drag_n,
                wing_area_m2=aircraft.wing_area_m2,
                cl=aircraft.cl
            )

            # 수정 후 이륙 거리 출력
            if takeoff_distance is not None:
                print(f"수정 후 이륙 예상 거리: {takeoff_distance:.2f} m")
    else:
        print("해당 항공기는 데이터베이스에 없습니다. 다시 입력해주세요.")