# enhanced_forms.py
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


class BusinessMatchForm(forms.Form):
    """Enhanced business matching form with additional options"""

    address = forms.CharField(
        label="Địa chỉ trung tâm",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: 227 Nguyễn Văn Cừ, Quận 5, TP.HCM',
            'autocomplete': 'address-line1'
        }),
        help_text="Nhập địa chỉ cụ thể để phân tích khu vực"
    )

    radius = forms.IntegerField(
        label="Bán kính phân tích (m)",
        min_value=100,
        max_value=5000,
        initial=2000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '100'
        }),
        help_text="Bán kính khu vực cần phân tích (100m - 5km)"
    )

    price_min = forms.IntegerField(
        label="Mức giá tối thiểu",
        min_value=1,
        max_value=4,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1 (rẻ nhất)'
        }),
        help_text="1: Rẻ, 2: Vừa phải, 3: Hơi đắt, 4: Đắt"
    )

    price_max = forms.IntegerField(
        label="Mức giá tối đa",
        min_value=1,
        max_value=4,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '4 (đắt nhất)'
        }),
        help_text="1: Rẻ, 2: Vừa phải, 3: Hơi đắt, 4: Đắt"
    )

    customer_target = forms.ChoiceField(
        label="Khách hàng mục tiêu",
        choices=[
            ("general", "Khách hàng phổ thông"),
            ("student", "Học sinh / Sinh viên"),
            ("office", "Dân văn phòng"),
            ("family", "Gia đình có trẻ em"),
            ("elderly", "Người cao tuổi"),
            ("tourist", "Khách du lịch"),
            ("young_professional", "Chuyên gia trẻ"),
        ],
        initial="general",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Advanced options
    analysis_depth = forms.ChoiceField(
        label="Độ sâu phân tích",
        choices=[
            ("basic", "Cơ bản - Nhanh"),
            ("standard", "Tiêu chuẩn - Cân bằng"),
            ("comprehensive", "Toàn diện - Chi tiết"),
        ],
        initial="standard",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Độ sâu phân tích ảnh hưởng đến thời gian và chi tiết kết quả"
    )


    market_condition = forms.ChoiceField(
        label="Điều kiện thị trường hiện tại",
        choices=[
            ("", "Tự động phát hiện"),
            ("growth", "Đang phát triển"),
            ("mature", "Ổn định/Trưởng thành"),
            ("declining", "Suy giảm"),
            ("emerging", "Mới nổi"),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Để trống để hệ thống tự động đánh giá"
    )

    location_type = forms.ChoiceField(
        label="Loại khu vực",
        choices=[
            ("", "Tự động phát hiện"),
            ("city_center", "Trung tâm thành phố"),
            ("residential", "Khu dân cư"),
            ("commercial", "Khu thương mại"),
            ("suburban", "Ngoại ô"),
            ("industrial", "Khu công nghiệp"),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Loại khu vực để điều chỉnh trọng số phân tích"
    )

    investment_budget = forms.DecimalField(
        label="Ngân sách đầu tư (triệu VNĐ)",
        max_digits=10,
        decimal_places=0,
        required=False,
        validators=[MinValueValidator(10)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: 500',
            'step': '10'
        }),
        help_text="Ngân sách dự kiến để lọc các ngành phù hợp"
    )

    business_experience = forms.ChoiceField(
        label="Kinh nghiệm kinh doanh",
        choices=[
            ("beginner", "Mới bắt đầu"),
            ("some_experience", "Có một ít kinh nghiệm"),
            ("experienced", "Có kinh nghiệm"),
            ("expert", "Chuyên gia"),
        ],
        initial="some_experience",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Mức độ kinh nghiệm ảnh hưởng đến khuyến nghị"
    )

    risk_tolerance = forms.ChoiceField(
        label="Mức độ chấp nhận rủi ro",
        choices=[
            ("conservative", "Thận trọng - Ít rủi ro"),
            ("moderate", "Vừa phải"),
            ("aggressive", "Tích cực - Chấp nhận rủi ro cao"),
        ],
        initial="moderate",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Mức độ rủi ro bạn sẵn sàng chấp nhận"
    )

    def clean(self):
        """Validate form data"""
        cleaned_data = super().clean()
        price_min = cleaned_data.get("price_min")
        price_max = cleaned_data.get("price_max")

        # Validate price range
        if price_min and price_max and price_min > price_max:
            raise forms.ValidationError("Giá tối thiểu không thể lớn hơn giá tối đa")

        return cleaned_data


class SensitivityAnalysisForm(forms.Form):
    """Form for sensitivity analysis parameters"""

    business_id = forms.CharField(widget=forms.HiddenInput())

    weight_adjustment = forms.DecimalField(
        label="Mức độ thay đổi trọng số (%)",
        max_digits=5,
        decimal_places=1,
        initial=20.0,
        validators=[MinValueValidator(5.0), MaxValueValidator(50.0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Phần trăm thay đổi trọng số để test (5% - 50%)"
    )

    factors_to_test = forms.MultipleChoiceField(
        label="Yếu tố cần phân tích",
        choices=[
            ("customer", "Phù hợp khách hàng"),
            ("competition", "Mức độ cạnh tranh"),
            ("market_potential", "Tiềm năng thị trường"),
            ("financial_viability", "Khả năng sinh lời"),
            ("transport", "Giao thông"),
            ("safety", "An toàn"),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Chọn các yếu tố muốn phân tích độ nhạy"
    )


class ScenarioForm(forms.Form):
    """Form for scenario planning"""

    business_id = forms.CharField(widget=forms.HiddenInput())

    scenario_name = forms.CharField(
        label="Tên kịch bản",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: Kịch bản kinh tế suy thoái'
        })
    )

    economic_growth = forms.DecimalField(
        label="Tăng trưởng kinh tế (%/năm)",
        max_digits=5,
        decimal_places=2,
        initial=0.0,
        validators=[MinValueValidator(-10.0), MaxValueValidator(15.0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Tốc độ tăng trưởng kinh tế dự kiến (-10% đến +15%)"
    )

    population_change = forms.DecimalField(
        label="Thay đổi dân số (%/năm)",
        max_digits=5,
        decimal_places=2,
        initial=0.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(10.0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Tốc độ thay đổi dân số (-5% đến +10%)"
    )

    competition_increase = forms.DecimalField(
        label="Gia tăng cạnh tranh (%)",
        max_digits=5,
        decimal_places=1,
        initial=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(200.0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1'
        }),
        help_text="Mức độ gia tăng đối thủ cạnh tranh (0% - 200%)"
    )

    infrastructure_improvement = forms.ChoiceField(
        label="Cải thiện hạ tầng",
        choices=[
            ("none", "Không thay đổi"),
            ("minor", "Cải thiện nhỏ"),
            ("moderate", "Cải thiện vừa"),
            ("major", "Cải thiện lớn"),
        ],
        initial="none",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    regulatory_changes = forms.ChoiceField(
        label="Thay đổi quy định",
        choices=[
            ("none", "Không thay đổi"),
            ("favorable", "Thuận lợi hơn"),
            ("neutral", "Trung tính"),
            ("restrictive", "Hạn chế hơn"),
        ],
        initial="none",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ComparisonForm(forms.Form):
    """Form for comparing multiple businesses"""

    business_ids = forms.MultipleChoiceField(
        label="Ngành cần so sánh",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Chọn tối đa 5 ngành để so sánh chi tiết"
    )

    comparison_criteria = forms.MultipleChoiceField(
        label="Tiêu chí so sánh",
        choices=[
            ("score", "Điểm tổng thể"),
            ("customer_fit", "Phù hợp khách hàng"),
            ("market_potential", "Tiềm năng thị trường"),
            ("competition", "Mức độ cạnh tranh"),
            ("financial_viability", "Khả năng sinh lời"),
            ("risk_level", "Mức độ rủi ro"),
        ],
        initial=["score", "risk_level"],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super().__init__(*args, **kwargs)

        # Dynamically populate business choices
        self.fields['business_ids'].choices = [
            (cat['id'], cat['name']) for cat in categories
        ]

    def clean_business_ids(self):
        """Validate business selection"""
        business_ids = self.cleaned_data.get('business_ids', [])

        if len(business_ids) < 2:
            raise forms.ValidationError("Vui lòng chọn ít nhất 2 ngành để so sánh")

        if len(business_ids) > 5:
            raise forms.ValidationError("Chỉ có thể so sánh tối đa 5 ngành")

        return business_ids


class ExportForm(forms.Form):
    """Form for exporting reports"""

    export_format = forms.ChoiceField(
        label="Định dạng xuất",
        choices=[
            ("pdf", "PDF - Báo cáo đầy đủ"),
            ("excel", "Excel - Dữ liệu chi tiết"),
            ("csv", "CSV - Dữ liệu thô"),
            ("json", "JSON - Dữ liệu API"),
        ],
        initial="pdf",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    include_charts = forms.BooleanField(
        label="Bao gồm biểu đồ",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Bao gồm biểu đồ và visualization trong báo cáo"
    )

    include_methodology = forms.BooleanField(
        label="Bao gồm phương pháp phân tích",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Giải thích chi tiết về phương pháp và thuật toán"
    )

    language = forms.ChoiceField(
        label="Ngôn ngữ",
        choices=[
            ("vi", "Tiếng Việt"),
            ("en", "English"),
        ],
        initial="vi",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FeedbackForm(forms.Form):
    """Form for user feedback on analysis results"""

    overall_satisfaction = forms.ChoiceField(
        label="Mức độ hài lòng tổng thể",
        choices=[
            (5, "Rất hài lòng"),
            (4, "Hài lòng"),
            (3, "Bình thường"),
            (2, "Không hài lòng"),
            (1, "Rất không hài lòng"),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    accuracy_rating = forms.ChoiceField(
        label="Độ chính xác kết quả",
        choices=[
            (5, "Rất chính xác"),
            (4, "Chính xác"),
            (3, "Tương đối chính xác"),
            (2, "Ít chính xác"),
            (1, "Không chính xác"),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    usefulness_rating = forms.ChoiceField(
        label="Tính hữu ích",
        choices=[
            (5, "Rất hữu ích"),
            (4, "Hữu ích"),
            (3, "Tương đối hữu ích"),
            (2, "Ít hữu ích"),
            (1, "Không hữu ích"),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    most_valuable_feature = forms.MultipleChoiceField(
        label="Tính năng hữu ích nhất",
        choices=[
            ("scoring", "Chấm điểm ngành"),
            ("rules", "Cảnh báo và quy tắc"),
            ("recommendations", "Khuyến nghị"),
            ("market_analysis", "Phân tích thị trường"),
            ("risk_assessment", "Đánh giá rủi ro"),
            ("sensitivity", "Phân tích độ nhạy"),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    suggestions = forms.CharField(
        label="Đề xuất cải thiện",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Chia sẻ ý kiến để chúng tôi cải thiện hệ thống...'
        }),
        required=False,
        help_text="Ý kiến đóng góp của bạn rất quan trọng với chúng tôi"
    )

    would_recommend = forms.BooleanField(
        label="Bạn có sẵn sàng giới thiệu hệ thống này không?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


# Form for admin/advanced users
class AdminAnalysisForm(BusinessMatchForm):
    """Extended form for admin users with advanced options"""

    custom_weights = forms.JSONField(
        label="Trọng số tùy chỉnh",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '{"customer": 0.3, "competition": 0.25, ...}'
        }),
        help_text="JSON định nghĩa trọng số tùy chỉnh cho từng yếu tố"
    )

    exclude_businesses = forms.MultipleChoiceField(
        label="Loại trừ ngành",
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Các ngành không muốn phân tích"
    )

    debug_mode = forms.BooleanField(
        label="Chế độ debug",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Hiển thị thông tin debug chi tiết"
    )

    cache_timeout = forms.IntegerField(
        label="Thời gian cache (giây)",
        initial=3600,
        min_value=300,
        max_value=86400,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Thời gian lưu cache kết quả (5 phút - 24 giờ)"
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super().__init__(*args, **kwargs)

        # Populate exclude_businesses choices
        self.fields['exclude_businesses'].choices = [
            (cat['id'], cat['name']) for cat in categories
        ]