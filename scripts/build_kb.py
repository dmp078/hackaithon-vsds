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

    history_geography_docs = [
        ("world_war_i", "Chiến tranh thế giới thứ nhất", ["1914", "1918", "liên minh"], "Diễn ra từ 1914 đến 1918 với hai khối chính là Liên minh và Hiệp ước.", "", "Khởi phát trực tiếp sau vụ ám sát Franz Ferdinand."),
        ("world_war_ii", "Chiến tranh thế giới thứ hai", ["1939", "1945", "phe trục"], "Diễn ra từ 1939 đến 1945, kết thúc bằng thắng lợi của phe Đồng minh.", "", "Sự kiện lớn gồm trận Stalingrad, D-Day và hai bom nguyên tử ở Nhật."),
        ("cold_war", "Chiến tranh Lạnh", ["Mỹ", "Liên Xô", "ý thức hệ"], "Giai đoạn đối đầu chiến lược giữa Mỹ và Liên Xô sau Thế chiến II.", "", "Nổi bật với chạy đua vũ trang, không gian và các cuộc chiến ủy nhiệm."),
        ("french_revolution", "Cách mạng Pháp", ["1789", "nhân quyền", "quân chủ"], "Lật đổ trật tự phong kiến cũ và khẳng định các khẩu hiệu tự do, bình đẳng, bác ái.", "", "Mở đầu cho nhiều biến đổi chính trị ở châu Âu."),
        ("industrial_revolution", "Cách mạng công nghiệp", ["máy hơi nước", "công xưởng"], "Chuyển sản xuất thủ công sang cơ khí hóa quy mô lớn.", "", "Bắt đầu ở Anh rồi lan sang châu Âu và Bắc Mỹ."),
        ("renaissance", "Phong trào Phục hưng", ["nhân văn", "châu Âu"], "Phong trào văn hóa - tư tưởng đề cao con người và khoa học cổ điển.", "", "Khởi phát mạnh ở Ý rồi lan ra Tây Âu."),
        ("united_nations", "Liên Hợp Quốc", ["1945", "hòa bình", "an ninh"], "Tổ chức quốc tế thành lập năm 1945 nhằm duy trì hòa bình, an ninh và hợp tác quốc tế.", "", "Cơ quan chính gồm Đại hội đồng, HĐBA, ICJ, ECOSOC."),
        ("asean", "ASEAN", ["Đông Nam Á", "1967"], "Hiệp hội các quốc gia Đông Nam Á thành lập năm 1967 nhằm thúc đẩy hợp tác khu vực.", "", "Việt Nam gia nhập ASEAN năm 1995."),
        ("eu", "Liên minh châu Âu", ["EU", "thị trường chung"], "Liên minh kinh tế - chính trị của nhiều quốc gia châu Âu.", "", "Đặc trưng bởi thị trường chung và đồng euro ở nhiều nước thành viên."),
        ("nato", "NATO", ["phòng thủ tập thể", "1949"], "Liên minh quân sự Bắc Đại Tây Dương thành lập năm 1949.", "", "Nguyên tắc cốt lõi là phòng thủ tập thể theo Điều 5."),
        ("vietnam_august_revolution", "Cách mạng Tháng Tám", ["1945", "độc lập"], "Phong trào giành chính quyền năm 1945 dẫn tới sự ra đời của nước Việt Nam Dân chủ Cộng hòa.", "", "Tuyên ngôn Độc lập được đọc ngày 2/9/1945."),
        ("dien_bien_phu", "Chiến thắng Điện Biên Phủ", ["1954", "kháng chiến"], "Chiến thắng quyết định của Việt Minh trước quân Pháp năm 1954.", "", "Mở đường cho Hiệp định Genève."),
        ("geneva_1954", "Hiệp định Genève 1954", ["đình chiến", "vĩ tuyến 17"], "Hiệp định quốc tế liên quan chấm dứt chiến sự ở Đông Dương.", "", "Việt Nam tạm thời bị chia cắt ở vĩ tuyến 17."),
        ("paris_1973", "Hiệp định Paris 1973", ["Việt Nam", "ngừng bắn"], "Hiệp định nhằm lập lại hòa bình ở Việt Nam ký năm 1973.", "", "Liên quan việc rút quân Mỹ khỏi Việt Nam."),
        ("doi_moi_1986", "Đổi Mới 1986", ["kinh tế", "cải cách"], "Chủ trương đổi mới toàn diện, chuyển mạnh sang kinh tế thị trường định hướng XHCN.", "", "Tác động lớn đến tăng trưởng và hội nhập kinh tế của Việt Nam."),
        ("mekong", "Sông Mekong", ["Đông Nam Á", "lưu vực"], "Một trong các con sông lớn của châu Á, chảy qua nhiều quốc gia Đông Nam Á.", "", "Đồng bằng sông Cửu Long là vùng hạ lưu quan trọng của Mekong."),
        ("red_river", "Sông Hồng", ["miền Bắc", "đồng bằng"], "Hệ thống sông quan trọng ở miền Bắc Việt Nam.", "", "Gắn liền với đồng bằng sông Hồng và nông nghiệp lúa nước."),
        ("mountain_climate", "Khí hậu miền núi", ["độ cao", "nhiệt độ"], "Nhiệt độ thường giảm khi độ cao tăng, khí hậu phân hóa theo đai cao.", "", "Khu vực núi cao có thể có khí hậu mát hơn rõ rệt."),
        ("monsoon", "Gió mùa", ["mùa mưa", "mùa khô"], "Kiểu hoàn lưu gió đổi hướng theo mùa do chênh lệch khí áp lục địa - đại dương.", "", "Ảnh hưởng mạnh đến khí hậu Việt Nam và Nam Á."),
        ("latitude_longitude", "Vĩ độ và kinh độ", ["tọa độ địa lý"], "Vĩ độ đo vị trí bắc - nam so với xích đạo; kinh độ đo đông - tây so với kinh tuyến gốc.", "", "Dùng để xác định vị trí tuyệt đối trên Trái Đất."),
        ("time_zones", "Múi giờ", ["kinh tuyến", "UTC"], "Thế giới chia thành các múi giờ gần đúng theo kinh tuyến.", "", "Chênh lệch 15 độ kinh tuyến tương ứng khoảng 1 giờ."),
        ("plate_tectonics", "Kiến tạo mảng", ["động đất", "núi lửa"], "Vỏ Trái Đất gồm các mảng kiến tạo di chuyển tương đối với nhau.", "", "Ranh giới mảng thường gắn với động đất và núi lửa."),
        ("erosion_weathering", "Phong hóa và xói mòn", ["địa mạo"], "Phong hóa phá vỡ đá tại chỗ, còn xói mòn là quá trình bóc mòn và vận chuyển vật liệu.", "", "Nước, gió, băng là tác nhân quan trọng."),
        ("desert_definition", "Hoang mạc", ["lượng mưa thấp"], "Vùng có lượng mưa rất thấp, thảm thực vật thưa thớt.", "", "Không nhất thiết phải nóng; có cả hoang mạc lạnh."),
        ("savanna", "Xa van", ["đồng cỏ", "nhiệt đới"], "Kiểu cảnh quan nhiệt đới với cỏ là chủ yếu và cây phân tán.", "", "Thường có mùa mưa và mùa khô rõ rệt."),
        ("rainforest", "Rừng mưa nhiệt đới", ["đa dạng sinh học"], "Hệ sinh thái nóng ẩm với lượng mưa lớn quanh năm.", "", "Đa dạng sinh học rất cao và nhiều tầng tán."),
        ("ocean_currents", "Dòng biển", ["nóng", "lạnh"], "Dòng biển nóng/lạnh ảnh hưởng lớn đến khí hậu ven bờ và ngư trường.", "", "Ví dụ Gulf Stream là dòng biển nóng nổi tiếng."),
        ("el_nino_la_nina", "El Niño và La Niña", ["thái bình dương", "dao động khí hậu"], "Hai pha đối lập của ENSO gây biến động thời tiết toàn cầu.", "", "El Niño thường làm nóng lên bất thường vùng trung tâm - đông Thái Bình Dương."),
        ("map_scale", "Tỷ lệ bản đồ", ["khoảng cách", "bản đồ"], "Biểu thị quan hệ giữa khoảng cách trên bản đồ và ngoài thực địa.", "", "Tỷ lệ lớn cho chi tiết cao hơn trên phạm vi nhỏ."),
        ("population_density", "Mật độ dân số", ["người/km2"], "Số người trên một đơn vị diện tích.", "Mật độ = dân số / diện tích", "Dùng để so sánh mức độ tập trung dân cư."),
        ("urbanization", "Đô thị hóa", ["thành phố", "cơ cấu lao động"], "Quá trình gia tăng tỷ lệ dân cư sống ở đô thị và mở rộng không gian đô thị.", "", "Thường đi kèm chuyển dịch lao động khỏi nông nghiệp."),
        ("migration", "Di cư", ["nhập cư", "xuất cư"], "Di chuyển dân cư từ nơi này sang nơi khác trong hoặc ngoài một quốc gia.", "", "Nguyên nhân có thể là kinh tế, xã hội, môi trường, xung đột."),
        ("natural_resources", "Tài nguyên thiên nhiên", ["tái tạo", "không tái tạo"], "Gồm các nguồn lực lấy từ tự nhiên phục vụ phát triển.", "", "Phân biệt tài nguyên tái tạo và không tái tạo."),
        ("energy_resources", "Nguồn năng lượng", ["hóa thạch", "tái tạo"], "Bao gồm năng lượng hóa thạch, thủy điện, gió, mặt trời, sinh khối...", "", "Năng lượng tái tạo thường có lợi thế bền vững hơn."),
        ("seismic_risk", "Rủi ro động đất", ["đới đứt gãy"], "Nguy cơ động đất lớn hơn ở gần ranh giới mảng và đới đứt gãy hoạt động.", "", "Thiết kế công trình phải xét đến cấp động đất."),
        ("sea_level_rise", "Nước biển dâng", ["biến đổi khí hậu"], "Mực nước biển tăng do băng tan và giãn nở nhiệt của đại dương.", "", "Ảnh hưởng mạnh đến đồng bằng ven biển thấp."),
        ("capital_city", "Khái niệm thủ đô", ["trung tâm chính trị"], "Thủ đô thường là trung tâm chính trị - hành chính của quốc gia.", "", "Không phải lúc nào cũng là thành phố lớn nhất về dân số."),
        ("archipelago", "Quần đảo", ["đảo", "biển"], "Tập hợp nhiều đảo gần nhau tạo thành một vùng đảo.", "", "Ví dụ Indonesia và Philippines là quốc gia quần đảo."),
        ("isthmus_peninsula", "Eo đất và bán đảo", ["địa hình ven biển"], "Eo đất là dải đất hẹp nối hai vùng đất lớn; bán đảo là phần đất nhô ra biển ba phía.", "", "Hai khái niệm địa lý thường dễ bị nhầm lẫn."),
        ("cartography_symbols", "Ký hiệu bản đồ", ["chú giải", "bản đồ"], "Ký hiệu bản đồ giúp biểu diễn đối tượng địa lý dưới dạng quy ước.", "", "Luôn đọc chú giải trước khi suy luận từ bản đồ."),
    ]
    docs.extend(
        [
            make_doc("history_geography", topic, title, keywords, explanation, formulas, definitions)
            for topic, title, keywords, explanation, formulas, definitions in history_geography_docs
        ]
    )

    biology_environment_docs = [
        ("cell_theory", "Học thuyết tế bào", ["tế bào", "sinh học"], "Mọi cơ thể sống được cấu tạo từ tế bào và tế bào là đơn vị cơ bản của sự sống.", "", "Tế bào chỉ sinh ra từ tế bào có trước."),
        ("prokaryote_eukaryote", "Tế bào nhân sơ và nhân thực", ["nhân", "bào quan"], "Nhân sơ không có màng nhân; nhân thực có nhân thật và nhiều bào quan có màng.", "", "Vi khuẩn là ví dụ điển hình của sinh vật nhân sơ."),
        ("cell_membrane", "Màng sinh chất", ["vận chuyển", "phospholipid"], "Màng sinh chất kiểm soát trao đổi chất vào ra tế bào.", "", "Mô hình khảm lỏng gồm phospholipid và protein."),
        ("osmosis_diffusion", "Khuếch tán và thẩm thấu", ["màng bán thấm", "nước"], "Khuếch tán là chuyển động từ nơi nồng độ cao xuống thấp; thẩm thấu là khuếch tán nước qua màng bán thấm.", "", "Không cần năng lượng trao đổi chất."),
        ("active_transport", "Vận chuyển chủ động", ["ATP", "gradient"], "Vận chuyển chất ngược gradient nồng độ cần năng lượng.", "", "Ví dụ bơm Na+/K+ ở tế bào động vật."),
        ("mitosis", "Nguyên phân", ["phân bào", "NST"], "Nguyên phân tạo hai tế bào con có bộ NST giống tế bào mẹ.", "", "Phục vụ sinh trưởng, tái tạo mô, sinh sản vô tính."),
        ("meiosis", "Giảm phân", ["giao tử", "biến dị"], "Giảm phân tạo giao tử với số NST giảm đi một nửa.", "", "Là nguồn gốc quan trọng của biến dị tổ hợp."),
        ("dna_structure", "Cấu trúc DNA", ["nucleotide", "xoắn kép"], "DNA gồm hai mạch polynucleotide xoắn kép ngược chiều.", "", "A bắt cặp T, G bắt cặp C theo nguyên tắc bổ sung."),
        ("rna_types", "Các loại RNA", ["mRNA", "tRNA", "rRNA"], "mRNA mang mã, tRNA vận chuyển amino acid, rRNA cấu tạo ribosome.", "", "RNA thường mạch đơn và có uracil thay thymine."),
        ("replication", "Nhân đôi DNA", ["bán bảo tồn"], "DNA nhân đôi theo nguyên tắc bổ sung và bán bảo tồn.", "", "Mỗi phân tử mới có một mạch cũ và một mạch mới."),
        ("transcription_translation", "Phiên mã và dịch mã", ["protein", "gene"], "Thông tin di truyền đi từ DNA sang RNA rồi sang protein.", "", "Ribosome đọc codon trên mRNA để tổng hợp polypeptide."),
        ("genetic_code", "Mã di truyền", ["codon", "amino acid"], "Mã di truyền là mã bộ ba gần như phổ biến và thoái hóa.", "", "Một codon mã hóa một amino acid hoặc tín hiệu kết thúc."),
        ("mendel_laws", "Các định luật Mendel", ["phân li", "phân li độc lập"], "Quy luật phân li và phân li độc lập mô tả di truyền tính trạng đơn gen cơ bản.", "", "Tỷ lệ kiểu hình cổ điển 3:1, 9:3:3:1 tùy phép lai."),
        ("dominant_recessive", "Trội và lặn", ["allele", "kiểu hình"], "Alen trội biểu hiện ở thể dị hợp, alen lặn cần đồng hợp lặn để biểu hiện.", "", "Tính trạng trội không có nghĩa là phổ biến hơn trong quần thể."),
        ("hardy_weinberg", "Cân bằng Hardy-Weinberg", ["tần số alen", "quần thể"], "Mô hình cân bằng di truyền lý tưởng của quần thể ngẫu phối lớn.", "p + q = 1; p^2 + 2pq + q^2 = 1", "Dùng để suy tần số kiểu gen từ tần số alen."),
        ("mutation", "Đột biến", ["gene", "NST"], "Đột biến là biến đổi vật chất di truyền ở mức gen hoặc nhiễm sắc thể.", "", "Có thể có lợi, có hại hoặc trung tính tùy ngữ cảnh."),
        ("natural_selection", "Chọn lọc tự nhiên", ["tiến hóa", "thích nghi"], "Cá thể có đặc điểm thích nghi hơn thường để lại nhiều con hơn.", "", "Là cơ chế trung tâm của tiến hóa Darwin."),
        ("speciation", "Hình thành loài", ["cách li", "tiến hóa"], "Loài mới hình thành khi quần thể tích lũy khác biệt và bị cách li sinh sản.", "", "Cách li địa lý và sinh thái là các cơ chế quan trọng."),
        ("food_chain_web", "Chuỗi và lưới thức ăn", ["hệ sinh thái", "dinh dưỡng"], "Chuỗi thức ăn thể hiện dòng năng lượng; lưới thức ăn là tập hợp nhiều chuỗi liên hệ.", "", "Sinh vật sản xuất thường ở bậc dinh dưỡng đầu."),
        ("photosynthesis", "Quang hợp", ["diệp lục", "ánh sáng"], "Thực vật dùng năng lượng ánh sáng tổng hợp chất hữu cơ từ CO2 và nước.", "6CO2 + 6H2O -> C6H12O6 + 6O2", "Diễn ra chủ yếu ở lục lạp."),
        ("cellular_respiration", "Hô hấp tế bào", ["ATP", "glucose"], "Phá vỡ glucose để giải phóng năng lượng dưới dạng ATP.", "", "Ở sinh vật hiếu khí, chất nhận electron cuối cùng là oxy."),
        ("enzymes", "Enzyme", ["xúc tác sinh học"], "Enzyme là chất xúc tác sinh học giúp tăng tốc phản ứng mà không bị tiêu hao đáng kể.", "", "Hoạt tính enzyme phụ thuộc nhiệt độ, pH và nồng độ cơ chất."),
        ("immune_system", "Hệ miễn dịch", ["miễn dịch bẩm sinh", "thích ứng"], "Bảo vệ cơ thể trước tác nhân gây bệnh qua nhiều tầng cơ chế.", "", "Kháng thể là thành phần quan trọng của miễn dịch dịch thể."),
        ("vaccination", "Tiêm chủng", ["miễn dịch chủ động"], "Đưa kháng nguyên hoặc thông tin kháng nguyên vào cơ thể để kích hoạt miễn dịch bảo vệ.", "", "Giúp cơ thể ghi nhớ và đáp ứng nhanh khi gặp mầm bệnh thật."),
        ("ecological_succession", "Diễn thế sinh thái", ["quần xã", "phục hồi"], "Quá trình thay thế tuần tự các quần xã sinh vật theo thời gian.", "", "Có diễn thế nguyên sinh và thứ sinh."),
        ("population_growth", "Tăng trưởng quần thể", ["mật độ", "sức chứa"], "Quần thể có thể tăng theo hàm mũ khi nguồn lực dồi dào hoặc logistic khi bị giới hạn.", "", "Sức chứa môi trường giới hạn quy mô dài hạn."),
        ("biodiversity", "Đa dạng sinh học", ["gen", "loài", "hệ sinh thái"], "Đa dạng sinh học gồm mức độ gen, loài và hệ sinh thái.", "", "Đa dạng cao thường tăng khả năng ổn định hệ sinh thái."),
        ("climate_change_ecology", "Biến đổi khí hậu và sinh thái", ["nhiệt độ", "môi trường"], "Biến đổi khí hậu làm thay đổi phân bố loài, chu kỳ sinh học và chất lượng môi trường sống.", "", "Nhiều hệ sinh thái nhạy cảm như san hô và vùng ven biển bị ảnh hưởng mạnh."),
        ("nitrogen_cycle", "Chu trình nitơ", ["vi khuẩn", "nông nghiệp"], "Nitơ lưu chuyển giữa khí quyển, đất, nước và sinh vật qua nhiều quá trình.", "", "Cố định nitơ, nitrat hóa và phản nitrat hóa là các bước quan trọng."),
        ("carbon_cycle", "Chu trình carbon", ["CO2", "sinh quyển"], "Carbon trao đổi giữa khí quyển, đại dương, đất đá và sinh vật.", "", "Đốt nhiên liệu hóa thạch làm tăng CO2 khí quyển."),
        ("water_cycle", "Chu trình nước", ["bốc hơi", "mưa"], "Nước vận động liên tục qua bốc hơi, ngưng tụ, mưa và dòng chảy.", "", "Năng lượng mặt trời là động lực chính của chu trình nước."),
        ("symbiosis", "Quan hệ cộng sinh", ["hỗ trợ", "ký sinh"], "Quan hệ giữa các loài có thể là cộng sinh, hợp tác, hội sinh, ký sinh...", "", "Phân biệt dựa trên lợi ích hay thiệt hại của các bên."),
        ("human_digestion", "Hệ tiêu hóa người", ["enzym", "hấp thu"], "Chức năng chính là tiêu hóa thức ăn và hấp thu chất dinh dưỡng.", "", "Ruột non là nơi hấp thu phần lớn dưỡng chất."),
        ("human_circulation", "Hệ tuần hoàn người", ["tim", "máu"], "Vận chuyển oxy, chất dinh dưỡng, hormon và chất thải trong cơ thể.", "", "Máu lưu thông qua vòng tuần hoàn nhỏ và lớn."),
        ("human_respiration", "Hệ hô hấp người", ["phổi", "trao đổi khí"], "Thực hiện trao đổi O2 và CO2 giữa cơ thể và môi trường.", "", "Phế nang là nơi trao đổi khí chủ yếu."),
        ("human_nervous_system", "Hệ thần kinh", ["não", "neurone"], "Điều khiển và phối hợp hoạt động cơ thể thông qua xung thần kinh.", "", "Gồm thần kinh trung ương và ngoại biên."),
        ("human_endocrine", "Hệ nội tiết", ["hormone"], "Điều hòa hoạt động cơ thể bằng các hormone do tuyến nội tiết tiết ra.", "", "Insulin, thyroxine, adrenaline là ví dụ quen thuộc."),
        ("homeostasis", "Cân bằng nội môi", ["điều hòa"], "Khả năng duy trì môi trường trong ổn định tương đối của cơ thể.", "", "Ví dụ điều hòa thân nhiệt, đường huyết, pH máu."),
        ("ecosystem_services", "Dịch vụ hệ sinh thái", ["thụ phấn", "điều tiết"], "Hệ sinh thái mang lại lợi ích cung cấp, điều tiết, văn hóa và hỗ trợ cho con người.", "", "Rừng, đất ngập nước và biển cung cấp nhiều dịch vụ quan trọng."),
        ("conservation", "Bảo tồn thiên nhiên", ["đa dạng sinh học", "khu bảo tồn"], "Các biện pháp bảo vệ loài, sinh cảnh và nguồn gen trước suy thoái.", "", "Bảo tồn tại chỗ và chuyển chỗ là hai chiến lược lớn."),
    ]
    docs.extend(
        [
            make_doc("biology_environment", topic, title, keywords, explanation, formulas, definitions)
            for topic, title, keywords, explanation, formulas, definitions in biology_environment_docs
        ]
    )

    law_safety_docs = [
        ("offer_acceptance", "Đề nghị và chấp nhận trong giao kết", ["hợp đồng", "đề nghị"], "Một giao kết hợp đồng thường cần đề nghị rõ ràng và sự chấp nhận phù hợp.", "", "Sửa đổi nội dung quan trọng có thể bị xem là đề nghị mới."),
        ("void_contract", "Giao dịch vô hiệu", ["vô hiệu", "trái luật"], "Giao dịch có thể vô hiệu khi vi phạm điều cấm, giả tạo, bị lừa dối hoặc chủ thể không đủ năng lực theo trường hợp luật định.", "", "Hậu quả thường là khôi phục tình trạng ban đầu trong phạm vi có thể."),
        ("representation_warranty", "Cam đoan và bảo đảm", ["giao dịch", "trách nhiệm"], "Các cam đoan/bảo đảm phân bổ rủi ro thông tin giữa các bên.", "", "Vi phạm có thể kéo theo bồi thường hoặc quyền chấm dứt."),
        ("breach_remedies", "Biện pháp khi vi phạm hợp đồng", ["bồi thường", "phạt vi phạm"], "Biện pháp phổ biến gồm buộc thực hiện, bồi thường thiệt hại, phạt vi phạm, hủy bỏ/chấm dứt trong điều kiện luật định.", "", "Cần phân biệt bồi thường với phạt vi phạm."),
        ("force_majeure", "Bất khả kháng", ["sự kiện khách quan"], "Sự kiện khách quan, không lường trước và không thể khắc phục có thể miễn/giảm trách nhiệm theo điều kiện áp dụng.", "", "Không phải mọi khó khăn kinh doanh đều là bất khả kháng."),
        ("good_faith", "Thiện chí và trung thực", ["nguyên tắc"], "Nguyên tắc thiện chí, trung thực thường chi phối đàm phán và thực hiện nghĩa vụ.", "", "Giấu thông tin trọng yếu có thể tạo rủi ro pháp lý."),
        ("civil_vs_criminal", "Dân sự và hình sự", ["tranh chấp", "tội phạm"], "Dân sự chủ yếu giải quyết quyền, nghĩa vụ và bồi thường; hình sự xử lý hành vi bị coi là tội phạm.", "", "Cùng một sự kiện có thể phát sinh nhiều loại trách nhiệm khác nhau."),
        ("administrative_sanctions", "Xử phạt hành chính", ["vi phạm", "mức phạt"], "Cơ chế xử lý vi phạm pháp luật chưa đến mức truy cứu trách nhiệm hình sự.", "", "Thường gồm phạt tiền, buộc khắc phục hậu quả, tước quyền sử dụng giấy phép..."),
        ("intellectual_property", "Sở hữu trí tuệ", ["nhãn hiệu", "sáng chế"], "Bao gồm quyền tác giả, nhãn hiệu, sáng chế, kiểu dáng, bí mật kinh doanh...", "", "Mỗi đối tượng có điều kiện xác lập và thời hạn bảo hộ khác nhau."),
        ("trademark_basics", "Nhãn hiệu", ["phân biệt hàng hóa"], "Dấu hiệu dùng để phân biệt hàng hóa, dịch vụ của các chủ thể khác nhau.", "", "Nhãn hiệu cần khả năng phân biệt và không thuộc dấu hiệu bị loại trừ."),
        ("patent_basics", "Sáng chế", ["mới", "sáng tạo"], "Giải pháp kỹ thuật có thể được bảo hộ nếu đáp ứng tính mới, trình độ sáng tạo và khả năng áp dụng công nghiệp.", "", "Không phải mọi ý tưởng kỹ thuật đều được cấp bằng."),
        ("trade_secret", "Bí mật kinh doanh", ["thông tin mật"], "Thông tin có giá trị thương mại nhờ không phổ biến và được chủ sở hữu giữ bí mật hợp lý.", "", "Mất tính bí mật có thể làm mất lợi thế bảo hộ."),
        ("employment_obligations", "Nghĩa vụ cơ bản trong quan hệ lao động", ["lao động", "tiền lương"], "Người sử dụng lao động phải trả lương, bảo đảm điều kiện làm việc; người lao động phải thực hiện công việc thỏa thuận.", "", "Thời giờ làm việc, nghỉ ngơi và bảo hiểm là mảng dễ bị hỏi."),
        ("workplace_safety", "An toàn lao động", ["PPE", "tai nạn"], "Doanh nghiệp có nghĩa vụ đánh giá rủi ro, huấn luyện và trang bị biện pháp an toàn phù hợp.", "", "Phòng ngừa luôn được ưu tiên hơn khắc phục."),
        ("non_discrimination", "Không phân biệt đối xử", ["bình đẳng", "lao động"], "Nguyên tắc bình đẳng áp dụng rộng trong tuyển dụng, sử dụng lao động và cung ứng dịch vụ.", "", "Phân biệt đối xử có thể phát sinh trách nhiệm dân sự/hành chính tùy trường hợp."),
        ("data_minimization", "Tối thiểu hóa dữ liệu", ["privacy", "compliance"], "Chỉ nên thu thập và xử lý dữ liệu cần thiết cho mục đích hợp pháp, rõ ràng.", "", "Thu thập quá mức là rủi ro tuân thủ phổ biến."),
        ("data_subject_rights", "Quyền của chủ thể dữ liệu", ["truy cập", "xóa", "sửa"], "Chủ thể dữ liệu thường có quyền biết, truy cập, chỉnh sửa, xóa hoặc hạn chế xử lý theo khuôn khổ áp dụng.", "", "Quyền cụ thể tùy hệ thống pháp luật nhưng xu hướng chung là tăng kiểm soát cá nhân."),
        ("cybersecurity_incident", "Sự cố an ninh mạng", ["thông báo", "ứng phó"], "Cần quy trình phát hiện, cô lập, khắc phục và thông báo phù hợp khi có sự cố.", "", "Nhật ký, bằng chứng và phân quyền là yếu tố quan trọng."),
        ("anti_money_laundering", "Chống rửa tiền cơ bản", ["KYC", "giao dịch đáng ngờ"], "Nhận biết khách hàng và theo dõi giao dịch đáng ngờ là trụ cột cơ bản của AML.", "", "Tổ chức tài chính thường có nghĩa vụ báo cáo theo luật chuyên ngành."),
        ("fiduciary_duty", "Nghĩa vụ ủy thác / cẩn trọng", ["quản trị", "xung đột lợi ích"], "Người quản lý phải hành động cẩn trọng, trung thực, vì lợi ích hợp pháp của tổ chức và tránh trục lợi.", "", "Xung đột lợi ích cần được khai báo và xử lý."),
        ("board_governance", "Quản trị hội đồng", ["nghị quyết", "ủy quyền"], "Quy trình ra quyết định cần đúng thẩm quyền, trình tự và minh bạch.", "", "Biên bản, biểu quyết và xung đột lợi ích là điểm kiểm soát chính."),
        ("procurement_integrity", "Liêm chính trong mua sắm", ["đấu thầu", "quà tặng"], "Mua sắm cần công bằng, minh bạch, tránh thông đồng và hối lộ.", "", "Quà tặng/hospitality có thể tạo rủi ro liêm chính nếu vượt ngưỡng cho phép."),
        ("competition_law", "Cạnh tranh và lạm dụng vị trí", ["thỏa thuận hạn chế cạnh tranh"], "Thỏa thuận ấn định giá, phân chia thị trường hoặc lạm dụng vị trí thống lĩnh có thể bị cấm.", "", "Phân tích thường xoay quanh thị trường liên quan và sức mạnh thị trường."),
        ("consumer_disclosure", "Nghĩa vụ công bố thông tin với người tiêu dùng", ["minh bạch", "quảng cáo"], "Thông tin về công dụng, giá, điều kiện giao dịch cần rõ ràng, không gây hiểu lầm.", "", "Quảng cáo sai sự thật là nguồn rủi ro lớn."),
        ("product_liability", "Trách nhiệm sản phẩm", ["khuyết tật", "an toàn"], "Nhà sản xuất/phân phối có thể chịu trách nhiệm khi sản phẩm có khuyết tật gây thiệt hại.", "", "Nghĩa vụ cảnh báo và thu hồi có thể phát sinh."),
        ("environmental_compliance", "Tuân thủ môi trường", ["xả thải", "giấy phép"], "Hoạt động sản xuất cần tuân thủ yêu cầu về đánh giá tác động, quản lý chất thải và phát thải.", "", "Vi phạm có thể kéo theo xử phạt, đình chỉ hoặc bồi thường."),
        ("record_retention", "Lưu giữ hồ sơ", ["hồ sơ", "kiểm toán"], "Tổ chức cần lưu giữ hồ sơ theo thời hạn và hình thức phù hợp để phục vụ kiểm toán, tranh chấp và tuân thủ.", "", "Xóa quá sớm hoặc giữ thiếu kiểm soát đều có rủi ro."),
        ("whistleblowing", "Tố giác nội bộ", ["whistleblowing", "bảo vệ người tố giác"], "Cơ chế báo cáo nội bộ giúp phát hiện vi phạm sớm và cần bảo vệ người báo cáo thiện chí.", "", "Ẩn danh, không trả đũa và điều tra độc lập là nguyên tắc tốt."),
        ("sanctions_screening", "Sàng lọc cấm vận", ["sanctions", "compliance"], "Doanh nghiệp xuyên biên giới thường cần sàng lọc đối tác, hàng hóa và giao dịch với danh sách hạn chế.", "", "Vi phạm có thể dẫn tới hậu quả pháp lý và tài chính rất lớn."),
        ("export_controls", "Kiểm soát xuất khẩu", ["dual-use", "giấy phép"], "Một số hàng hóa, công nghệ hoặc dữ liệu cần giấy phép trước khi xuất khẩu/chuyển giao.", "", "Đặc biệt quan trọng với hàng lưỡng dụng và công nghệ nhạy cảm."),
    ]
    docs.extend(
        [
            make_doc("law_safety", topic, title, keywords, explanation, formulas, definitions)
            for topic, title, keywords, explanation, formulas, definitions in law_safety_docs
        ]
    )

    general_docs = [
        ("logic_deduction", "Suy luận diễn dịch", ["logic", "mệnh đề"], "Nếu tiền đề đúng và lập luận hợp lệ thì kết luận phải đúng.", "", "Phân biệt diễn dịch với quy nạp."),
        ("logic_induction", "Suy luận quy nạp", ["mẫu quan sát"], "Từ các quan sát cụ thể suy ra kết luận tổng quát có tính xác suất.", "", "Kết luận quy nạp có thể mạnh hoặc yếu tùy bằng chứng."),
        ("correlation_causation", "Tương quan và nhân quả", ["thống kê", "nguyên nhân"], "Tương quan không tự động hàm ý quan hệ nhân quả.", "", "Có thể tồn tại biến nhiễu hoặc quan hệ đảo chiều."),
        ("median_vs_mean", "Trung vị so với trung bình", ["outlier"], "Trung vị thường bền vững hơn trước ngoại lệ, còn trung bình dùng toàn bộ dữ liệu.", "", "Dữ liệu lệch mạnh thường làm trung vị hữu ích hơn."),
        ("sampling_bias", "Sai lệch chọn mẫu", ["khảo sát", "mẫu"], "Mẫu không đại diện dẫn đến kết luận sai lệch về tổng thể.", "", "Lấy mẫu ngẫu nhiên và đủ lớn giúp giảm sai lệch."),
        ("confidence_interval", "Khoảng tin cậy", ["ước lượng"], "Khoảng giá trị hợp lý cho tham số tổng thể dựa trên mẫu.", "", "Độ rộng phụ thuộc phương sai, cỡ mẫu và mức tin cậy."),
        ("base_rate", "Tỷ lệ nền", ["xác suất Bayes"], "Bỏ qua tỷ lệ nền dễ dẫn tới đánh giá sai xác suất thực tế.", "", "Rất quan trọng trong bài toán xét nghiệm và phân loại."),
        ("bayes_rule", "Định lý Bayes", ["xác suất có điều kiện"], "Cập nhật niềm tin khi có bằng chứng mới.", "P(A|B)=P(B|A)P(A)/P(B)", "Kết hợp tỷ lệ nền với độ nhạy/độ đặc hiệu."),
        ("false_positive_negative", "Dương tính giả và âm tính giả", ["độ nhạy", "độ đặc hiệu"], "Một xét nghiệm hoặc mô hình phân loại có thể sai theo hai hướng.", "", "Đánh đổi giữa hai loại sai tùy ngưỡng quyết định."),
        ("normal_distribution", "Phân phối chuẩn", ["bell curve"], "Phân phối đối xứng hình chuông với nhiều tính chất quan trọng trong thống kê.", "", "Khoảng 68-95-99.7% nằm trong 1-2-3 độ lệch chuẩn."),
        ("central_limit", "Định lý giới hạn trung tâm", ["mẫu lớn"], "Trung bình mẫu có xu hướng gần chuẩn khi cỡ mẫu đủ lớn.", "", "Là nền tảng của nhiều xấp xỉ thống kê."),
        ("precision_recall", "Precision và Recall", ["machine learning", "phân loại"], "Precision đo độ chính xác của dự báo dương; recall đo mức bao phủ các trường hợp dương thật.", "", "F1 cân bằng tương đối giữa precision và recall."),
        ("f1_score", "F1-score", ["precision", "recall"], "Trung bình điều hòa của precision và recall.", "F1 = 2PR/(P+R)", "Hữu ích khi lớp dữ liệu mất cân bằng."),
        ("overfitting", "Quá khớp", ["machine learning"], "Mô hình học quá sát dữ liệu huấn luyện nên tổng quát hóa kém.", "", "Regularization, validation và thêm dữ liệu giúp giảm overfitting."),
        ("underfitting", "Thiếu khớp", ["bias"], "Mô hình quá đơn giản nên không nắm được quy luật chính của dữ liệu.", "", "Biểu hiện bởi lỗi cao trên cả train và test."),
        ("train_validation_test", "Tách train/validation/test", ["đánh giá mô hình"], "Ba tập dữ liệu phục vụ huấn luyện, chọn siêu tham số và đánh giá cuối cùng.", "", "Không dùng test set để tuning."),
        ("binary_hex", "Nhị phân và thập lục phân", ["cơ số"], "Hex thuận tiện để biểu diễn nhóm 4 bit nhị phân.", "", "A-F tương ứng 10-15 trong hệ 16."),
        ("ascii_unicode", "ASCII và Unicode", ["mã hóa ký tự"], "ASCII chỉ bao phủ tập ký tự nhỏ; Unicode bao phủ đa ngôn ngữ rộng hơn.", "", "UTF-8 là cách mã hóa Unicode rất phổ biến."),
        ("http_methods", "Các phương thức HTTP cơ bản", ["GET", "POST", "PUT", "DELETE"], "Mỗi phương thức biểu thị ý nghĩa thao tác khác nhau với tài nguyên web.", "", "GET thường an toàn/idempotent hơn POST."),
        ("cache_definition", "Cache", ["bộ nhớ đệm"], "Cache lưu tạm dữ liệu truy cập thường xuyên để giảm độ trễ.", "", "Có nhiều tầng cache: CPU, ứng dụng, CDN, trình duyệt."),
        ("latency_vs_throughput", "Latency và Throughput", ["hiệu năng"], "Latency là độ trễ cho một yêu cầu; throughput là số lượng xử lý theo đơn vị thời gian.", "", "Tối ưu một chỉ số không luôn tối ưu chỉ số còn lại."),
        ("encryption_hashing", "Mã hóa và băm", ["crypto"], "Mã hóa có thể giải ngược bằng khóa; băm nhằm tạo dấu vân tay một chiều.", "", "Không dùng hash thay cho encryption khi cần khôi phục dữ liệu."),
        ("auth_vs_authz", "Authentication và Authorization", ["xác thực", "phân quyền"], "Authentication trả lời bạn là ai, authorization trả lời bạn được làm gì.", "", "Hai bước này khác nhau nhưng thường đi cùng nhau."),
        ("sql_injection", "SQL Injection", ["bảo mật ứng dụng"], "Khai thác việc ghép chuỗi truy vấn không an toàn để thao túng cơ sở dữ liệu.", "", "Prepared statements là biện pháp phòng vệ chuẩn."),
        ("xss", "Cross-Site Scripting", ["XSS", "browser"], "Chèn script độc hại vào nội dung được trình duyệt người dùng thực thi.", "", "Escape output và CSP giúp giảm rủi ro."),
        ("phishing", "Phishing", ["lừa đảo"], "Kỹ thuật lừa người dùng tiết lộ thông tin nhạy cảm bằng cách giả mạo nguồn tin cậy.", "", "Cảnh giác URL, tệp đính kèm và yêu cầu khẩn cấp bất thường."),
        ("root_cause", "Nguyên nhân gốc", ["RCA"], "Giải pháp bền vững cần xử lý nguyên nhân gốc thay vì chỉ triệu chứng.", "", "5 Whys và fishbone là các kỹ thuật hay dùng."),
        ("project_scope", "Phạm vi dự án", ["scope"], "Xác định rõ phạm vi giúp giảm trượt mục tiêu và overrun.", "", "Scope creep là việc mở rộng phạm vi không kiểm soát."),
        ("stakeholder", "Stakeholder", ["bên liên quan"], "Bên liên quan là cá nhân/tổ chức có lợi ích hoặc ảnh hưởng đến dự án/quyết định.", "", "Nhận diện stakeholder giúp truyền thông và ưu tiên tốt hơn."),
        ("risk_matrix", "Ma trận rủi ro", ["impact", "likelihood"], "Rủi ro thường được đánh giá theo xác suất và mức độ ảnh hưởng.", "", "Ưu tiên xử lý rủi ro xác suất cao và tác động lớn."),
    ]
    docs.extend(
        [
            make_doc("general_knowledge", topic, title, keywords, explanation, formulas, definitions)
            for topic, title, keywords, explanation, formulas, definitions in general_docs
        ]
    )

    economics_extra_docs = [
        ("balance_sheet", "Bảng cân đối kế toán", ["tài sản", "nợ phải trả"], "Cho biết tình hình tài chính tại một thời điểm.", "Tài sản = Nợ phải trả + Vốn chủ sở hữu", "Khác với báo cáo kết quả kinh doanh là theo kỳ."),
        ("income_statement", "Báo cáo kết quả kinh doanh", ["doanh thu", "chi phí"], "Phản ánh hiệu quả hoạt động trong một kỳ.", "", "Lợi nhuận ròng = doanh thu - chi phí sau thuế và các khoản liên quan."),
        ("cash_flow", "Báo cáo lưu chuyển tiền tệ", ["operating", "investing", "financing"], "Theo dõi dòng tiền vào ra theo hoạt động kinh doanh, đầu tư, tài trợ.", "", "Lợi nhuận và dòng tiền không phải lúc nào cũng trùng nhau."),
        ("current_ratio", "Current Ratio", ["thanh khoản"], "Khả năng thanh toán ngắn hạn bằng tài sản ngắn hạn.", "Current ratio = Current assets / Current liabilities", "Chỉ số quá thấp làm tăng rủi ro thanh khoản."),
        ("quick_ratio", "Quick Ratio", ["acid test"], "Chỉ số thanh khoản chặt hơn vì loại hàng tồn kho.", "Quick ratio = (Current assets - Inventory) / Current liabilities", ""),
        ("debt_to_equity", "Debt-to-Equity", ["đòn bẩy"], "Mức độ sử dụng nợ so với vốn chủ sở hữu.", "D/E = Total debt / Equity", "Đòn bẩy cao làm tăng rủi ro tài chính."),
        ("gross_margin", "Biên lợi nhuận gộp", ["gross profit"], "Cho biết phần doanh thu còn lại sau giá vốn.", "Gross margin = Gross profit / Revenue", ""),
        ("net_margin", "Biên lợi nhuận ròng", ["net profit"], "Tỷ lệ lợi nhuận ròng trên doanh thu.", "Net margin = Net income / Revenue", ""),
        ("inventory_turnover", "Vòng quay hàng tồn kho", ["inventory"], "Đo tốc độ bán và thay thế hàng tồn kho.", "Inventory turnover = COGS / Average inventory", ""),
        ("dscr", "Debt Service Coverage Ratio", ["dòng tiền", "nợ"], "Khả năng trang trải nghĩa vụ nợ bằng dòng tiền hoạt động.", "DSCR = Operating income / Debt service", ""),
        ("foreign_exchange", "Tỷ giá hối đoái", ["forex"], "Giá của một đồng tiền biểu thị bằng đồng tiền khác.", "", "Tỷ giá ảnh hưởng thương mại, lạm phát và dòng vốn."),
        ("purchasing_power_parity", "Ngang giá sức mua", ["PPP"], "Trong dài hạn tỷ giá có xu hướng phản ánh sức mua tương đối giữa hai nền kinh tế.", "", "Dùng trong so sánh quốc tế mức sống/GDP."),
        ("fisher_equation", "Phương trình Fisher", ["lãi suất thực"], "Liên hệ lãi suất danh nghĩa, lãi suất thực và lạm phát kỳ vọng.", "i ≈ r + π^e", ""),
        ("yield_curve", "Đường cong lợi suất", ["trái phiếu"], "Quan hệ giữa lợi suất và kỳ hạn của công cụ nợ cùng rủi ro.", "", "Đường cong đảo ngược đôi khi được xem là tín hiệu suy thoái."),
        ("dividend_discount", "Mô hình chiết khấu cổ tức", ["DDM"], "Định giá cổ phiếu bằng giá trị hiện tại của cổ tức tương lai.", "P0 = D1/(r-g)", "Áp dụng phù hợp hơn với doanh nghiệp trả cổ tức ổn định."),
        ("breakeven", "Điểm hòa vốn", ["cost-volume-profit"], "Mức sản lượng/doanh thu tại đó tổng doanh thu bằng tổng chi phí.", "Q_BE = Fixed cost / (Price - Variable cost/unit)", ""),
        ("marginal_cost", "Chi phí cận biên", ["MC"], "Chi phí tăng thêm khi sản xuất thêm một đơn vị sản lượng.", "", "MC thường quan trọng trong quyết định tối ưu ngắn hạn."),
        ("average_total_cost", "Chi phí bình quân toàn phần", ["ATC"], "Tổng chi phí chia cho sản lượng.", "ATC = TC / Q", ""),
        ("producer_consumer_surplus", "Thặng dư tiêu dùng và thặng dư sản xuất", ["welfare"], "Đo lợi ích của người mua và người bán trên thị trường.", "", "Biến động giá và chính sách thuế ảnh hưởng hai đại lượng này."),
        ("tax_incidence", "Gánh nặng thuế", ["co giãn"], "Người chịu gánh nặng thuế nhiều hơn thường là phía kém co giãn hơn.", "", "Không nhất thiết rơi vào bên có nghĩa vụ nộp thuế danh nghĩa."),
    ]
    docs.extend(
        [
            make_doc("economics_finance", topic, title, keywords, explanation, formulas, definitions)
            for topic, title, keywords, explanation, formulas, definitions in economics_extra_docs
        ]
    )

    computer_science_extra_docs = [
        ("heap_priority_queue", "Heap và priority queue", ["heap", "ưu tiên"], "Heap hỗ trợ lấy phần tử ưu tiên cao/thấp nhất hiệu quả.", "", "Min-heap và max-heap có tính chất cây gần hoàn chỉnh."),
        ("union_find", "Union-Find", ["disjoint set"], "Cấu trúc dữ liệu quản lý các tập rời nhau và hỗ trợ hợp nhất/tìm đại diện.", "", "Hay dùng trong Kruskal và bài toán kết nối."),
        ("topological_sort", "Sắp xếp topo", ["DAG"], "Sắp xếp đỉnh của DAG sao cho mọi cạnh đi từ trước ra sau.", "", "Không tồn tại nếu đồ thị có chu trình."),
        ("mst", "Cây khung nhỏ nhất", ["Kruskal", "Prim"], "Kết nối tất cả đỉnh với tổng trọng số nhỏ nhất.", "", "Áp dụng cho đồ thị vô hướng liên thông có trọng số."),
        ("bellman_ford", "Bellman-Ford", ["cạnh âm"], "Tìm đường đi ngắn nhất kể cả khi có cạnh âm nếu không có chu trình âm.", "", "Chậm hơn Dijkstra nhưng tổng quát hơn."),
        ("normal_forms", "Chuẩn 1NF/2NF/3NF", ["database"], "Các mức chuẩn hóa giúp giảm dư thừa và bất nhất dữ liệu.", "", "1NF loại bỏ nhóm lặp; 2NF loại phụ thuộc bộ phận; 3NF loại phụ thuộc bắc cầu."),
        ("indexing", "Chỉ mục cơ sở dữ liệu", ["B-tree"], "Chỉ mục tăng tốc truy vấn đọc nhưng có chi phí ghi và lưu trữ.", "", "Không phải truy vấn nào cũng được lợi như nhau từ index."),
        ("tcp_udp", "TCP và UDP", ["transport"], "TCP tin cậy, có kết nối; UDP nhẹ hơn nhưng không đảm bảo giao hàng.", "", "Chọn giao thức theo yêu cầu ứng dụng."),
        ("dns", "DNS", ["phân giải tên"], "Hệ thống phân giải tên miền thành địa chỉ IP.", "", "Có phân cấp và cơ chế cache rộng rãi."),
        ("http_status", "Mã trạng thái HTTP", ["200", "404", "500"], "Mã trạng thái cho biết kết quả xử lý yêu cầu HTTP.", "", "2xx thành công, 4xx lỗi phía client, 5xx lỗi phía server."),
        ("rest_basics", "REST cơ bản", ["resource", "stateless"], "Phong cách thiết kế API xoay quanh tài nguyên và giao tiếp stateless.", "", "URL thường đại diện tài nguyên, phương thức HTTP đại diện thao tác."),
        ("concurrency_parallelism", "Concurrency và Parallelism", ["đa luồng"], "Concurrency là quản lý nhiều việc chồng lấp; parallelism là thực thi đồng thời thật sự.", "", "Hai khái niệm liên quan nhưng không đồng nhất."),
        ("deadlock", "Deadlock", ["khóa"], "Tình trạng tiến trình chờ lẫn nhau vô hạn.", "", "Bốn điều kiện kinh điển gồm loại trừ tương hỗ, giữ và chờ, không tước đoạt, chờ vòng tròn."),
        ("paging_virtual_memory", "Phân trang và bộ nhớ ảo", ["page", "frame"], "Cho phép chương trình dùng không gian địa chỉ lớn hơn RAM vật lý.", "", "Page fault xảy ra khi trang cần thiết chưa ở trong RAM."),
        ("compiler_interpreter", "Compiler và Interpreter", ["biên dịch", "thông dịch"], "Compiler dịch trước, interpreter thực thi từng phần/trực tiếp hơn.", "", "Nhiều ngôn ngữ hiện đại kết hợp cả hai cách."),
        ("oop_principles", "Nguyên lý OOP", ["encapsulation", "inheritance", "polymorphism"], "Các khái niệm lõi gồm đóng gói, kế thừa, đa hình, trừu tượng.", "", "Dùng để tổ chức mã theo đối tượng và hành vi."),
        ("git_basics", "Khái niệm Git cơ bản", ["commit", "branch", "merge"], "Git quản lý lịch sử thay đổi của mã nguồn theo commit và branch.", "", "Commit ghi snapshot, branch cho phép phát triển song song."),
        ("testing_pyramid", "Testing pyramid", ["unit", "integration", "e2e"], "Khuyến nghị nhiều unit test hơn integration và e2e để giữ tốc độ và ổn định.", "", "Tùy hệ thống mà tỉ lệ cụ thể có thể khác."),
        ("ci_cd", "CI/CD", ["automation"], "CI tự động kiểm tra tích hợp liên tục; CD tự động phát hành hoặc triển khai.", "", "Giúp giảm lỗi thủ công và tăng tốc vòng phản hồi."),
        ("container_basics", "Container cơ bản", ["docker"], "Container đóng gói ứng dụng cùng phụ thuộc ở mức nhẹ hơn máy ảo.", "", "Chung kernel host nhưng cô lập tiến trình và filesystem ở mức nhất định."),
    ]
    docs.extend(
        [
            make_doc("computer_science", topic, title, keywords, explanation, formulas, definitions)
            for topic, title, keywords, explanation, formulas, definitions in computer_science_extra_docs
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
    if not 250 <= len(documents) <= 400:
        raise ValueError(f"Expected 250-400 documents, got {len(documents)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(documents)} documents to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
