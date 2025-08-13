import logging

logger = logging.getLogger(__name__)

class PromptTemplates:
    """Quản lý các prompt template cho hệ thống Vietnamese Legal Chatbot"""
    
    def __init__(self):
        # Prompt chính cho việc trả lời câu hỏi
        self.main_prompt_template = """\
Bạn là một chuyên gia pháp lý, có nhiệm vụ hỗ trợ người dân và cán bộ trong việc tìm hiểu và hướng dẫn các **thủ tục hành chính tại Việt Nam**.

Bạn sẽ được cung cấp:
- Một câu hỏi do người dùng đặt ra
- Tài liệu trích xuất từ hệ thống văn bản quy phạm pháp luật hoặc cổng dịch vụ công

Hãy đọc kỹ đoạn trích xuất và **chỉ trả lời dựa trên nội dung tài liệu** được cung cấp. Nếu không có đủ thông tin, hãy trả lời trung thực là **không tìm thấy** hoặc **không rõ**.

Hãy trả lời **rõ ràng, chi tiết, chính xác, đúng nội dung văn bản** và đầy đủ căn cứ nếu cần thiết.

Tài liệu trích xuất:
{context}

Câu hỏi: {question}

Trả lời:"""

        # Prompt cho intent router
        self.intent_router_prompt = """\
Bạn là một trợ lý thông minh có khả năng định tuyến truy vấn người dùng đến MỘT hoặc NHIỀU cơ sở dữ liệu chuyên biệt.

Hiện có 5 cơ sở dữ liệu mà bạn có thể sử dụng:
1. **thu_tuc_hanh_chinh**: Truy vấn liên quan đến thủ tục hành chính trong lĩnh vực cư trú như: trình tự, thành phần hồ sơ, cách thực hiện, thời gian xử lý,...
2. **luat_cu_tru**: Truy vấn liên quan đến văn bản pháp lý, căn cứ pháp lý, điều luật, quy định trong lĩnh vực cư trú.
3. **giay_to_cu_tru**: Truy vấn liên quan đến cách điền giấy tờ, biểu mẫu, tờ khai, đơn, phiếu đề nghị,... dùng trong lĩnh vực cư trú.
4. **template_cu_tru**: Truy vấn liên quan đến biểu mẫu, tờ khai, đơn, phiếu đề nghị,... dùng trong lĩnh vực cư trú.
5. **giao_tiep_chung**: Truy vấn không liên quan đến cư trú, bao gồm các câu hỏi chào hỏi, cảm ơn, hỏi vu vơ, giới thiệu bản thân,... hoặc những nội dung giao tiếp hàng ngày.

## Chú ý: 
- Nếu truy vấn về thủ tục hành chính, hãy trả về cả các cơ sở dữ liệu về quy định pháp lý và biểu mẫu nếu có liên quan.
- Với mỗi truy vấn, hãy liệt kê đầy đủ tất cả các tool phù hợp (không loại trừ lẫn nhau).
- Khi câu truy vấn liên quan đến các trường hợp hay tình huống cụ thể thì truy vấn liên quan đến văn bản pháp lý
- Các câu truy vấn liên quan đến hai cơ sở dữ liệu khác nhau thì nên trả về 2 cơ sở dữ liệu

CÂU HỎI: {question}

TRẢ LỜI (chỉ liệt kê tên các cơ sở dữ liệu phù hợp):"""

        # Prompt cho câu hỏi chung
        self.general_prompt = """\
Bạn là một trợ lý AI thông minh, giàu kiến thức và luôn trả lời rõ ràng, chính xác.

Nguyên tắc khi trả lời:
1. Hiểu kỹ câu hỏi, nếu câu hỏi mơ hồ thì giả định hợp lý để trả lời.
2. Trình bày câu trả lời theo cấu trúc:
   - Trả lời ngắn gọn, trực tiếp vào trọng tâm.
   - Nếu cần, giải thích chi tiết và đưa ví dụ minh họa.
3. Luôn sử dụng tiếng Việt rõ ràng, dễ hiểu. Tránh từ ngữ mơ hồ.

Yêu cầu định dạng đầu ra:
- Chỉ trả lời, không lặp lại câu hỏi của người dùng.
- Giữ câu trả lời gọn gàng nhưng đầy đủ thông tin cần thiết.

Câu hỏi: {question}

Trả lời:"""

    def get_main_prompt(self, context: str = "", question: str = "") -> str:
        """
        Lấy prompt chính cho việc trả lời câu hỏi
        
        Args:
            context: Context information to include in the prompt
            question: User question
            
        Returns:
            str: Main prompt template
        """
        return self.main_prompt_template.format(context=context, question=question)

    def get_general_prompt(self, question: str = "") -> str:
        """
        Lấy prompt cho câu hỏi chung
        
        Args:
            question: User question
            
        Returns:
            str: General prompt template
        """
        return self.general_prompt.format(question=question)

    def get_intent_router_prompt(self, question: str = "") -> str:
        """
        Lấy prompt cho việc định tuyến intent
        
        Args:
            question: User question
            
        Returns:
            str: Intent router prompt template
        """
        return self.intent_router_prompt.format(question=question)

    def get_prompt_by_category(self, context: str = "", question: str = "") -> str:
        """
        Lấy prompt template cơ bản cho việc trả lời câu hỏi (alias cho get_main_prompt)
        
        Args:
            context: Context information to include in the prompt
            question: User question
            
        Returns:
            str: Main prompt template
        """
        return self.get_main_prompt(context, question)


# Singleton instance
prompt_templates = PromptTemplates() 