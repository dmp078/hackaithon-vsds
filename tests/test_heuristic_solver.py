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
