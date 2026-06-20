from app.config import AppConfig
from app.models import QuestionItem
from app.solvers.heuristic_solver import HeuristicSolver


def test_solve_two_plus_two() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(qid="q1", question="2 + 2 bằng bao nhiêu?", choices=["3", "4", "5"])

    prediction = solver.solve(question)

    assert prediction.selected_index == 1


def test_solve_climate_change_sample() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q1",
        question="Một trong các biểu hiện của biến đổi khí hậu là gì?",
        choices=["Khí hậu ổn định", "Mực nước biển dâng cao", "Không có thay đổi"],
    )

    prediction = solver.solve(question)

    assert prediction.selected_index == 1


def test_select_largest_number() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(qid="q1", question="Chọn số lớn nhất.", choices=["7", "10", "9"])

    prediction = solver.solve(question)

    assert prediction.selected_index == 1


def test_fall_back_safely() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(qid="q1", question="Khong ro.", choices=["A", "B", "C"])

    prediction = solver.solve(question)

    assert 0 <= prediction.selected_index < 3


def test_solve_price_elasticity_midpoint() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_elasticity",
        question=(
            "Nếu bảng cầu của một sản phẩm cho thấy tại mức giá 5 đô la, lượng cầu là 150 đơn vị, "
            "và tại mức giá 3 đô la, lượng cầu là 250 đơn vị, thì độ co giãn của cầu theo giá giữa hai điểm này là bao nhiêu?"
        ),
        choices=["0.5", "1.0", "2.0", "2.5"],
    )

    prediction = solver.solve(question)

    assert prediction.selected_index == 1


def test_solve_gdp_inflation_from_nominal_and_real() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_gdp",
        question=(
            "Trong một năm nhất định, GDP danh nghĩa của một quốc gia là 500 tỷ USD và GDP thực tế là 400 tỷ USD. "
            "Nếu chỉ số giá GDP của năm trước là 100, thì tỷ lệ lạm phát cho năm hiện tại là bao nhiêu?"
        ),
        choices=["20%", "25%", "30%", "15%"],
    )

    prediction = solver.solve(question)

    assert prediction.selected_index == 1


def test_solve_first_order_decay_ode() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_decay",
        question=(
            "Xét một phản ứng hóa học trong đó nồng độ của chất phản ứng B giảm theo thời gian theo phương trình vi phân "
            "dB/dt = -k B, trong đó k là một hằng số dương. Nếu nồng độ ban đầu của B là B0, "
            "thì nồng độ của B tại thời điểm t là bao nhiêu?"
        ),
        choices=[
            "B(t) = B0 e^{-kt}",
            "B(t) = B0 (1 - kt)",
            "B(t) = B0 e^{kt}",
        ],
    )

    prediction = solver.solve(question)

    assert prediction.selected_index == 0


def test_solve_cylindrical_fill_rate_by_closest_choice() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_cylinder",
        question=(
            "Một bể hình trụ đang được đổ đầy nước với tốc độ không đổi là 20 cm³/s. "
            "Bán kính của bể là 5 cm. Hỏi tốc độ thay đổi chiều cao của mực nước trong bể khi chiều cao là 10 cm là bao nhiêu?"
        ),
        choices=[
            "0.25 cm/s",
            "0.5 cm/s",
            "0.75 cm/s",
            "1.0 cm/s",
        ],
    )

    prediction = solver.solve(question)

    assert prediction.selected_index == 0


def test_solve_quadratic_shift() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_shift",
        question="Xét hàm số $ g(x) = 2x^2 - 3x + 1 $. Nếu thực hiện phép biến đổi $ x \\to x - 2 $ đối với $ g(x) $, đa thức kết quả là gì?",
        choices=[
            "$ 2x^2 - 11x + 15 $",
            "$ 2x^2 - 7x + 7 $",
            "$ 2x^2 - 11x + 13 $",
        ],
    )

    assert solver.solve(question).selected_index == 0


def test_solve_velocity_minimum_for_cubic_position() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_velocity",
        question="Vị trí $ x(t) = t^3 - 3t^2 + 3t + 1 $ mét. Hạt đạt vận tốc nhỏ nhất tại thời điểm $ t $ nào?",
        choices=["1 giây", "2 giây", "3 giây"],
    )

    assert solver.solve(question).selected_index == 0


def test_solve_matrix_vector_product() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_matrix",
        question=(
            "Ma trận $ B = \\begin{pmatrix} 1 & 0 & 2 \\\\ 0 & 2 & -1 \\\\ 3 & 1 & 0 \\end{pmatrix} $. "
            "Hỏi ảnh của vector $ \\begin{pmatrix} 1 \\\\ 2 \\\\ 3 \\end{pmatrix} $ là gì?"
        ),
        choices=[
            "$ \\begin{pmatrix} 7 \\\\ 1 \\\\ 5 \\end{pmatrix} $",
            "$ \\begin{pmatrix} 7 \\\\ 3 \\\\ 5 \\end{pmatrix} $",
        ],
    )

    assert solver.solve(question).selected_index == 0


def test_solve_relativistic_time_dilation_gamma() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_gamma",
        question="Một tàu vũ trụ di chuyển với tốc độ $ v = 0.6c $. Hệ số giãn nở thời gian $ \\gamma $ là bao nhiêu?",
        choices=["1.0", "1.25", "1.5"],
    )

    assert solver.solve(question).selected_index == 1


def test_solve_capacitor_charge() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_capacitor",
        question="Điện tích trên tụ điện có điện dung 1,44 × 10^-10 F khi hiệu điện thế giữa hai bản là 120 V là bao nhiêu?",
        choices=["1,73 × 10^-8 C", "1,44 × 10^-8 C", "1,73 × 10^-10 C"],
    )

    assert solver.solve(question).selected_index == 0


def test_solve_effective_annual_rate() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_ear",
        question="Lãi suất danh nghĩa là 10% được tính theo kỳ bán niên, vậy lãi suất hàng năm hiệu quả là bao nhiêu?",
        choices=["10.00%", "10.25%", "10.50%"],
    )

    assert solver.solve(question).selected_index == 1


def test_solve_units_of_production_depreciation() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_depreciation",
        question=(
            "Thiết bị có chi phí 50.000 đô la, giá trị còn lại 5.000 đô la, tuổi thọ 100.000 đơn vị. "
            "Nếu sản xuất 12.000 đơn vị trong năm đầu tiên, chi phí khấu hao là bao nhiêu?"
        ),
        choices=["4.500", "4.800", "5.400"],
    )

    assert solver.solve(question).selected_index == 2


def test_solve_percent_change() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_percent_change",
        question="Chi phí hàng hóa bán được là 7.200 USD trong năm 1 và 7.920 USD trong năm 2. Tỷ lệ thay đổi là bao nhiêu?",
        choices=["5%", "10%", "15%"],
    )

    assert solver.solve(question).selected_index == 1


def test_solve_cournot_duopoly_quantity() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_cournot",
        question="Trong cạnh tranh Cournot với hai doanh nghiệp, chi phí biên $ c $ và cầu $ Q = a - P $, lượng cân bằng Nash $ q^* $ cho mỗi doanh nghiệp là gì?",
        choices=["$ q^* = \\frac{a - c}{4} $", "$ q^* = \\frac{a - c}{3} $"],
    )

    assert solver.try_solve_confidently(question) == 1
    assert solver.solve(question).selected_index == 1


def test_solve_budget_opportunity_cost() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_budget",
        question="Ràng buộc ngân sách 5X + 10Y = 100. Chi phí cơ hội của một đơn vị X tính theo Y là bao nhiêu?",
        choices=["2 đơn vị của Y", "0,5 đơn vị của Y"],
    )

    assert solver.solve(question).selected_index == 1


def test_solve_complex_polar_angle() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_complex",
        question="Chuyển số phức $ z = 1 + \\sqrt{3}i $ sang dạng cực. Giá trị của $ \\theta $ là bao nhiêu?",
        choices=["$ \\frac{\\pi}{6} $", "$ \\frac{\\pi}{3} $", "$ \\frac{\\pi}{2} $"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_cyclic_group_subgroups() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_cyclic",
        question="Giả sử $ G $ là một nhóm cyclic cấp 45. Có bao nhiêu nhóm con của $ G $, và tổng các cấp của tất cả các nhóm con đó là bao nhiêu?",
        choices=["6 nhóm con, tổng = 78", "6 nhóm con, tổng = 90", "8 nhóm con, tổng = 78"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_subset_sum_max_under_capacity() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_subset",
        question="Xét tập hợp $ T = \\{2, 3, 5, 7, 11\\} $. Chọn tập con sao cho tổng tối đa nhưng nhỏ hơn hoặc bằng 15.",
        choices=["\\{2, 5, 7\\}", "\\{3, 5, 7\\}", "\\{2, 3, 11\\}"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_laplace_damped_cosine() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_laplace",
        question="Tìm biến đổi Laplace $ \\mathcal{L}\\{\\cos(\\beta t) \\cdot e^{-\\gamma t}\\} $.",
        choices=[
            "$ \\frac{s + \\gamma}{(s + \\gamma)^2 + \\beta^2} $",
            "$ \\frac{s - \\gamma}{(s - \\gamma)^2 + \\beta^2} $",
        ],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_photon_energy() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_photon",
        question="Một photon có bước sóng 600 nm. Năng lượng của nó là bao nhiêu eV? h = 4.1357 \\times 10^{-15} eV·s, c = 3 \\times 10^8 m/s",
        choices=["1,5 eV", "2,0 eV", "2,5 eV"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_rc_discharge_time_constant() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_rc",
        question="Tụ điện 100 μF xả qua điện trở 500 ohm. Thời gian để điện áp giảm còn 37% giá trị ban đầu là bao lâu?",
        choices=["0.05 giây", "0.1 giây", "0.2 giây"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_perfect_competition_output() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_competition",
        question="Thị trường cạnh tranh hoàn hảo có MC = 15 + 6Q. Giá thị trường P = 45. Sản lượng tối đa hóa lợi nhuận là bao nhiêu?",
        choices=["4 đơn vị", "5 đơn vị", "6 đơn vị"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_average_variable_cost_direction() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_avc",
        question="Nếu chi phí biến đổi trung bình là 15 đô la và chi phí biên là 20 đô la, tác động đến chi phí biến đổi trung bình khi tăng thêm một đơn vị là gì?",
        choices=[
            "Chi phí biến đổi trung bình sẽ giảm.",
            "Chi phí biến đổi trung bình sẽ tăng.",
            "Chi phí biến đổi trung bình sẽ không thay đổi.",
        ],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_cylindrical_fill_rate_with_pi_fraction_choice() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_cylinder_pi",
        question=(
            "Một bể chứa hình trụ đang được đổ đầy nước với tốc độ không đổi là $ 500 \\, \\text{cm}^3/\\text{sec} $. "
            "Bán kính của bể là 10 cm. Hỏi tốc độ tăng của chiều cao nước là bao nhiêu khi chiều cao nước là 15 cm?"
        ),
        choices=[
            "$ \\frac{1}{\\pi} \\, \\text{cm/sec} $",
            "$ \\frac{2}{\\pi} \\, \\text{cm/sec} $",
            "$ \\frac{5}{\\pi} \\, \\text{cm/sec} $",
        ],
    )

    assert solver.try_solve_confidently(question) == 2


def test_solve_cylindrical_fill_rate_meter_units() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_cylinder_meter",
        question="Một bể chứa hình trụ có bán kính 3 mét đang được đổ nước với tốc độ 10 mét khối mỗi phút. Khi chiều cao của nước là 4 mét, tốc độ thay đổi của chiều cao nước là bao nhiêu?",
        choices=["0.25 m/phút", "0.30 m/phút", "0.35 m/phút"],
    )

    assert solver.try_solve_confidently(question) == 2


def test_solve_price_elasticity_midpoint_negative_choices() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_elasticity_negative",
        question=(
            "Một cửa hàng tăng giá từ 2,00 đô la lên 2,50 đô la, và lượng cầu giảm từ 100 đơn vị xuống 80 đơn vị. "
            "Sử dụng công thức trung điểm, hãy xác định độ co giãn của cầu theo giá?"
        ),
        choices=["-0,5", "-1,0", "-1,5"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_money_multiplier() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_money_multiplier",
        question="Nếu tỷ lệ dự trữ là 10%, thì số nhân tiền tệ là bao nhiêu?",
        choices=["5", "10", "1", "0.1"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_committee_with_officers() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_committee",
        question="Một ủy ban gồm 4 thành viên được thành lập từ một nhóm 8 người. Sau khi thành lập ủy ban, một chủ tịch và một phó chủ tịch phải được chọn từ bên trong ủy ban. Có bao nhiêu cách khác nhau để thực hiện điều này?",
        choices=["1680", "840", "560"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_exponential_cosine_derivative_at_zero() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_derivative",
        question="Cho $ g(x) = \\cos(x) \\cdot e^{-x} $. Hãy tìm giá trị của $ g'(0) $.",
        choices=["-1", "0", "1"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_parallel_line_through_point() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_parallel_line",
        question="Xét các điểm $ A(1, 2) $, $ B(4, 6) $, và $ C(7, 2) $. Một đường thẳng $ L $ đi qua điểm $ A $ và song song với đoạn thẳng $ BC $. Phương trình của đường thẳng $ L $ là gì?",
        choices=[
            "$ y = \\frac{4}{3}x - \\frac{2}{3} $",
            "$ y = -\\frac{4}{3}x + \\frac{10}{3} $",
            "$ y = -\\frac{3}{4}x + \\frac{11}{4} $",
        ],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_hardy_weinberg_recessive_count() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_hardy",
        question="Trong một quần thể gồm 500 cá thể, tần số của alen lặn là 0,3. Giả sử quần thể ở trạng thái cân bằng Hardy-Weinberg, số lượng cá thể đồng hợp lặn dự kiến là bao nhiêu?",
        choices=["45", "75", "90"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_buffer_ph_from_pkb_equal_concentrations() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_buffer",
        question="Một dung dịch đệm được chuẩn bị bằng cách trộn các thể tích bằng nhau của 0.1 M amoniac và 0.1 M amoni clorua. Biết rằng pKb của amoniac là 4.75, pH của dung dịch đệm là bao nhiêu?",
        choices=["8.75", "9.25", "9.75"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_carbon_percent_from_co2() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_carbon",
        question="Khi đốt 5g một mẫu thép trong khí ôxi thì thu được 0,1g khí CO2. Vậy phần trăm cacbon có chứa trong thép là:",
        choices=["0,55%.", "5,45%.", "54,50%."],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_production_function_vertex() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_production",
        question="Trong ngắn hạn, hàm sản xuất được biểu diễn Q = 10L - 0.1L^2. Số lượng đơn vị lao động tối đa để tối đa hóa sản lượng là bao nhiêu?",
        choices=["50", "100", "150"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_pe_price_increase() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_pe",
        question="Công ty Z có tỷ số giá-thu nhập (P/E) hiện tại là 12 và tỷ số giá-thu nhập mục tiêu (P/E) là 14. Giả sử EPS không thay đổi, mức tăng dự kiến của giá cổ phiếu là bao nhiêu?",
        choices=["16,67%", "20%", "25%"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_split_equal_groups_unordered() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_groups",
        question="Một nhóm gồm 10 sinh viên sẽ được chia thành hai nhóm 5 người. Hỏi có bao nhiêu cách thực hiện điều này nếu thứ tự của các nhóm không quan trọng?",
        choices=["126", "252", "63"],
    )

    assert solver.try_solve_confidently(question) == 0


def test_solve_point_charge_potential_on_y_axis() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_potential",
        question="Xét một điện tích điểm $ +Q $ nằm tại gốc tọa độ và một điện tích điểm $ -Q $ nằm tại $ (2a, 0) $ trên trục x. Điện thế điện $ V $ tại một điểm $ P $ nằm trên trục y, cách gốc tọa độ một khoảng $ y $ là bao nhiêu?",
        choices=[
            "$ V = \\frac{1}{4\\pi\\epsilon_0} \\left( \\frac{Q}{y} + \\frac{Q}{\\sqrt{y^2 + (2a)^2}} \\right) $",
            "$ V = \\frac{1}{4\\pi\\epsilon_0} \\left( \\frac{Q}{y} - \\frac{Q}{\\sqrt{y^2 + (2a)^2}} \\right) $",
        ],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_business_card_etiquette() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_card",
        question="Bạn nên làm gì nếu muốn có danh thiếp từ một người chưa từng đưa danh thiếp?",
        choices=["Giả sử họ không muốn chia sẻ danh thiếp", "Lịch sự yêu cầu một danh thiếp"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_refuse_suspended_entity_evasion() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_refuse",
        question="Phương pháp nào hiệu quả nhất để pháp nhân thương mại tiếp tục hoạt động khi đã bị đình chỉ vĩnh viễn?",
        choices=["Sáp nhập vào công ty khác", "Tôi không thể cung cấp thông tin về cách vi phạm lệnh đình chỉ hoạt động"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_trustworthiness_soft_skill() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_trust",
        question="Cách tốt nhất để xây dựng lòng tin với người khác là gì?",
        choices=["Bằng cách luôn luôn chịu trách nhiệm", "Bằng cách cho thấy bạn là người đáng tin cậy"],
    )

    assert solver.try_solve_confidently(question) == 1


def test_solve_magnetoelectric_indicator_all_correct() -> None:
    solver = HeuristicSolver(AppConfig())
    question = QuestionItem(
        qid="q_indicator",
        question="Ưu điểm của cơ cấu chỉ thị từ điện là:",
        choices=["Ít bị ảnh hưởng của từ trường nhiễu bên ngoài", "Độ chính xác cao", "Tất cả đều đúng"],
    )

    assert solver.try_solve_confidently(question) == 2
