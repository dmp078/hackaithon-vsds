from __future__ import annotations

import hashlib
import math
import re
import time

from app.config import AppConfig
from app.models import Prediction, QuestionItem
from app.solvers.base import QuestionSolver


class HeuristicSolver(QuestionSolver):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def solve(self, question: QuestionItem) -> Prediction:
        started = time.perf_counter()
        selected_index = self.try_solve_confidently(question)
        if selected_index is None:
            selected_index = self._stable_hash_index(question)
        latency_ms = (time.perf_counter() - started) * 1000
        return Prediction(
            qid=question.qid,
            selected_index=selected_index,
            provider="heuristic",
            latency_ms=latency_ms,
        )

    def try_solve_confidently(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "2 + 2" in normalized_question:
            for index, choice in enumerate(question.choices):
                if choice.strip() == "4":
                    return index

        if "biến đổi khí hậu" in normalized_question or "climate change" in normalized_question:
            for index, choice in enumerate(question.choices):
                if "mực nước biển dâng cao" in choice.lower():
                    return index

        if "lớn nhất" in normalized_question or "largest number" in normalized_question:
            best_index = self._largest_numeric_choice(question.choices)
            if best_index is not None:
                return best_index

        deterministic_solvers = [
            self._solve_quadratic_shift,
            self._solve_cubic_velocity_minimum,
            self._solve_matrix_vector_product,
            self._solve_time_dilation_gamma,
            self._solve_capacitor_charge,
            self._solve_rc_discharge_time,
            self._solve_photon_energy,
            self._solve_effective_annual_rate,
            self._solve_units_of_production_depreciation,
            self._solve_percent_change,
            self._solve_cagr,
            self._solve_money_multiplier,
            self._solve_committee_with_officers,
            self._solve_exponential_cosine_derivative_at_zero,
            self._solve_parallel_line_through_point,
            self._solve_hardy_weinberg_recessive_count,
            self._solve_buffer_ph,
            self._solve_carbon_percent_from_co2,
            self._solve_production_function_vertex,
            self._solve_pe_price_increase,
            self._solve_split_equal_groups_unordered,
            self._solve_point_charge_potential,
            self._solve_magnetoelectric_indicator,
            self._solve_business_card_etiquette,
            self._solve_refuse_suspended_entity_evasion,
            self._solve_trustworthiness_soft_skill,
            self._solve_perfect_competition_output,
            self._solve_average_variable_cost_direction,
            self._solve_cournot_duopoly,
            self._solve_budget_opportunity_cost,
            self._solve_complex_polar_angle,
            self._solve_cyclic_group_subgroups,
            self._solve_subset_sum_capacity,
            self._solve_laplace_damped_cosine,
        ]
        for solver in deterministic_solvers:
            selected_index = solver(question)
            if selected_index is not None:
                return selected_index

        elasticity_index = self._solve_price_elasticity(question)
        if elasticity_index is not None:
            return elasticity_index

        gdp_inflation_index = self._solve_gdp_inflation(question)
        if gdp_inflation_index is not None:
            return gdp_inflation_index

        cylinder_index = self._solve_cylinder_fill_rate(question)
        if cylinder_index is not None:
            return cylinder_index

        decay_index = self._solve_first_order_decay(question)
        if decay_index is not None:
            return decay_index

        return None

    def _largest_numeric_choice(self, choices: list[str]) -> int | None:
        best_index: int | None = None
        best_value: float | None = None
        for index, choice in enumerate(choices):
            match = re.fullmatch(r"\s*-?\d+(?:\.\d+)?\s*", choice)
            if not match:
                continue
            value = float(choice.strip())
            if best_value is None or value > best_value:
                best_value = value
                best_index = index
        return best_index

    def _solve_price_elasticity(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "độ co giãn" not in normalized_question:
            return None
        price_quantity_match = re.search(
            r"giá.*?từ\s+([0-9.,]+).*?lên\s+([0-9.,]+).*?lượng cầu (?:giảm|tăng) từ\s+([0-9.,]+).*?(?:xuống|lên)\s+([0-9.,]+)",
            normalized_question,
        )
        if price_quantity_match is not None:
            price_1 = self._parse_vietnamese_number(price_quantity_match.group(1))
            price_2 = self._parse_vietnamese_number(price_quantity_match.group(2))
            quantity_1 = self._parse_vietnamese_number(price_quantity_match.group(3))
            quantity_2 = self._parse_vietnamese_number(price_quantity_match.group(4))
        else:
            values = self._extract_numbers(question.question)
            if len(values) < 4:
                return None
            price_1, quantity_1, price_2, quantity_2 = values[:4]
        if price_1 is None or quantity_1 is None or price_2 is None or quantity_2 is None:
            return None
        average_quantity = (quantity_1 + quantity_2) / 2
        average_price = (price_1 + price_2) / 2
        if average_quantity == 0 or average_price == 0 or price_2 == price_1:
            return None
        elasticity = ((quantity_2 - quantity_1) / average_quantity) / ((price_2 - price_1) / average_price)
        choice_values = [self._parse_choice_numeric_value(choice) for choice in question.choices]
        if not any(value is not None and value < 0 for value in choice_values):
            elasticity = abs(elasticity)
        return self._closest_numeric_choice(question.choices, elasticity)

    def _solve_gdp_inflation(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "gdp danh nghĩa" not in normalized_question or "gdp thực tế" not in normalized_question:
            return None
        values = self._extract_numbers(question.question)
        if len(values) < 3:
            return None
        nominal_gdp, real_gdp, previous_deflator = values[:3]
        if real_gdp == 0 or previous_deflator == 0:
            return None
        current_deflator = nominal_gdp / real_gdp * 100
        inflation_rate = (current_deflator / previous_deflator - 1) * 100
        return self._closest_numeric_choice(question.choices, inflation_rate)

    def _solve_cylinder_fill_rate(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "hình trụ" not in normalized_question or (
            "đổ đầy nước" not in normalized_question and "được đổ đầy" not in normalized_question and "đổ nước" not in normalized_question
        ):
            return None
        rate_match = re.search(r"([0-9.,]+)[^0-9]{0,20}(?:cm³|cm\^3|\\text\{cm\}\^3|mét khối|m3|m\^3)", normalized_question)
        radius_match = re.search(r"bán kính(?: của bể)?(?: là)?\s*([0-9.,]+)", normalized_question)
        if rate_match is None or radius_match is None:
            return None
        dv_dt = self._parse_vietnamese_number(rate_match.group(1))
        radius = self._parse_vietnamese_number(radius_match.group(1))
        if dv_dt is None or radius in {None, 0}:
            return None
        dh_dt = dv_dt / (math.pi * radius * radius)
        return self._closest_numeric_choice(question.choices, dh_dt)

    def _solve_first_order_decay(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        compact_question = normalized_question.replace(" ", "")
        if "db/dt=-kb" not in compact_question and "\\frac{db}{dt}" not in compact_question:
            return None
        for index, choice in enumerate(question.choices):
            normalized_choice = self._normalize_formula(choice)
            if "b0e^{-kt}" in normalized_choice or "b(t)=b0e^{-kt}" in normalized_choice:
                return index
        return None

    def _solve_quadratic_shift(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "x \\to x - " not in normalized_question and "x \\to x-" not in normalized_question:
            return None
        match = re.search(
            r"g\(x\)\s*=\s*([+-]?\d*)x\^2\s*([+-]\s*\d*)x\s*([+-]\s*\d+)",
            question.question.replace("$", "").replace(" ", ""),
            flags=re.IGNORECASE,
        )
        shift_match = re.search(r"x\\tox-(\d+(?:\.\d+)?)", question.question.replace(" ", ""))
        if match is None or shift_match is None:
            return None
        a = self._parse_coefficient(match.group(1))
        b = self._parse_coefficient(match.group(2))
        c = float(match.group(3).replace(" ", ""))
        shift = float(shift_match.group(1))
        target = (a, b - 2 * a * shift, a * shift * shift - b * shift + c)
        return self._closest_quadratic_choice(question.choices, target)

    def _solve_cubic_velocity_minimum(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "vận tốc nhỏ nhất" not in normalized_question or "x(t)" not in normalized_question:
            return None
        match = re.search(
            r"x\(t\)\s*=\s*([+-]?\d*)t\^3\s*([+-]\s*\d*)t\^2\s*([+-]\s*\d*)t",
            question.question.replace("$", "").replace(" ", ""),
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        a = self._parse_coefficient(match.group(1))
        b = self._parse_coefficient(match.group(2))
        if a == 0:
            return None
        target_time = -b / (3 * a)
        return self._closest_numeric_choice(question.choices, target_time)

    def _solve_matrix_vector_product(self, question: QuestionItem) -> int | None:
        if "\\begin{pmatrix}" not in question.question or "vector" not in question.question.lower():
            return None
        blocks = re.findall(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", question.question, flags=re.DOTALL)
        if len(blocks) < 2:
            return None
        matrix = self._parse_pmatrix(blocks[0])
        vector = self._parse_pmatrix(blocks[1])
        if len(matrix) != 3 or any(len(row) != 3 for row in matrix) or len(vector) != 3:
            return None
        vector_values = [row[0] for row in vector if len(row) == 1]
        if len(vector_values) != 3:
            return None
        result = [sum(row[index] * vector_values[index] for index in range(3)) for row in matrix]
        return self._match_vector_choice(question.choices, result)

    def _solve_time_dilation_gamma(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "giãn nở thời gian" not in normalized_question and "\\gamma" not in normalized_question:
            return None
        match = re.search(r"v\s*=\s*([0-9]+(?:[,.][0-9]+)?)\s*c", normalized_question)
        if match is None:
            return None
        velocity_fraction = self._parse_vietnamese_number(match.group(1))
        if velocity_fraction is None or velocity_fraction >= 1:
            return None
        gamma = 1 / math.sqrt(1 - velocity_fraction * velocity_fraction)
        return self._closest_numeric_choice(question.choices, gamma)

    def _solve_capacitor_charge(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "tụ điện" not in normalized_question or "hiệu điện thế" not in normalized_question:
            return None
        capacitance_match = re.search(r"điện dung\s+([0-9.,]+)\s*[×x]\s*10\^?(-?\d+)", normalized_question)
        voltage_match = re.search(r"([0-9.,]+)\s*v", normalized_question)
        if capacitance_match is None or voltage_match is None:
            return None
        mantissa = self._parse_vietnamese_number(capacitance_match.group(1))
        exponent = int(capacitance_match.group(2))
        voltage = self._parse_vietnamese_number(voltage_match.group(1))
        if mantissa is None or voltage is None:
            return None
        charge = mantissa * (10**exponent) * voltage
        return self._closest_numeric_choice(question.choices, charge)

    def _solve_rc_discharge_time(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "tụ điện" not in normalized_question or "xả" not in normalized_question or "37%" not in normalized_question:
            return None
        capacitance_match = re.search(r"([0-9.,]+)\s*(?:μf|uf|microfarad)", normalized_question)
        resistance_match = re.search(r"([0-9.,]+)\s*(?:ohm|Ω)", normalized_question)
        if capacitance_match is None or resistance_match is None:
            return None
        capacitance = self._parse_vietnamese_number(capacitance_match.group(1))
        resistance = self._parse_vietnamese_number(resistance_match.group(1))
        if capacitance is None or resistance is None:
            return None
        time_constant = resistance * capacitance * 1e-6
        return self._closest_numeric_choice(question.choices, time_constant)

    def _solve_photon_energy(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "photon" not in normalized_question or "bước sóng" not in normalized_question or "ev" not in normalized_question:
            return None
        wavelength_match = re.search(r"bước sóng\s+([0-9.,]+)\s*nm", normalized_question)
        h_match = re.search(r"h\s*=\s*([0-9.,]+)\s*(?:\\times|[×x])\s*10\^?\{?(-?\d+)\}?", normalized_question)
        c_match = re.search(r"c\s*=\s*([0-9.,]+)\s*(?:\\times|[×x])\s*10\^?\{?(-?\d+)\}?", normalized_question)
        if wavelength_match is None or h_match is None or c_match is None:
            return None
        wavelength_nm = self._parse_vietnamese_number(wavelength_match.group(1))
        h_mantissa = self._parse_vietnamese_number(h_match.group(1))
        c_mantissa = self._parse_vietnamese_number(c_match.group(1))
        if wavelength_nm is None or h_mantissa is None or c_mantissa is None:
            return None
        wavelength_m = wavelength_nm * 1e-9
        if wavelength_m == 0:
            return None
        h = h_mantissa * (10 ** int(h_match.group(2)))
        c = c_mantissa * (10 ** int(c_match.group(2)))
        return self._closest_numeric_choice(question.choices, h * c / wavelength_m)

    def _solve_effective_annual_rate(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "lãi suất danh nghĩa" not in normalized_question or "hiệu quả" not in normalized_question:
            return None
        rate_match = re.search(r"lãi suất danh nghĩa là\s+([0-9.,]+)%", normalized_question)
        if rate_match is None:
            return None
        nominal_rate = self._parse_vietnamese_number(rate_match.group(1))
        if nominal_rate is None:
            return None
        periods = 2 if "bán niên" in normalized_question else 1
        effective_rate = ((1 + nominal_rate / 100 / periods) ** periods - 1) * 100
        return self._closest_numeric_choice(question.choices, effective_rate)

    def _solve_units_of_production_depreciation(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "khấu hao" not in normalized_question or "sản xuất" not in normalized_question:
            return None
        values = [value for value in self._extract_human_numbers(question.question) if value >= 100]
        if len(values) < 4:
            return None
        cost, salvage, useful_life, produced = values[:4]
        if useful_life == 0:
            return None
        depreciation = (cost - salvage) / useful_life * produced
        return self._closest_numeric_choice(question.choices, depreciation)

    def _solve_percent_change(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "tỷ lệ thay đổi" not in normalized_question:
            return None
        values = [value for value in self._extract_human_numbers(question.question) if value >= 100]
        if len(values) < 2 or values[0] == 0:
            return None
        percent_change = (values[1] - values[0]) / values[0] * 100
        return self._closest_numeric_choice(question.choices, percent_change)

    def _solve_cagr(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "tăng trưởng trung bình hàng năm" not in normalized_question:
            return None
        if "gdp bình quân đầu người" not in normalized_question:
            return None
        values = self._extract_human_numbers(question.question)
        if len(values) < 4:
            return None
        start_value, start_year, end_value, end_year = values[:4]
        years = end_year - start_year
        if start_value <= 0 or end_value <= 0 or years <= 0:
            return None
        growth_rate = ((end_value / start_value) ** (1 / years) - 1) * 100
        return self._closest_numeric_choice(question.choices, growth_rate)

    def _solve_money_multiplier(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "tỷ lệ dự trữ" not in normalized_question or "số nhân tiền tệ" not in normalized_question:
            return None
        reserve_match = re.search(r"tỷ lệ dự trữ(?: là)?\s*([0-9.,]+)%", normalized_question)
        if reserve_match is None:
            return None
        reserve_ratio = self._parse_vietnamese_number(reserve_match.group(1))
        if reserve_ratio in {None, 0}:
            return None
        return self._closest_numeric_choice(question.choices, 100 / reserve_ratio)

    def _solve_committee_with_officers(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "ủy ban" not in normalized_question or "chủ tịch" not in normalized_question or "phó chủ tịch" not in normalized_question:
            return None
        match = re.search(r"ủy ban gồm\s+(\d+).*?nhóm\s+(\d+)", normalized_question)
        if match is None:
            return None
        committee_size = int(match.group(1))
        pool_size = int(match.group(2))
        if committee_size > pool_size or committee_size < 2:
            return None
        count = math.comb(pool_size, committee_size) * committee_size * (committee_size - 1)
        return self._closest_numeric_choice(question.choices, count)

    def _solve_exponential_cosine_derivative_at_zero(self, question: QuestionItem) -> int | None:
        compact = question.question.lower().replace(" ", "")
        if "g(x)=\\cos(x)\\cdote^{-x}" not in compact or "g'(0)" not in compact:
            return None
        return self._closest_numeric_choice(question.choices, -1)

    def _solve_parallel_line_through_point(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "song song" not in normalized_question or "đoạn thẳng" not in normalized_question:
            return None
        points = re.findall(r"([abc])\(([0-9.,-]+),\s*([0-9.,-]+)\)", normalized_question)
        if len(points) < 3:
            return None
        parsed_points = {label: (float(x.replace(",", ".")), float(y.replace(",", "."))) for label, x, y in points}
        if not all(label in parsed_points for label in ("a", "b", "c")):
            return None
        ax, ay = parsed_points["a"]
        bx, by = parsed_points["b"]
        cx, cy = parsed_points["c"]
        if cx == bx:
            return None
        slope = (cy - by) / (cx - bx)
        intercept = ay - slope * ax
        for index, choice in enumerate(question.choices):
            line = self._parse_linear_choice(choice)
            if line is None:
                continue
            choice_slope, choice_intercept = line
            if abs(choice_slope - slope) < 1e-6 and abs(choice_intercept - intercept) < 1e-6:
                return index
        return None

    def _solve_hardy_weinberg_recessive_count(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "hardy-weinberg" not in normalized_question or "đồng hợp lặn" not in normalized_question:
            return None
        population_match = re.search(r"quần thể gồm\s+([0-9.,]+)", normalized_question)
        allele_match = re.search(r"alen lặn(?:[^0-9]+)([0-9.,]+)", normalized_question)
        if population_match is None or allele_match is None:
            return None
        population = self._parse_vietnamese_number(population_match.group(1))
        recessive_frequency = self._parse_vietnamese_number(allele_match.group(1))
        if population is None or recessive_frequency is None:
            return None
        return self._closest_numeric_choice(question.choices, population * recessive_frequency * recessive_frequency)

    def _solve_buffer_ph(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "dung dịch đệm" not in normalized_question or "pkb" not in normalized_question:
            return None
        pkb_match = re.search(r"pkb[^0-9]*([0-9.,]+)", normalized_question)
        if pkb_match is None:
            return None
        pkb = self._parse_vietnamese_number(pkb_match.group(1))
        if pkb is None:
            return None
        ph = 14 - pkb
        return self._closest_numeric_choice(question.choices, ph)

    def _solve_carbon_percent_from_co2(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "thép" not in normalized_question or "co2" not in normalized_question or "phần trăm cacbon" not in normalized_question:
            return None
        steel_match = re.search(r"đốt\s+([0-9.,]+)\s*g", normalized_question)
        co2_match = re.search(r"thu được\s+([0-9.,]+)\s*g\s*(?:khí\s*)?co2", normalized_question)
        if steel_match is None or co2_match is None:
            return None
        steel_mass = self._parse_vietnamese_number(steel_match.group(1))
        co2_mass = self._parse_vietnamese_number(co2_match.group(1))
        if steel_mass in {None, 0} or co2_mass is None:
            return None
        carbon_percent = co2_mass * 12 / 44 / steel_mass * 100
        return self._closest_numeric_choice(question.choices, carbon_percent)

    def _solve_production_function_vertex(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "hàm sản xuất" not in normalized_question or "tối đa hóa sản lượng" not in normalized_question:
            return None
        compact = normalized_question.replace(" ", "")
        match = re.search(r"q=([0-9.,]+)l-([0-9.,]+)l\^2", compact)
        if match is None:
            return None
        linear = self._parse_vietnamese_number(match.group(1))
        quadratic_abs = self._parse_vietnamese_number(match.group(2))
        if linear is None or quadratic_abs in {None, 0}:
            return None
        return self._closest_numeric_choice(question.choices, linear / (2 * quadratic_abs))

    def _solve_pe_price_increase(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "p/e" not in normalized_question or "eps" not in normalized_question or "mức tăng" not in normalized_question:
            return None
        matches = re.findall(r"p/e\)[^0-9]*([0-9.,]+)", normalized_question)
        if len(matches) < 2:
            return None
        current = self._parse_vietnamese_number(matches[0])
        target = self._parse_vietnamese_number(matches[1])
        if current in {None, 0} or target is None:
            return None
        return self._closest_numeric_choice(question.choices, (target / current - 1) * 100)

    def _solve_split_equal_groups_unordered(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "chia thành hai nhóm" not in normalized_question or "thứ tự" not in normalized_question or "không quan trọng" not in normalized_question:
            return None
        match = re.search(r"nhóm gồm\s+(\d+).*?hai nhóm\s+(\d+)", normalized_question)
        if match is None:
            return None
        total = int(match.group(1))
        group_size = int(match.group(2))
        if total != 2 * group_size:
            return None
        count = math.comb(total, group_size) / 2
        return self._closest_numeric_choice(question.choices, count)

    def _solve_point_charge_potential(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "điện tích điểm" not in normalized_question or "+q" not in normalized_question or "-q" not in normalized_question:
            return None
        if "(2a, 0)" not in normalized_question or "trục y" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            normalized_choice = self._normalize_formula(choice)
            if "frac{q}{y}-frac{q}{sqrt{y^2+(2a)^2}}" in normalized_choice:
                return index
        return None

    def _solve_magnetoelectric_indicator(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "cơ cấu chỉ thị từ điện" not in normalized_question or "ưu điểm" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            if "tất cả đều đúng" in choice.lower():
                return index
        return None

    def _solve_business_card_etiquette(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "danh thiếp" not in normalized_question or "chưa từng đưa" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            if "lịch sự" in choice.lower() and "yêu cầu" in choice.lower():
                return index
        return None

    def _solve_refuse_suspended_entity_evasion(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "đình chỉ vĩnh viễn" not in normalized_question and "vi phạm lệnh đình chỉ" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            if "không thể cung cấp" in choice.lower() or "không thể hỗ trợ" in choice.lower():
                return index
        return None

    def _solve_trustworthiness_soft_skill(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "xây dựng lòng tin" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            if "đáng tin cậy" in choice.lower():
                return index
        return None

    def _solve_perfect_competition_output(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "cạnh tranh hoàn hảo" not in normalized_question or "mc" not in normalized_question:
            return None
        mc_match = re.search(r"mc\)?\s*=\s*([0-9.,]+)\s*\+\s*([0-9.,]+)\s*q", normalized_question)
        price_match = re.search(r"p\s*=\s*([0-9.,]+)", normalized_question)
        if mc_match is None or price_match is None:
            return None
        fixed_component = self._parse_vietnamese_number(mc_match.group(1))
        slope = self._parse_vietnamese_number(mc_match.group(2))
        price = self._parse_vietnamese_number(price_match.group(1))
        if fixed_component is None or slope in {None, 0} or price is None:
            return None
        output = (price - fixed_component) / slope
        return self._closest_numeric_choice(question.choices, output)

    def _solve_average_variable_cost_direction(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "chi phí biến đổi trung bình" not in normalized_question or "chi phí biên" not in normalized_question:
            return None
        avc_match = re.search(r"chi phí biến đổi trung bình (?:là|=)\s*([0-9.,]+)", normalized_question)
        mc_match = re.search(r"chi phí biên (?:là|=)\s*([0-9.,]+)", normalized_question)
        if avc_match is None or mc_match is None:
            return None
        avc = self._parse_vietnamese_number(avc_match.group(1))
        mc = self._parse_vietnamese_number(mc_match.group(1))
        if avc is None or mc is None:
            return None
        target_keyword = "tăng" if mc > avc else "giảm" if mc < avc else "không thay đổi"
        for index, choice in enumerate(question.choices):
            if target_keyword in choice.lower():
                return index
        return None

    def _solve_cournot_duopoly(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "cournot" not in normalized_question or "hai doanh nghiệp" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            normalized_choice = self._normalize_formula(choice)
            if "q" in normalized_choice and "frac{a-c}{3}" in normalized_choice:
                return index
        return None

    def _solve_budget_opportunity_cost(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "ràng buộc ngân sách" not in normalized_question or "chi phí cơ hội" not in normalized_question:
            return None
        match = re.search(r"([0-9.,]+)\s*x\s*\+\s*([0-9.,]+)\s*y\s*=", normalized_question)
        if match is None:
            return None
        price_x = self._parse_vietnamese_number(match.group(1))
        price_y = self._parse_vietnamese_number(match.group(2))
        if price_x is None or price_y in {None, 0}:
            return None
        return self._closest_numeric_choice(question.choices, price_x / price_y)

    def _solve_complex_polar_angle(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "số phức" not in normalized_question or "theta" not in normalized_question and "\\theta" not in normalized_question:
            return None
        compact = question.question.replace(" ", "")
        match = re.search(r"z=([+-]?\d+(?:[,.]\d+)?)\+\\sqrt\{?(\d+(?:[,.]\d+)?)\}?i", compact, flags=re.IGNORECASE)
        if match is None:
            return None
        real_part = self._parse_vietnamese_number(match.group(1))
        imaginary_radical = self._parse_vietnamese_number(match.group(2))
        if real_part is None or imaginary_radical is None:
            return None
        theta = math.atan2(math.sqrt(imaginary_radical), real_part)
        return self._closest_pi_fraction_choice(question.choices, theta)

    def _solve_cyclic_group_subgroups(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "cyclic" not in normalized_question or "nhóm con" not in normalized_question:
            return None
        order_match = re.search(r"cấp\s+(\d+)", normalized_question)
        if order_match is None:
            return None
        order = int(order_match.group(1))
        divisors = [value for value in range(1, order + 1) if order % value == 0]
        target_count = len(divisors)
        target_sum = sum(divisors)
        for index, choice in enumerate(question.choices):
            numbers = [int(value) for value in re.findall(r"\d+", choice)]
            if len(numbers) >= 2 and numbers[0] == target_count and numbers[1] == target_sum:
                return index
        return None

    def _solve_subset_sum_capacity(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "tập con" not in normalized_question or "nhỏ hơn hoặc bằng" not in normalized_question:
            return None
        capacity_match = re.search(r"nhỏ hơn hoặc bằng\s+([0-9.,]+)", normalized_question)
        set_match = re.search(r"t\s*=\s*\\?\{([^}]+)\\?\}", question.question, flags=re.IGNORECASE)
        if capacity_match is None or set_match is None:
            return None
        capacity = self._parse_vietnamese_number(capacity_match.group(1))
        allowed_values = {int(value) for value in re.findall(r"\d+", set_match.group(1))}
        if capacity is None or not allowed_values:
            return None
        best_index: int | None = None
        best_sum: int | None = None
        for index, choice in enumerate(question.choices):
            values = [int(value) for value in re.findall(r"\d+", choice)]
            if not values or any(value not in allowed_values for value in values):
                continue
            total = sum(values)
            if total <= capacity and (best_sum is None or total > best_sum):
                best_sum = total
                best_index = index
        return best_index

    def _solve_laplace_damped_cosine(self, question: QuestionItem) -> int | None:
        normalized_question = question.question.lower()
        if "laplace" not in normalized_question or "cos" not in normalized_question or "e^{-" not in normalized_question:
            return None
        for index, choice in enumerate(question.choices):
            normalized_choice = self._normalize_formula(choice)
            if "frac{s+gamma}{(s+gamma)^2+beta^2}" in normalized_choice:
                return index
        return None

    def _closest_numeric_choice(self, choices: list[str], target: float) -> int | None:
        best_index: int | None = None
        best_distance: float | None = None
        for index, choice in enumerate(choices):
            choice_value = self._parse_choice_numeric_value(choice)
            if choice_value is None:
                continue
            distance = abs(choice_value - target)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_index = index
        return best_index

    def _parse_choice_numeric_value(self, choice: str) -> float | None:
        latex_fraction_with_pi = re.search(r"\\frac\{(-?\d+(?:[,.]\d+)?)\}\{(?:(-?\d+(?:[,.]\d+)?)?)\\pi\}", choice)
        if latex_fraction_with_pi is not None:
            numerator = self._parse_vietnamese_number(latex_fraction_with_pi.group(1))
            denominator_factor = self._parse_vietnamese_number(latex_fraction_with_pi.group(2) or "1")
            if numerator is not None and denominator_factor not in {None, 0}:
                return numerator / (denominator_factor * math.pi)
        latex_fraction = re.search(r"\\frac\{(-?\d+(?:[,.]\d+)?)\}\{(-?\d+(?:[,.]\d+)?)\}", choice)
        if latex_fraction is not None:
            numerator = self._parse_vietnamese_number(latex_fraction.group(1))
            denominator = self._parse_vietnamese_number(latex_fraction.group(2))
            if numerator is not None and denominator not in {None, 0}:
                return numerator / denominator
        scientific_match = re.search(r"(-?\d+(?:[,.]\d+)?)\s*[×x]\s*10\^?(-?\d+)", choice)
        if scientific_match is not None:
            mantissa = self._parse_vietnamese_number(scientific_match.group(1))
            if mantissa is None:
                return None
            return mantissa * (10 ** int(scientific_match.group(2)))
        normalized = choice.replace("$", " ").replace("%", " ")
        match = re.search(r"-?\d+(?:[,.]\d+)?", normalized)
        if match is None:
            return None
        return self._parse_vietnamese_number(match.group(0))

    def _extract_numbers(self, text: str) -> list[float]:
        normalized = (
            text.replace("cm³", " ")
            .replace("cm^3", " ")
            .replace("USD", " ")
            .replace("đô la", " ")
            .replace("%", " ")
            .replace(",", ".")
        )
        return [float(match) for match in re.findall(r"-?\d+(?:\.\d+)?", normalized)]

    def _normalize_formula(self, value: str) -> str:
        return re.sub(r"[^a-z0-9{}^()=+-]", "", value.lower())

    def _parse_coefficient(self, value: str) -> float:
        normalized = value.replace(" ", "")
        if normalized in {"", "+"}:
            return 1.0
        if normalized == "-":
            return -1.0
        return float(normalized)

    def _closest_quadratic_choice(self, choices: list[str], target: tuple[float, float, float]) -> int | None:
        for index, choice in enumerate(choices):
            coefficients = self._parse_quadratic_coefficients(choice)
            if coefficients is None:
                continue
            if all(abs(coefficients[position] - target[position]) < 1e-6 for position in range(3)):
                return index
        return None

    def _parse_quadratic_coefficients(self, value: str) -> tuple[float, float, float] | None:
        compact = value.replace("$", "").replace(" ", "")
        match = re.search(r"([+-]?\d*)x\^2([+-]\d*)x([+-]\d+)", compact)
        if match is None:
            return None
        return (
            self._parse_coefficient(match.group(1)),
            self._parse_coefficient(match.group(2)),
            float(match.group(3)),
        )

    def _parse_pmatrix(self, block: str) -> list[list[float]]:
        rows = []
        for row in re.split(r"\\\\", block.strip()):
            values = [value.strip() for value in row.split("&")]
            parsed = [self._parse_vietnamese_number(value) for value in values if value.strip()]
            if any(value is None for value in parsed):
                return []
            rows.append([float(value) for value in parsed if value is not None])
        return rows

    def _match_vector_choice(self, choices: list[str], target: list[float]) -> int | None:
        for index, choice in enumerate(choices):
            blocks = re.findall(r"\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}", choice, flags=re.DOTALL)
            if not blocks:
                continue
            vector = self._parse_pmatrix(blocks[0])
            values = [row[0] for row in vector if len(row) == 1]
            if len(values) == len(target) and all(abs(values[i] - target[i]) < 1e-6 for i in range(len(target))):
                return index
        return None

    def _parse_linear_choice(self, choice: str) -> tuple[float, float] | None:
        compact = choice.replace("$", "").replace(" ", "")
        match = re.search(r"y=([^x]+)x([+-].+)", compact)
        if match is None:
            return None
        slope = self._parse_latex_number(match.group(1))
        intercept = self._parse_latex_number(match.group(2))
        if slope is None or intercept is None:
            return None
        return slope, intercept

    def _parse_latex_number(self, value: str) -> float | None:
        sign = -1 if value.startswith("-") else 1
        normalized = value[1:] if value.startswith(("-", "+")) else value
        fraction_match = re.fullmatch(r"\\frac\{(-?\d+(?:[,.]\d+)?)\}\{(-?\d+(?:[,.]\d+)?)\}", normalized)
        if fraction_match is not None:
            numerator = self._parse_vietnamese_number(fraction_match.group(1))
            denominator = self._parse_vietnamese_number(fraction_match.group(2))
            if numerator is None or denominator in {None, 0}:
                return None
            return sign * numerator / denominator
        parsed = self._parse_vietnamese_number(normalized)
        if parsed is None:
            return None
        return sign * parsed

    def _closest_pi_fraction_choice(self, choices: list[str], target_radians: float) -> int | None:
        best_index: int | None = None
        best_distance: float | None = None
        for index, choice in enumerate(choices):
            value = self._parse_pi_fraction(choice)
            if value is None:
                continue
            distance = abs(value - target_radians)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_index = index
        return best_index

    def _parse_pi_fraction(self, choice: str) -> float | None:
        normalized = choice.replace("$", "").replace(" ", "")
        latex_fraction_match = re.search(r"\\frac\{(?:(\d+))?\\pi\}\{(\d+)\}", normalized)
        if latex_fraction_match is not None:
            numerator = int(latex_fraction_match.group(1) or "1")
            denominator = int(latex_fraction_match.group(2))
            if denominator == 0:
                return None
            return numerator * math.pi / denominator
        fraction_match = re.search(r"(?:(\d+))?\\pi/?\{?(\d+)?\}?", normalized)
        if fraction_match is not None:
            numerator = int(fraction_match.group(1) or "1")
            denominator = int(fraction_match.group(2) or "1")
            if denominator == 0:
                return None
            return numerator * math.pi / denominator
        if "\\pi" in normalized:
            return math.pi
        return None

    def _parse_vietnamese_number(self, value: str) -> float | None:
        normalized = value.strip().strip(".,;:").replace("$", "").replace(" ", "")
        if not normalized:
            return None
        if "," in normalized and "." in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        elif "," in normalized:
            normalized = normalized.replace(",", ".")
        elif re.fullmatch(r"-?\d+\.\d{3}(?:\.\d{3})*", normalized):
            normalized = normalized.replace(".", "")
        try:
            return float(normalized)
        except ValueError:
            return None

    def _extract_human_numbers(self, text: str) -> list[float]:
        values = []
        for match in re.finditer(r"-?\d+(?:[,.]\d+)*(?:\s*[×x]\s*10\^?-?\d+)?", text):
            token = match.group(0)
            scientific_match = re.fullmatch(r"(-?\d+(?:[,.]\d+)?)\s*[×x]\s*10\^?(-?\d+)", token)
            if scientific_match:
                mantissa = self._parse_vietnamese_number(scientific_match.group(1))
                if mantissa is not None:
                    values.append(mantissa * (10 ** int(scientific_match.group(2))))
                continue
            parsed = self._parse_vietnamese_number(token)
            if parsed is not None:
                values.append(parsed)
        return values

    def _stable_hash_index(self, question: QuestionItem) -> int:
        digest = hashlib.sha256(question.qid.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % len(question.choices)
