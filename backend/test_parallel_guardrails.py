
import asyncio
import time
from agents.workflow import create_rag_workflow
from agents.state import ChatState

async def test_parallel_guardrails():
    """Test parallel guardrails processing"""
    
    # Tạo workflow
    workflow = create_rag_workflow()
    
    # Tạo test state
    test_state = ChatState(
        question="Xin chào, tôi muốn hỏi về thủ tục đăng ký kinh doanh",
        session_id="test_session_001",
        messages=[],
        processing_time={},
        thread_id="test_thread_001",
        checkpoint_ns="test_namespace",
        checkpoint_id="test_checkpoint_001"
    )
    
    print("=== Testing Parallel Guardrails Processing ===")
    print(f"Question: {test_state['question']}")
    print(f"Session ID: {test_state['session_id']}")
    
    start_time = time.time()
    
    try:
        # Chạy workflow
        result = await workflow.ainvoke(test_state)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n=== Results ===")
        print(f"Total processing time: {total_time:.4f}s")
        print(f"Answer: {result.get('answer', 'No answer')}")
        print(f"Error: {result.get('error', 'None')}")
        print(f"Guardrails output validated: {result.get('guardrails_output_validated', False)}")
        print(f"Parallel guardrails completed: {result.get('parallel_guardrails_completed', False)}")
        print(f"Generation completed: {result.get('generation_completed', False)}")
        
        # In processing times
        processing_times = result.get('processing_time', {})
        print(f"\n=== Processing Times ===")
        for key, value in processing_times.items():
            print(f"{key}: {value:.4f}s")
        
        # Kiểm tra parallel processing
        if 'parallel_output_validation' in processing_times and 'answer_generation' in processing_times:
            parallel_time = processing_times['parallel_output_validation']
            generation_time = processing_times['answer_generation']
            
            print(f"\n=== Parallel Processing Analysis ===")
            print(f"Generation time: {generation_time:.4f}s")
            print(f"Parallel guardrails time: {parallel_time:.4f}s")
            
            # Nếu parallel processing hoạt động, tổng thời gian sẽ gần bằng max(generation_time, parallel_time)
            expected_parallel_time = max(generation_time, parallel_time)
            actual_time = total_time
            
            print(f"Expected parallel time: {expected_parallel_time:.4f}s")
            print(f"Actual total time: {actual_time:.4f}s")
            
            if actual_time <= expected_parallel_time * 1.2:  # Cho phép 20% overhead
                print("✅ Parallel processing appears to be working!")
            else:
                print("❌ Parallel processing may not be working as expected")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_parallel_guardrails())
