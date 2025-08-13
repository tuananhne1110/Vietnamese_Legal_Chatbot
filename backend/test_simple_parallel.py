#!/usr/bin/env python3
"""
Test đơn giản để kiểm tra parallel guardrails processing
"""

import asyncio
import time
from agents.state import ChatState

# Mock functions để test parallel processing
async def mock_generate(state: ChatState) -> ChatState:
    """Mock generate function"""
    print("🔄 Starting generation...")
    await asyncio.sleep(2)  # Simulate LLM generation time
    state["answer"] = "Đây là câu trả lời mẫu về thủ tục đăng ký kinh doanh."
    state["answer_chunks"] = ["Đây là câu trả lời mẫu", " về thủ tục đăng ký kinh doanh."]
    state["generation_completed"] = True
    print("✅ Generation completed")
    return state

async def mock_parallel_guardrails(state: ChatState) -> ChatState:
    """Mock parallel guardrails function"""
    print("🔄 Starting parallel guardrails...")
    await asyncio.sleep(1.5)  # Simulate guardrails validation time
    state["guardrails_output_validated"] = True
    state["parallel_guardrails_completed"] = True
    print("✅ Parallel guardrails completed")
    return state

async def mock_merge_results(state: ChatState) -> ChatState:
    """Mock merge results function"""
    print("🔄 Merging results...")
    generated_answer = state.get("answer", "")
    guardrails_validated = state.get("guardrails_output_validated", False)
    parallel_completed = state.get("parallel_guardrails_completed", False)
    generation_completed = state.get("generation_completed", False)
    
    if generation_completed and parallel_completed:
        state["final_answer"] = generated_answer
        print("✅ Results merged successfully")
    else:
        print("⏳ Waiting for both processes to complete...")
    
    return state

async def test_parallel_processing():
    """Test parallel processing với mock functions"""
    
    print("=== Testing Simple Parallel Processing ===")
    
    # Tạo test state
    test_state = ChatState(
        question="Xin chào, tôi muốn hỏi về thủ tục đăng ký kinh doanh",
        session_id="test_session_001",
        messages=[],
        processing_time={}
    )
    
    start_time = time.time()
    
    try:
        # Chạy generate và parallel_guardrails song song
        print("\n🚀 Starting parallel execution...")
        
        # Tạo tasks cho parallel execution
        generate_task = asyncio.create_task(mock_generate(test_state))
        guardrails_task = asyncio.create_task(mock_parallel_guardrails(test_state))
        
        # Đợi cả hai tasks hoàn thành
        await asyncio.gather(generate_task, guardrails_task)
        
        # Merge results
        await mock_merge_results(test_state)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n=== Results ===")
        print(f"Total processing time: {total_time:.4f}s")
        print(f"Answer: {test_state.get('answer', 'No answer')}")
        print(f"Guardrails validated: {test_state.get('guardrails_output_validated', False)}")
        print(f"Parallel completed: {test_state.get('parallel_guardrails_completed', False)}")
        print(f"Generation completed: {test_state.get('generation_completed', False)}")
        
        # Kiểm tra parallel processing
        expected_parallel_time = max(2.0, 1.5)  # max(generation_time, guardrails_time)
        actual_time = total_time
        
        print(f"\n=== Parallel Processing Analysis ===")
        print(f"Expected parallel time: {expected_parallel_time:.4f}s")
        print(f"Actual total time: {actual_time:.4f}s")
        
        if actual_time <= expected_parallel_time * 1.2:  # Cho phép 20% overhead
            print("✅ Parallel processing is working correctly!")
        else:
            print("❌ Parallel processing may not be working as expected")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_parallel_processing())
