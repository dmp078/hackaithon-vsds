from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def make_doc(
    category: str,
    topic: str,
    title: str,
    keywords: list[str],
    explanation: str,
    formulas: str = "",
    definitions: str = "",
) -> dict[str, object]:
    content_parts = [f"Giải thích ngắn: {explanation}"]
    if formulas:
        content_parts.append(f"Công thức: {formulas}")
    if definitions:
        content_parts.append(f"Định nghĩa quan trọng: {definitions}")
    content_parts.append(f"Từ khóa gợi ý: {', '.join(keywords)}")
    return {
        "id": f"{category}__{topic}",
        "category": category,
        "topic": topic,
        "title": title,
        "keywords": keywords,
        "content": "\n".join(content_parts),
    }


def build_documents() -> list[dict[str, object]]:
    docs: list[dict[str, object]] = []

    docs.extend(
        [
            make_doc("mathematics", "quadratic_formula", "Công thức nghiệm phương trình bậc hai", ["parabol", "delta", "nghiệm"], "Phương trình ax^2 + bx + c = 0 có nghiệm phụ thuộc vào biệt thức delta.", "x = (-b ± √Δ)/(2a), Δ = b^2 - 4ac", "Δ > 0 có hai nghiệm phân biệt; Δ = 0 nghiệm kép; Δ < 0 không có nghiệm thực."),
            make_doc("mathematics", "vieta", "Hệ thức Viète", ["nghiệm", "tổng", "tích"], "Liên hệ tổng và tích nghiệm của phương trình bậc hai với hệ số.", "x1 + x2 = -b/a, x1x2 = c/a", "Dùng để dựng phương trình khi biết nghiệm hoặc biến đổi biểu thức đối xứng."),
            make_doc("mathematics", "arithmetic_progression", "Cấp số cộng", ["dãy số", "công sai", "tổng"], "Mỗi số hạng sau bằng số trước cộng công sai d.", "u_n = u_1 + (n-1)d; S_n = n(u_1 + u_n)/2", "Công sai d không đổi."),
            make_doc("mathematics", "geometric_progression", "Cấp số nhân", ["công bội", "dãy số", "tổng"], "Mỗi số hạng sau bằng số trước nhân công bội q.", "u_n = u_1 q^(n-1); S_n = u_1(q^n - 1)/(q - 1), q ≠ 1", "Công bội q không đổi."),
            make_doc("mathematics", "derivative_rules", "Các quy tắc đạo hàm cơ bản", ["đạo hàm", "quy tắc", "vi phân"], "Đạo hàm đo tốc độ thay đổi tức thời của hàm số.", "(u+v)' = u' + v'; (uv)' = u'v + uv'; (u/v)' = (u'v - uv')/v^2", "Đạo hàm của hằng số bằng 0; đạo hàm của x^n bằng nx^(n-1)."),
            make_doc("mathematics", "integral_basics", "Nguyên hàm và tích phân cơ bản", ["nguyên hàm", "tích phân", "diện tích"], "Nguyên hàm là hàm có đạo hàm bằng hàm đã cho.", "∫x^n dx = x^(n+1)/(n+1) + C; ∫1/x dx = ln|x| + C", "Tích phân xác định liên hệ với diện tích có dấu dưới đồ thị."),
            make_doc("mathematics", "trigonometric_identities", "Đẳng thức lượng giác cơ bản", ["sin", "cos", "tan"], "Dùng để rút gọn và biến đổi biểu thức lượng giác.", "sin^2x + cos^2x = 1; tan x = sin x / cos x; 1 + tan^2x = 1/cos^2x", "Chú ý điều kiện xác định của tan và cot."),
            make_doc("mathematics", "logarithm_laws", "Quy tắc logarit", ["log", "mũ", "biến đổi"], "Logarit biến phép nhân thành phép cộng.", "log_a(xy)=log_a x + log_a y; log_a(x/y)=log_a x - log_a y; log_a x^n = n log_a x", "a > 0, a ≠ 1, x > 0."),
            make_doc("mathematics", "exponent_rules", "Quy tắc lũy thừa", ["số mũ", "nhân", "chia"], "Các quy tắc lũy thừa giúp rút gọn biểu thức mũ.", "a^m a^n = a^(m+n); a^m / a^n = a^(m-n); (a^m)^n = a^(mn)", "a ≠ 0 khi chia lũy thừa."),
            make_doc("mathematics", "determinant_2x2", "Định thức ma trận 2x2", ["ma trận", "định thức"], "Định thức cho biết ma trận có khả nghịch hay không.", "det([[a,b],[c,d]]) = ad - bc", "Ma trận 2x2 khả nghịch khi ad - bc ≠ 0."),
            make_doc("mathematics", "binomial_theorem", "Khai triển nhị thức Newton", ["tổ hợp", "khai triển"], "Khai triển (a+b)^n thành tổng các hạng chứa hệ số tổ hợp.", "(a+b)^n = Σ C(n,k)a^(n-k)b^k", "Hệ số C(n,k) = n!/[k!(n-k)!]."),
            make_doc("mathematics", "distance_formula", "Khoảng cách trong mặt phẳng tọa độ", ["tọa độ", "khoảng cách"], "Khoảng cách giữa hai điểm dùng định lý Pythagoras.", "d = √[(x2-x1)^2 + (y2-y1)^2]", "Trung điểm M của AB có tọa độ ((x1+x2)/2, (y1+y2)/2)."),
            make_doc("mathematics", "circle_equation", "Phương trình đường tròn", ["hình học giải tích", "bán kính"], "Đường tròn tâm I(a,b), bán kính R có dạng chuẩn.", "(x-a)^2 + (y-b)^2 = R^2", "R > 0, tâm là điểm cách đều mọi điểm trên đường tròn."),
            make_doc("mathematics", "probability_rules", "Quy tắc xác suất cơ bản", ["biến cố", "xác suất"], "Xác suất kết hợp và điều kiện thường xuất hiện trong câu hỏi tổ hợp-xác suất.", "P(A∪B)=P(A)+P(B)-P(A∩B); P(A|B)=P(A∩B)/P(B)", "Biến cố độc lập khi P(A∩B)=P(A)P(B)."),
            make_doc("mathematics", "statistics_central_tendency", "Trung bình, trung vị, mốt", ["thống kê", "trung bình"], "Các thước đo xu hướng trung tâm mô tả phân bố dữ liệu.", "Mean = tổng giá trị / số phần tử", "Trung vị là giá trị giữa sau khi sắp xếp; mốt là giá trị xuất hiện nhiều nhất."),
            make_doc("mathematics", "standard_deviation", "Phương sai và độ lệch chuẩn", ["phân tán", "thống kê"], "Đo mức độ phân tán của dữ liệu quanh giá trị trung bình.", "Var = Σ(x_i-μ)^2 / n; SD = √Var", "Độ lệch chuẩn lớn nghĩa là dữ liệu phân tán mạnh."),
        ]
    )

    docs.extend(
        [
            make_doc("physics_engineering", "newton_laws", "Ba định luật Newton", ["lực", "gia tốc", "quán tính"], "Ba định luật Newton mô tả chuyển động của vật dưới tác dụng lực.", "F = ma", "Định luật I nói về quán tính; định luật III nói về lực và phản lực."),
            make_doc("physics_engineering", "kinematics_linear", "Phương trình động học thẳng biến đổi đều", ["gia tốc", "vận tốc", "quãng đường"], "Liên hệ giữa vận tốc, gia tốc, thời gian và quãng đường.", "v = v0 + at; s = v0 t + 1/2 at^2; v^2 = v0^2 + 2as", "Áp dụng khi gia tốc không đổi."),
            make_doc("physics_engineering", "momentum", "Động lượng và xung lượng", ["va chạm", "bảo toàn"], "Động lượng là đại lượng vector liên quan khối lượng và vận tốc.", "p = mv; FΔt = Δp", "Trong hệ cô lập, tổng động lượng được bảo toàn."),
            make_doc("physics_engineering", "work_energy", "Công và động năng", ["năng lượng", "công cơ học"], "Công của lực bằng độ biến thiên động năng.", "W = Fs cosθ; K = 1/2 mv^2; W_net = ΔK", "Dấu của công phụ thuộc hướng lực so với chuyển dời."),
            make_doc("physics_engineering", "power", "Công suất", ["công", "năng lượng"], "Công suất là tốc độ thực hiện công.", "P = W/t = Fv cosθ", "Đơn vị SI là watt."),
            make_doc("physics_engineering", "gravitation", "Định luật vạn vật hấp dẫn", ["lực hấp dẫn", "quỹ đạo"], "Hai vật hút nhau với lực tỉ lệ thuận tích khối lượng và nghịch đảo bình phương khoảng cách.", "F = Gm1m2/r^2", "Gia tốc trọng trường gần mặt đất là g ≈ 9,8 m/s^2."),
            make_doc("physics_engineering", "coulomb", "Định luật Coulomb", ["điện tích", "lực điện"], "Lực giữa hai điện tích điểm trong chân không.", "F = k|q1q2|/r^2", "Cùng dấu đẩy nhau, khác dấu hút nhau."),
            make_doc("physics_engineering", "electric_field", "Điện trường và điện thế", ["điện trường", "điện thế"], "Điện trường cho lực trên đơn vị điện tích dương thử.", "E = F/q; V = W/q; E = kq/r^2", "Điện thế là đại lượng vô hướng, điện trường là vector."),
            make_doc("physics_engineering", "ohm_law", "Định luật Ohm", ["điện trở", "cường độ dòng điện"], "Quan hệ giữa hiệu điện thế, cường độ dòng điện và điện trở.", "V = IR", "Trong mạch thuần trở, công suất P = VI = I^2R = V^2/R."),
            make_doc("physics_engineering", "circuits_series_parallel", "Mạch nối tiếp và song song", ["điện trở tương đương", "mạch điện"], "Quy tắc cộng điện trở và dòng điện trong mạch cơ bản.", "R_nt = R1 + R2 + ...; 1/R_ss = 1/R1 + 1/R2 + ...", "Nối tiếp: dòng như nhau; song song: hiệu điện thế như nhau."),
            make_doc("physics_engineering", "capacitor", "Tụ điện", ["điện dung", "năng lượng điện trường"], "Tụ điện tích trữ điện tích và năng lượng.", "Q = CV; U = 1/2 CV^2 = Q^2/(2C)", "Điện dung của tụ phẳng tỉ lệ với diện tích bản và nghịch với khoảng cách."),
            make_doc("physics_engineering", "wave_speed", "Vận tốc truyền sóng", ["tần số", "bước sóng"], "Quan hệ giữa vận tốc, tần số và bước sóng.", "v = fλ", "Sóng mang năng lượng nhưng không mang vật chất theo phương truyền."),
            make_doc("physics_engineering", "lens_formula", "Công thức thấu kính mỏng", ["quang học", "tiêu cự"], "Liên hệ giữa vị trí vật, ảnh và tiêu cự.", "1/f = 1/d_o + 1/d_i; m = -d_i/d_o", "Dấu của tiêu cự phụ thuộc loại thấu kính."),
            make_doc("physics_engineering", "pressure", "Áp suất và lực đẩy Archimedes", ["chất lỏng", "áp lực"], "Áp suất và lực nổi thường gặp trong bài thủy tĩnh học.", "p = F/S; p = ρgh; F_A = ρgV", "Vật nổi khi lực đẩy Archimedes cân bằng trọng lượng."),
            make_doc("physics_engineering", "thermodynamics_first_law", "Nguyên lý I nhiệt động lực học", ["nhiệt lượng", "nội năng"], "Biến thiên nội năng bằng nhiệt lượng truyền vào trừ công do hệ thực hiện.", "ΔU = Q - W", "Quy ước dấu cần nhất quán theo đề bài."),
            make_doc("physics_engineering", "photon_energy", "Năng lượng photon", ["lượng tử", "ánh sáng"], "Năng lượng photon tỉ lệ với tần số ánh sáng.", "E = hf = hc/λ", "h là hằng số Planck."),
        ]
    )

    docs.extend(
        [
            make_doc("chemistry", "mole_concept", "Khái niệm mol", ["avogadro", "khối lượng mol"], "Mol liên hệ số hạt, khối lượng và thể tích khí ở điều kiện chuẩn.", "n = m/M = N/N_A", "Một mol chứa N_A ≈ 6,022×10^23 hạt."),
            make_doc("chemistry", "ideal_gas", "Phương trình khí lý tưởng", ["áp suất", "thể tích", "nhiệt độ"], "Mô tả trạng thái khí lý tưởng.", "PV = nRT", "Nhiệt độ tuyệt đối tính theo kelvin."),
            make_doc("chemistry", "ph_poh", "pH và pOH", ["axit", "bazơ", "nồng độ"], "pH đo độ axit-bazơ của dung dịch.", "pH = -log[H+]; pOH = -log[OH-]; pH + pOH = 14", "Áp dụng gần đúng ở 25°C cho dung dịch nước loãng."),
            make_doc("chemistry", "henderson_hasselbalch", "Phương trình Henderson-Hasselbalch", ["buffer", "đệm"], "Dùng để tính pH dung dịch đệm axit yếu/base liên hợp.", "pH = pKa + log([A-]/[HA])", "Dung dịch đệm chống lại sự thay đổi pH khi thêm ít axit hoặc bazơ."),
            make_doc("chemistry", "acid_base_strength", "Axit mạnh, bazơ mạnh và yếu", ["phân ly", "độ mạnh"], "Axit/bazơ mạnh phân ly gần như hoàn toàn trong nước.", "K_a = [H+][A-]/[HA]; K_b = [BH+][OH-]/[B]", "pKa nhỏ hơn thường biểu thị axit mạnh hơn."),
            make_doc("chemistry", "redox_oxidation_numbers", "Số oxi hóa và phản ứng oxi hóa-khử", ["electron", "oxi hóa", "khử"], "Theo dõi sự trao đổi electron trong phản ứng.", "Chất oxi hóa nhận e; chất khử nhường e", "Tổng số oxi hóa bằng điện tích toàn phần của phân tử/ion."),
            make_doc("chemistry", "equilibrium_constant", "Hằng số cân bằng", ["cân bằng hóa học", "Kc"], "Tỷ số giữa tích nồng độ sản phẩm và chất phản ứng ở trạng thái cân bằng.", "K_c = [C]^c[D]^d / [A]^a[B]^b", "Chỉ đưa chất khí, chất tan vào biểu thức khi thích hợp."),
            make_doc("chemistry", "le_chatelier", "Nguyên lý Le Chatelier", ["dịch chuyển cân bằng"], "Hệ cân bằng dịch chuyển để chống lại tác động bên ngoài.", "Tăng nồng độ chất phản ứng thường đẩy cân bằng theo chiều thuận", "Xét riêng ảnh hưởng của nhiệt độ, áp suất, nồng độ."),
            make_doc("chemistry", "gibbs_free_energy", "Năng lượng tự do Gibbs", ["tự diễn biến", "nhiệt động học"], "Điều kiện tự diễn biến của phản ứng ở T, P không đổi.", "ΔG = ΔH - TΔS", "ΔG < 0 tự diễn biến; ΔG = 0 cân bằng."),
            make_doc("chemistry", "hess_law", "Định luật Hess", ["enthalpy", "nhiệt phản ứng"], "Độ biến thiên enthalpy chỉ phụ thuộc trạng thái đầu-cuối.", "ΔH_rxn = ΣΔH_f(products) - ΣΔH_f(reactants)", "Có thể cộng/trừ các phương trình nhiệt hóa học để suy ra phản ứng cần tính."),
            make_doc("chemistry", "arrhenius_equation", "Phương trình Arrhenius", ["tốc độ phản ứng", "năng lượng hoạt hóa"], "Mô tả ảnh hưởng của nhiệt độ lên hằng số tốc độ.", "k = A e^(-E_a/RT)", "Tăng nhiệt độ thường làm tăng tốc độ phản ứng."),
            make_doc("chemistry", "solubility_product", "Tích số tan Ksp", ["kết tủa", "độ tan"], "Dùng để xét độ tan của muối ít tan.", "K_sp = [M^m+]^a [X^n-]^b", "Khi Q > K_sp, kết tủa có xu hướng hình thành."),
            make_doc("chemistry", "faraday_law", "Định luật Faraday điện phân", ["điện phân", "điện lượng"], "Khối lượng chất tạo ra ở điện cực tỉ lệ với điện lượng đi qua.", "Q = It; n_e = Q/F", "F ≈ 96485 C/mol electron."),
            make_doc("chemistry", "periodic_trends", "Xu hướng tuần hoàn", ["bán kính nguyên tử", "độ âm điện"], "Các tính chất biến đổi có quy luật theo chu kỳ và nhóm.", "Bán kính giảm dần theo chu kỳ, tăng theo nhóm", "Độ âm điện tăng theo chu kỳ, giảm theo nhóm."),
            make_doc("chemistry", "hybridization", "Lai hóa orbital", ["sp", "sp2", "sp3"], "Lai hóa giúp dự đoán hình học phân tử.", "sp: thẳng; sp2: tam giác phẳng; sp3: tứ diện", "Đếm miền electron quanh nguyên tử trung tâm để suy luận."),
            make_doc("chemistry", "organic_functional_groups", "Nhóm chức hữu cơ cơ bản", ["ancol", "andehit", "axit cacboxylic"], "Nhóm chức quyết định tính chất hóa học đặc trưng của hợp chất hữu cơ.", "Ancol: -OH; Andehit: -CHO; Xeton: >C=O; Axit cacboxylic: -COOH", "Nhận diện nhóm chức giúp dự đoán phản ứng."),
        ]
    )

    docs.extend(
        [
            make_doc("economics_finance", "demand_law", "Luật cầu", ["cầu", "giá"], "Khi các yếu tố khác không đổi, giá tăng thường làm lượng cầu giảm.", "Q_d = f(P, thu nhập, thị hiếu,...)", "Đường cầu thường dốc xuống."),
            make_doc("economics_finance", "supply_law", "Luật cung", ["cung", "giá"], "Giá tăng thường khuyến khích nhà sản xuất cung nhiều hơn.", "Q_s = f(P, công nghệ, chi phí đầu vào,...)", "Đường cung thường dốc lên."),
            make_doc("economics_finance", "price_elasticity_demand", "Độ co giãn cầu theo giá", ["co giãn", "midpoint"], "Đo mức độ phản ứng của lượng cầu khi giá thay đổi.", "E_d = (%ΔQ)/(%ΔP)", "|E_d| > 1 cầu co giãn; |E_d| < 1 cầu kém co giãn."),
            make_doc("economics_finance", "price_elasticity_supply", "Độ co giãn cung theo giá", ["co giãn", "cung"], "Đo mức độ phản ứng của lượng cung với biến động giá.", "E_s = (%ΔQ_s)/(%ΔP)", "Nguồn lực linh hoạt thường làm cung co giãn hơn."),
            make_doc("economics_finance", "gdp_nominal_real", "GDP danh nghĩa và GDP thực", ["gdp", "giảm phát"], "GDP danh nghĩa dùng giá hiện hành; GDP thực loại bỏ ảnh hưởng giá.", "Deflator = GDP danh nghĩa / GDP thực × 100", "GDP thực phản ánh thay đổi sản lượng tốt hơn."),
            make_doc("economics_finance", "inflation_cpi", "Lạm phát và CPI", ["cpi", "mức giá"], "Lạm phát là tốc độ tăng mức giá chung theo thời gian.", "Inflation = (CPI_t - CPI_(t-1))/CPI_(t-1) × 100%", "CPI đo chi phí của một rổ hàng hóa tiêu biểu."),
            make_doc("economics_finance", "unemployment_rate", "Tỷ lệ thất nghiệp", ["lao động", "thất nghiệp"], "Tỷ lệ thất nghiệp = số người thất nghiệp / lực lượng lao động.", "u = unemployed / labor force × 100%", "Không bao gồm người ngoài lực lượng lao động."),
            make_doc("economics_finance", "opportunity_cost", "Chi phí cơ hội", ["lựa chọn", "đánh đổi"], "Giá trị phương án tốt nhất bị từ bỏ khi đưa ra quyết định.", "", "Khái niệm trung tâm của kinh tế học về sự khan hiếm."),
            make_doc("economics_finance", "comparative_advantage", "Lợi thế so sánh", ["thương mại", "cơ hội"], "Một tác nhân có lợi thế so sánh nếu chi phí cơ hội sản xuất hàng hóa đó thấp hơn.", "", "Thương mại mang lại lợi ích khi mỗi bên chuyên môn hóa theo lợi thế so sánh."),
            make_doc("economics_finance", "marginal_utility", "Lợi ích cận biên", ["tiêu dùng", "tối ưu"], "Lợi ích cận biên là mức tăng thỏa dụng khi tiêu dùng thêm một đơn vị hàng hóa.", "", "Quy luật lợi ích cận biên giảm dần thường áp dụng."),
            make_doc("economics_finance", "perfect_competition", "Thị trường cạnh tranh hoàn hảo", ["giá chấp nhận", "mr=mc"], "Doanh nghiệp là người chấp nhận giá, tối đa hóa lợi nhuận tại MR = MC.", "Trong cạnh tranh hoàn hảo: P = MR", "Trong dài hạn có thể P = min ATC ở trạng thái cân bằng."),
            make_doc("economics_finance", "monopoly", "Độc quyền", ["mr", "mc"], "Doanh nghiệp độc quyền đối mặt đường cầu thị trường và MR < P.", "Tối đa hóa lợi nhuận tại MR = MC", "Có thể gây mất mát vô ích do sản lượng thấp hơn cạnh tranh."),
            make_doc("economics_finance", "cournot_duopoly", "Cân bằng Cournot", ["song quyền", "nash"], "Hai doanh nghiệp chọn sản lượng đồng thời, mỗi bên phản ứng theo sản lượng đối thủ.", "", "Mỗi doanh nghiệp tối ưu hóa lợi nhuận theo phản ứng tốt nhất."),
            make_doc("economics_finance", "nash_equilibrium", "Cân bằng Nash", ["game theory", "chiến lược"], "Không người chơi nào muốn đơn phương đổi chiến lược khi chiến lược người khác giữ nguyên.", "", "Khái niệm nền tảng của lý thuyết trò chơi."),
            make_doc("economics_finance", "fiscal_policy", "Chính sách tài khóa", ["chi tiêu công", "thuế"], "Chính phủ dùng chi tiêu và thuế để tác động tổng cầu.", "", "Mở rộng tài khóa thường tăng cầu; thắt chặt tài khóa thường giảm cầu."),
            make_doc("economics_finance", "monetary_policy", "Chính sách tiền tệ", ["lãi suất", "cung tiền"], "Ngân hàng trung ương điều tiết cung tiền và lãi suất.", "", "Thắt chặt tiền tệ thường giảm lạm phát nhưng có thể làm giảm tăng trưởng ngắn hạn."),
        ]
    )

    docs.extend(
        [
            make_doc("economics_finance", "simple_interest", "Lãi đơn", ["lãi suất", "tiền gốc"], "Lãi chỉ tính trên tiền gốc ban đầu.", "I = Prt; A = P(1 + rt)", "P là vốn gốc, r là lãi suất, t là thời gian."),
            make_doc("economics_finance", "compound_interest", "Lãi kép", ["ghép lãi", "tăng trưởng"], "Lãi phát sinh được cộng vào gốc cho kỳ tiếp theo.", "A = P(1 + r/n)^(nt)", "Tần suất ghép lãi cao hơn thường làm giá trị tương lai lớn hơn."),
            make_doc("economics_finance", "effective_annual_rate", "Lãi suất hiệu dụng năm", ["EAR", "APR"], "EAR phản ánh lãi suất thực tế sau khi tính ghép lãi trong năm.", "EAR = (1 + r/n)^n - 1", "Khác với lãi suất danh nghĩa APR."),
            make_doc("economics_finance", "net_present_value", "Giá trị hiện tại thuần", ["NPV", "chiết khấu"], "Đánh giá dự án bằng giá trị hiện tại của dòng tiền vào trừ ra.", "NPV = Σ CF_t/(1+r)^t - I_0", "NPV > 0 thường là tín hiệu dự án tạo giá trị."),
            make_doc("economics_finance", "internal_rate_return", "Tỷ suất hoàn vốn nội bộ", ["IRR", "đầu tư"], "IRR là mức chiết khấu khiến NPV bằng 0.", "0 = Σ CF_t/(1+IRR)^t - I_0", "So sánh IRR với chi phí vốn yêu cầu."),
            make_doc("economics_finance", "capm", "Mô hình CAPM", ["beta", "lợi suất yêu cầu"], "Lợi suất kỳ vọng phụ thuộc lãi suất phi rủi ro và phần bù rủi ro thị trường.", "E(R_i) = R_f + β_i(E(R_m)-R_f)", "Beta đo mức nhạy của tài sản với thị trường."),
            make_doc("economics_finance", "wacc", "Chi phí vốn bình quân gia quyền", ["WACC", "cấu trúc vốn"], "Mức chiết khấu thường dùng cho dòng tiền doanh nghiệp.", "WACC = w_e r_e + w_d r_d(1-T)", "Trọng số dựa trên cơ cấu vốn mục tiêu."),
            make_doc("economics_finance", "bond_price_yield", "Quan hệ giá trái phiếu và lợi suất", ["bond", "yield"], "Giá trái phiếu và lợi suất biến động ngược chiều.", "", "Khi lợi suất thị trường tăng, giá trái phiếu hiện có thường giảm."),
            make_doc("economics_finance", "duration", "Duration trái phiếu", ["lãi suất", "độ nhạy"], "Duration xấp xỉ độ nhạy giá trái phiếu với thay đổi lãi suất.", "", "Duration cao thường làm giá nhạy hơn với biến động lãi suất."),
            make_doc("economics_finance", "pe_ratio", "Hệ số P/E", ["định giá", "thu nhập"], "Giá thị trường chia lợi nhuận trên mỗi cổ phiếu.", "P/E = Price / EPS", "P/E cao có thể phản ánh kỳ vọng tăng trưởng hoặc định giá cao."),
            make_doc("economics_finance", "roe_dupont", "ROE và phân tích DuPont", ["roe", "biên lợi nhuận"], "ROE có thể tách thành biên lợi nhuận, vòng quay tài sản và đòn bẩy tài chính.", "ROE = (LN ròng/Doanh thu) × (Doanh thu/Tài sản) × (Tài sản/Vốn CSH)", "Giúp tìm nguồn gốc thay đổi hiệu quả sinh lời."),
            make_doc("economics_finance", "working_capital_cycle", "Chu kỳ vốn lưu động", ["CCC", "hàng tồn kho"], "Đo thời gian từ lúc chi tiền mua đầu vào đến lúc thu tiền bán hàng.", "CCC = DIO + DSO - DPO", "Chu kỳ ngắn hơn thường cải thiện thanh khoản."),
        ]
    )

    docs.extend(
        [
            make_doc("computer_science", "big_o", "Độ phức tạp Big-O", ["thuật toán", "độ phức tạp"], "Big-O mô tả tốc độ tăng chi phí tính toán theo kích thước đầu vào.", "", "O(1) hằng số; O(log n) logarit; O(n) tuyến tính; O(n^2) bậc hai."),
            make_doc("computer_science", "binary_search", "Tìm kiếm nhị phân", ["mảng có thứ tự", "log n"], "Tìm kiếm trên dãy đã sắp xếp bằng cách chia đôi không gian tìm kiếm.", "Độ phức tạp O(log n)", "Yêu cầu dữ liệu được sắp xếp trước."),
            make_doc("computer_science", "bfs", "Breadth-First Search", ["đồ thị", "hàng đợi"], "Duyệt theo lớp, thường dùng tìm đường đi ngắn nhất trong đồ thị không trọng số.", "", "BFS dùng queue."),
            make_doc("computer_science", "dfs", "Depth-First Search", ["đồ thị", "ngăn xếp"], "Đi sâu nhất có thể trước khi quay lui.", "", "DFS dùng stack hoặc đệ quy."),
            make_doc("computer_science", "hash_table", "Bảng băm", ["tra cứu", "xung đột"], "Cấu trúc dữ liệu cho phép tra cứu trung bình gần O(1).", "", "Cần chiến lược xử lý xung đột như chaining hoặc open addressing."),
            make_doc("computer_science", "stack_queue", "Ngăn xếp và hàng đợi", ["LIFO", "FIFO"], "Stack theo LIFO, queue theo FIFO.", "", "Stack: push/pop; queue: enqueue/dequeue."),
            make_doc("computer_science", "recursion", "Đệ quy", ["base case", "call stack"], "Hàm tự gọi lại chính nó để giải bài toán con.", "", "Phải có điều kiện dừng rõ ràng để tránh lặp vô hạn."),
            make_doc("computer_science", "dynamic_programming", "Quy hoạch động", ["subproblem", "memoization"], "Giải bài toán bằng cách lưu kết quả các bài toán con chồng lấp.", "", "Thường dùng memoization hoặc tabulation."),
            make_doc("computer_science", "dijkstra", "Thuật toán Dijkstra", ["đường đi ngắn nhất", "đồ thị có trọng số"], "Tìm đường đi ngắn nhất từ một nguồn trên đồ thị trọng số không âm.", "", "Không áp dụng trực tiếp khi có cạnh trọng số âm."),
            make_doc("computer_science", "sql_joins", "Các phép JOIN trong SQL", ["inner join", "left join"], "Kết hợp dữ liệu từ nhiều bảng theo khóa liên hệ.", "", "INNER JOIN giữ phần giao; LEFT JOIN giữ toàn bộ bảng trái."),
            make_doc("computer_science", "acid", "Thuộc tính ACID", ["database", "transaction"], "Một giao dịch đáng tin cậy thường thỏa ACID.", "", "Atomicity, Consistency, Isolation, Durability."),
            make_doc("computer_science", "osi_tcpip", "Mô hình OSI và TCP/IP", ["mạng máy tính", "protocol"], "OSI có 7 tầng; TCP/IP thường gộp thành 4 hoặc 5 tầng.", "", "Giúp xác định vai trò của giao thức ở từng lớp."),
        ]
    )

    docs.extend(
        [
            make_doc("law_safety", "contract_elements", "Các yếu tố cơ bản của hợp đồng", ["đề nghị", "chấp nhận", "năng lực"], "Hợp đồng thường cần sự thỏa thuận tự nguyện, chủ thể có năng lực và mục đích hợp pháp.", "", "Điều khoản trái pháp luật có thể làm giao dịch vô hiệu."),
            make_doc("law_safety", "burden_of_proof", "Gánh nặng chứng minh", ["chứng cứ", "tranh chấp"], "Bên đưa ra yêu cầu thường có nghĩa vụ chứng minh cho yêu cầu của mình.", "", "Quy tắc cụ thể tùy lĩnh vực tố tụng."),
            make_doc("law_safety", "consumer_rights", "Quyền cơ bản của người tiêu dùng", ["thông tin", "an toàn"], "Người tiêu dùng thường có quyền được cung cấp thông tin chính xác và sử dụng hàng hóa an toàn.", "", "Tổ chức kinh doanh có nghĩa vụ minh bạch và bồi thường khi vi phạm."),
            make_doc("law_safety", "labor_contract", "Khái niệm hợp đồng lao động", ["lao động", "người sử dụng lao động"], "Hợp đồng lao động ghi nhận việc làm có trả công, điều kiện làm việc và quyền nghĩa vụ của các bên.", "", "Cần lưu ý thời hạn, thử việc, bảo hiểm và điều kiện chấm dứt."),
            make_doc("law_safety", "limited_liability", "Trách nhiệm hữu hạn", ["doanh nghiệp", "vốn góp"], "Chủ sở hữu/cổ đông thường chịu trách nhiệm trong phạm vi phần vốn góp theo loại hình phù hợp.", "", "Phân biệt với trách nhiệm vô hạn của một số mô hình khác."),
            make_doc("law_safety", "copyright_basics", "Bản quyền cơ bản", ["quyền tác giả", "tác phẩm"], "Quyền tác giả bảo vệ tác phẩm sáng tạo thể hiện dưới hình thức nhất định.", "", "Không bảo hộ ý tưởng thuần túy chưa được thể hiện."),
            make_doc("law_safety", "data_privacy_consent", "Đồng ý trong bảo vệ dữ liệu cá nhân", ["consent", "privacy"], "Xử lý dữ liệu cá nhân thường cần căn cứ pháp lý phù hợp, trong đó có sự đồng ý hợp lệ.", "", "Sự đồng ý nên tự nguyện, cụ thể và có thể chứng minh."),
            make_doc("law_safety", "anti_corruption_conflict", "Xung đột lợi ích", ["liêm chính", "tuân thủ"], "Xung đột lợi ích phát sinh khi lợi ích cá nhân có thể ảnh hưởng đến quyết định công vụ hoặc nghề nghiệp.", "", "Cần nhận diện, khai báo và xử lý minh bạch."),
        ]
    )

    docs.extend(
        [
            make_doc("general_knowledge", "vector_dot_product", "Tích vô hướng", ["vector", "góc"], "Tích vô hướng liên hệ độ dài và góc giữa hai vector.", "a·b = |a||b|cosθ = Σ a_i b_i", "Hai vector vuông góc khi tích vô hướng bằng 0."),
            make_doc("general_knowledge", "derivative_meaning", "Ý nghĩa hình học của đạo hàm", ["tiếp tuyến", "độ dốc"], "Đạo hàm tại một điểm là hệ số góc của tiếp tuyến đồ thị tại điểm đó.", "", "Cũng là tốc độ thay đổi tức thời trong ngữ cảnh vật lý/kinh tế."),
            make_doc("general_knowledge", "integral_meaning", "Ý nghĩa của tích phân xác định", ["diện tích", "tổng tích lũy"], "Tích phân xác định mô tả lượng tích lũy hoặc diện tích có dấu.", "", "Thường dùng để tính diện tích, quãng đường tích lũy, xác suất."),
            make_doc("general_knowledge", "p_value", "Khái niệm p-value", ["kiểm định giả thuyết", "thống kê"], "p-value là xác suất quan sát dữ liệu cực đoan như đã thấy nếu giả thuyết không đúng bị giữ.", "", "p-value nhỏ thường chống lại giả thuyết gốc."),
            make_doc("general_knowledge", "entropy_information", "Entropy trong lý thuyết thông tin", ["bit", "bất định"], "Entropy đo mức độ bất định trung bình của nguồn tin.", "H(X) = -Σ p(x) log_2 p(x)", "Entropy cao hơn nghĩa là thông tin trung bình nhiều hơn."),
            make_doc("general_knowledge", "probability_expectation", "Kỳ vọng toán học", ["xác suất", "trung bình"], "Kỳ vọng là giá trị trung bình dài hạn của biến ngẫu nhiên.", "E[X] = Σ x p(x)", "Không nhất thiết là giá trị thực sự quan sát được."),
            make_doc("general_knowledge", "algorithm_definition", "Định nghĩa thuật toán", ["bước hữu hạn", "giải bài toán"], "Thuật toán là dãy bước xác định, hữu hạn để giải một lớp bài toán.", "", "Các tiêu chí thường gồm đúng đắn, hiệu quả và tính dừng."),
            make_doc("general_knowledge", "database_normalization", "Chuẩn hóa cơ sở dữ liệu", ["1NF", "2NF", "3NF"], "Chuẩn hóa giảm dư thừa và bất nhất dữ liệu bằng cách tổ chức quan hệ hợp lý.", "", "3NF thường loại bỏ phụ thuộc bắc cầu không cần thiết."),
            make_doc("general_knowledge", "inflation_deflation", "Lạm phát và giảm phát", ["mức giá", "kinh tế vĩ mô"], "Lạm phát là mức giá chung tăng; giảm phát là mức giá chung giảm.", "", "Hai hiện tượng có hệ quả rất khác nhau lên tiêu dùng và đầu tư."),
            make_doc("general_knowledge", "risk_return_tradeoff", "Đánh đổi rủi ro - lợi nhuận", ["đầu tư", "risk premium"], "Lợi nhuận kỳ vọng cao hơn thường đòi hỏi chấp nhận rủi ro cao hơn.", "", "Khái niệm nền tảng trong tài chính và quyết định đầu tư."),
        ]
    )

    return docs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a small curated offline knowledge base")
    parser.add_argument("--output", type=Path, default=Path("knowledge_base/reference_documents.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    documents = build_documents()
    if not 100 <= len(documents) <= 200:
        raise ValueError(f"Expected 100-200 documents, got {len(documents)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(documents)} documents to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
