"""Beginner-friendly Technical Analysis (TA) curriculum that pairs each day's lesson with the best matching real stock chart."""

from __future__ import annotations

from typing import Any

LESSONS: list[dict[str, Any]] = [
    {
        "id": 1,
        "slug": "candlestick-basics",
        "title": "Bài 1: Nến Nhật — Cuộc chiến giữa Phe Mua và Phe Bán",
        "focus_indicator": "candle",
        "concept_plain": (
            "Mỗi cây nến đại diện cho 1 ngày giao dịch. Thân nến XANH nghĩa là cuối ngày giá đóng cửa CAO hơn lúc mở cửa "
            "(phe Mua thắng). Thân nến ĐỎ nghĩa là đóng cửa THẤP hơn lúc mở (phe Bán thắng). "
            "Thân nến càng dài, phe thắng càng áp đảo."
        ),
        "how_to_spot": "Nhìn thân nến ngày cuối cùng bên phải biểu đồ: màu sắc và độ dài thân so với các ngày trước.",
        "quiz": {
            "question": "Một cây nến có thân màu XANH rất dài cho thấy điều gì trong phiên hôm đó?",
            "options": [
                "Phe Mua áp đảo, đẩy giá đóng cửa cao hơn nhiều so với giá mở cửa",
                "Không có ai giao dịch cổ phiếu đó",
                "Giá cổ phiếu chắc chắn sẽ giảm vào ngày mai",
            ],
            "answer_index": 0,
            "explanation": "Thân xanh dài thể hiện lực cầu (mua) rất mạnh trong phiên, kiểm soát từ lúc mở cửa đến khi đóng cửa.",
        },
    },
    {
        "id": 2,
        "slug": "wicks-and-pinbar",
        "title": "Bài 2: Râu nến (Bóng nến) — Dấu vết của sự từ chối giá",
        "focus_indicator": "wick",
        "concept_plain": (
            "Đường mảnh thò ra trên hoặc dưới thân nến gọi là 'râu nến'. Râu DƯỚI dài giống cây búa (nến rút chân) "
            "cho thấy trong phiên giá từng bị đạp xuống sâu, nhưng cuối phiên có lực mua mạnh kéo ngược lên — dấu hiệu có người đỡ giá. "
            "Ngược lại, râu TRÊN dài nghĩa là giá cố vượt lên nhưng bị bán dội xuống."
        ),
        "how_to_spot": "So sánh độ dài phần râu nến phía dưới/trên với phần thân đặc của cây nến hôm nay.",
        "quiz": {
            "question": "Khi giá giảm về vùng thấp rồi xuất hiện nến có râu dưới rất dài (nến rút chân), điều đó thường báo hiệu gì?",
            "options": [
                "Lực bán hoàn toàn áp đảo tới cuối phiên",
                "Có lực cầu bắt đáy xuất hiện, từ chối mức giá thấp",
                "Công ty sắp phá sản",
            ],
            "answer_index": 1,
            "explanation": "Râu dưới dài nghĩa là phe bán đã đẩy giá xuống nhưng phe mua kéo giá bật ngược trở lại trước khi đóng cửa.",
        },
    },
    {
        "id": 3,
        "slug": "volume-fuel",
        "title": "Bài 3: Khối lượng (Volume) — 'Nhiên liệu' kiểm chứng giá",
        "focus_indicator": "volume",
        "concept_plain": (
            "Giá tăng giống như chiếc xe chạy nhanh, còn Khối lượng (các cột ở nửa dưới biểu đồ) chính là lượng xăng. "
            "Giá tăng mạnh KÈM cột khối lượng cao hơn đường trung bình 20 ngày (MA20 Vol) chứng tỏ dòng tiền lớn thực sự vào cuộc, đáng tin hơn tăng mà thanh khoản lèo tèo."
        ),
        "how_to_spot": "Nhìn cột Volume cuối cùng ở nửa dưới biểu đồ xem có cao vượt trội so với các cột xung quanh không.",
        "quiz": {
            "question": "Khi cổ phiếu tăng giá mạnh nhưng cột Volume lại thấp hơn hẳn mức trung bình, bạn nên nghĩ thế nào?",
            "options": [
                "Tín hiệu rất đáng tin, nên mua đuổi ngay",
                "Thận trọng vì giá tăng thiếu sự đồng thuận của dòng tiền lớn",
                "Volume không liên quan gì đến giá",
            ],
            "answer_index": 1,
            "explanation": "Giá tăng thiếu volume giống xe chạy mà thiếu xăng, dễ hụt hơi hoặc chỉ là nhịp kéo nhẹ thiếu lực cầu bền vững.",
        },
    },
    {
        "id": 4,
        "slug": "support-resistance",
        "title": "Bài 4: Hỗ trợ (Sàn đỡ) & Kháng cự (Trần cản)",
        "focus_indicator": "sr",
        "concept_plain": (
            "Hỗ trợ là vùng giá thấp mà trước đó cổ phiếu chạm vào rồi bật lên (giống sàn nhà đỡ quả bóng). "
            "Kháng cự là vùng đỉnh cũ mà giá cứ lên tới đó lại bị bán quay đầu (giống trần nhà). "
            "Người mới tuyệt đối tránh mua ngay sát trần Kháng cự, mà thường chờ xem giá có vượt dứt khoát trần đó hay không."
        ),
        "how_to_spot": "Nhìn 2 đường nét đứt ngang trên biểu đồ: đường xanh dưới là Hỗ trợ 20 phiên, đường đỏ trên là Kháng cự 20 phiên.",
        "quiz": {
            "question": "Tại sao người mới nên hạn chế mua ngay khi giá vừa chạm sát vùng Kháng cự cũ?",
            "options": [
                "Vì ở vùng đỉnh cũ thường có nhiều người đang chờ bán hòa vốn hoặc chốt lời",
                "Vì sàn giao dịch không cho mua",
                "Vì vùng kháng cự luôn có giá 0 đồng",
            ],
            "answer_index": 0,
            "explanation": "Kháng cự là nơi từng xuất hiện áp lực bán lớn, nên xác suất giá bị rung lắc hoặc điều chỉnh ngắn hạn ở đây rất cao.",
        },
    },
    {
        "id": 5,
        "slug": "ma20-compass",
        "title": "Bài 5: Đường MA20 — La bàn xu hướng ngắn hạn",
        "focus_indicator": "ma20",
        "concept_plain": (
            "MA20 là giá đóng cửa trung bình của 20 phiên (khoảng 1 tháng giao dịch). "
            "Khi giá nằm TRÊN đường MA20 và MA20 đang hướng lên, cổ phiếu đang trong nhịp khỏe ngắn hạn. "
            "Khi giá cắt từ dưới lên vượt qua MA20 kèm volume lớn, đó thường là tín hiệu cải thiện xu hướng đầu tiên."
        ),
        "how_to_spot": "Quan sát vị trí cây nến hôm nay so với đường màu cam (MA20) trên biểu đồ.",
        "quiz": {
            "question": "Đường MA20 thể hiện điều gì?",
            "options": [
                "Mức giá trung bình của cổ phiếu trong 20 phiên giao dịch gần nhất",
                "Lợi nhuận công ty trong 20 năm",
                "Số lượng cổ đông của công ty",
            ],
            "answer_index": 0,
            "explanation": "MA20 = Moving Average 20, tức giá trị trung bình động 20 phiên, giúp làm mượt nhiễu và nhìn rõ xu hướng ngắn hạn.",
        },
    },
    {
        "id": 6,
        "slug": "ma50-medium-trend",
        "title": "Bài 6: Đường MA50 — Xu hướng trung hạn & Điểm tựa lớn",
        "focus_indicator": "ma50",
        "concept_plain": (
            "MA50 tính trung bình khoảng 2,5 tháng giao dịch nên phản ánh xu hướng trung hạn ổn định hơn. "
            "Khi cả MA20 nằm trên MA50 và giá nằm trên cả hai đường, cổ phiếu đang ở cấu trúc tăng giá đẹp. "
            "Ngược lại, MA50 nằm phía trên giá thường đóng vai trò một trần cản cứng."
        ),
        "how_to_spot": "So sánh đường màu cam (MA20) và đường màu tím/xanh dương (MA50) cùng vị trí cây nến.",
        "quiz": {
            "question": "Trạng thái nào cho thấy xu hướng cổ phiếu đang khỏe và đồng thuận nhất?",
            "options": [
                "Giá nằm dưới cả MA20 và MA50",
                "Giá nằm trên MA20, và MA20 nằm trên MA50 cùng hướng lên",
                "MA20 và MA50 đi ngang dính sát nhau nhiều tháng",
            ],
            "answer_index": 1,
            "explanation": "Khi giá > MA20 > MA50 và dốc lên, cả xu hướng ngắn hạn lẫn trung hạn đều ủng hộ phe Mua.",
        },
    },
    {
        "id": 7,
        "slug": "rsi-momentum",
        "title": "Bài 7: Chỉ số RSI — Nhiệt kế đo độ 'nóng' và 'lạnh'",
        "focus_indicator": "rsi",
        "concept_plain": (
            "RSI chạy từ 0 đến 100. Trên 70 gọi là 'Quá mua' — giá đã tăng nóng, nhiều người hưng phấn mua đuổi nên dễ có nhịp điều chỉnh nghỉ ngơi. "
            "Dưới 30 gọi là 'Quá bán' — giá bị bán tháo quá đà, dễ có nhịp hồi kỹ thuật. Vùng 45–65 là vùng khỏe ổn định."
        ),
        "how_to_spot": "Xem ô biểu đồ phụ dưới cùng: đường RSI đang ở mức nào so với 2 vạch đứt 30 và 70.",
        "quiz": {
            "question": "Khi thấy RSI lên mức 78, người mới nên lưu ý điều gì?",
            "options": [
                "Cổ phiếu đang ở vùng quá mua (tăng nóng), mua đuổi lúc này rủi ro điều chỉnh ngắn hạn cao",
                "Chắc chắn cổ phiếu sẽ tăng gấp đôi ngay ngày mai",
                "RSI 78 nghĩa là giá cổ phiếu là 78.000 đồng",
            ],
            "answer_index": 0,
            "explanation": "RSI >= 70 cảnh báo đà tăng ngắn hạn đã quá căng; không nên vội mua đuổi (FOMO) mà nên chờ nhịp hạ nhiệt.",
        },
    },
    {
        "id": 8,
        "slug": "macd-momentum-shift",
        "title": "Bài 8: MACD — Bắt nhịp đổi chiều động lượng",
        "focus_indicator": "ma20",
        "concept_plain": (
            "MACD đo khoảng cách giữa 2 đường trung bình nhanh (12 ngày) và chậm (26 ngày). "
            "Khi đường MACD cắt từ dưới lên trên đường Tín hiệu (Signal), động lượng đang chuyển từ yếu sang mạnh. "
            "Tuy nhiên MACD là chỉ báo trễ, nên dùng kèm Volume và vùng Hỗ trợ."
        ),
        "how_to_spot": "Kiểm tra xem đường MACD vừa cắt lên đường Signal hay đang mở rộng lên trên.",
        "quiz": {
            "question": "Điểm yếu phổ biến của chỉ báo MACD là gì?",
            "options": [
                "Là chỉ báo trễ (phản ứng sau khi giá đã chạy một đoạn)",
                "Chỉ dùng được cho tiền ảo",
                "Không thể vẽ trên biểu đồ ngày",
            ],
            "answer_index": 0,
            "explanation": "MACD tính từ các đường trung bình giá quá khứ nên có độ trễ; cần kết hợp nhìn nến và khối lượng.",
        },
    },
    {
        "id": 9,
        "slug": "breakout-vs-bulltrap",
        "title": "Bài 9: Phá vỡ thật (Breakout) vs Bẫy tăng giá (Bull Trap)",
        "focus_indicator": "sr",
        "concept_plain": (
            "Breakout thật là khi giá vượt qua Kháng cự với thân nến đóng cửa dứt khoát ở trên VÀ Volume nổ lớn (thường >= 1.5 lần trung bình). "
            "Còn nếu giá chỉ thò râu lên trên Kháng cự trong phiên rồi cuối ngày tụt lại bên dưới (kèm vol yếu), rất dễ là bẫy tăng giá (Bull Trap)."
        ),
        "how_to_spot": "Quan sát cây nến gần vùng Kháng cự 20 phiên cùng cột Volume tương ứng.",
        "quiz": {
            "question": "Dấu hiệu nào giúp phân biệt Breakout thật đáng tin hơn Bull Trap?",
            "options": [
                "Giá đóng cửa vượt hẳn kháng cự kèm khối lượng giao dịch tăng vọt",
                "Giá chỉ chạm nhẹ kháng cự giữa phiên rồi tụt xuống",
                "Khối lượng giao dịch càng nhỏ càng tốt",
            ],
            "answer_index": 0,
            "explanation": "Giá đóng cửa giữ vững trên kháng cự cùng dòng tiền lớn (volume cao) chứng tỏ phe mua thực sự chấp nhận mặt bằng giá mới.",
        },
    },
    {
        "id": 10,
        "slug": "risk-management-stoploss",
        "title": "Bài 10: Nguyên tắc sống còn — Cắt lỗ (Stop-loss) theo Hỗ trợ",
        "focus_indicator": "sr",
        "concept_plain": (
            "Phân tích kỹ thuật không phải để đoán đúng 100%, mà để biết KHI NÀO MÌNH SAI thì thoát sớm. "
            "Trước khi bấm nút mua, hãy nhìn vùng Hỗ trợ gần nhất hoặc đường MA20: nếu giá thủng xuống dưới mức đó với volume bán lớn, kịch bản tăng đã hỏng — cần tuân thủ kỷ luật hạ tỷ trọng."
        ),
        "how_to_spot": "Xác định sẵn vùng Hỗ trợ gần nhất bên dưới giá hiện tại trên biểu đồ.",
        "quiz": {
            "question": "Mục đích quan trọng nhất của Phân tích kỹ thuật đối với người mới là gì?",
            "options": [
                "Đoán chính xác 100% giá ngày mai",
                "Quản trị rủi ro, tìm điểm mua hợp lý và biết điểm cắt lỗ khi kịch bản sai",
                "Không cần quan tâm tin tức vĩ mô",
            ],
            "answer_index": 1,
            "explanation": "Không có phương pháp nào đúng 100%. TA giúp bạn có kế hoạch mua/bán kỷ luật và bảo vệ tài khoản khi thị trường đi ngược kỳ vọng.",
        },
    },
]


def _score_stock_for_lesson(stock: dict[str, Any], focus: str) -> float:
    c = stock["candle"]
    sig = stock["signals"]
    if focus == "candle":
        return c["body_pct"] + (10 if abs(stock["change_pct"]) >= 1.0 else 0)
    if focus == "wick":
        score = max(c["lower_wick_pct"], c["upper_wick_pct"])
        if c["is_hammer"] or c["is_shooting_star"]:
            score += 40
        return score
    if focus == "volume":
        return stock["vol_ratio"] * 30.0
    if focus == "sr":
        score = 10.0
        if sig["near_support"] or sig["near_resistance"]:
            score += 50.0
        return score
    if focus == "ma20":
        score = 10.0
        if sig["ma20_cross_up"]:
            score += 60.0
        elif stock["ma20"]:
            dist = abs(stock["close"] - stock["ma20"]) / stock["ma20"]
            score += max(0.0, 30.0 - dist * 500.0)
        return score
    if focus == "ma50":
        score = 10.0
        if stock["ma50"]:
            dist = abs(stock["close"] - stock["ma50"]) / stock["ma50"]
            score += max(0.0, 35.0 - dist * 400.0)
        return score
    if focus == "rsi":
        # Highlight stocks farthest from 50 (more educational on RSI)
        return abs(stock["rsi14"] - 50.0)
    return abs(stock["change_pct"])


def select_lesson_and_case_study(stocks: list[dict[str, Any]], day_index: int) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Pick today's sequential TA lesson and the stock in watchlist that best illustrates it today."""
    lesson = LESSONS[day_index % len(LESSONS)]
    if not stocks:
        return lesson, None

    best_stock = max(stocks, key=lambda s: _score_stock_for_lesson(s, lesson["focus_indicator"]))
    return lesson, best_stock
