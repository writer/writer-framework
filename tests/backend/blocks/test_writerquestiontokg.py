import pytest
import writer.ai
from writer.blocks.writerquestiontokg import WriterQuestionToKG
from writer.ss_types import WriterConfigurationError

# Create a mock response object
class MockQuestion:
    def __init__(self, answer="Test answer", subqueries=None):
        self.answer = answer
        self.subqueries = subqueries or []

class MockGraphs:
    def question(self, graph_ids, question, stream, subqueries):
        # Don't assert specific graph IDs, just verify it's a list
        assert isinstance(graph_ids, list)
        assert isinstance(question, str)
        assert isinstance(stream, bool)
        assert isinstance(subqueries, bool)
        
        # Return subqueries only if enabled
        return MockQuestion(
            answer="This is the answer",
            subqueries=["subquery1", "subquery2"] if subqueries else []
        )

class MockClient:
    def __init__(self):
        self.graphs = MockGraphs()

def mock_acquire_client():
    return MockClient()

def test_question_to_kg(monkeypatch, session, runner):
    monkeypatch.setattr(writer.ai.WriterAIManager, "acquire_client", mock_acquire_client)

    # 3. Setup: Add fake component (simulates UI input)
    session.add_fake_component({
        "graphId": "123e4567-e89b-12d3-a456-426614174000",
        "question": "What is the test question?",
        "subqueries": "yes"
    })
    
    # 4. Create and run the block
    block = WriterQuestionToKG("fake_id", runner, {})
    block.run()
    
    # 5. Verify the outcomes
    assert block.outcome == "success"
    assert isinstance(block.result, MockQuestion)
    assert block.result.answer == "This is the answer"
    assert block.result.subqueries == ["subquery1", "subquery2"] 

def test_question_to_kg_multiple_graph_ids(monkeypatch, session, runner):
    monkeypatch.setattr(writer.ai.WriterAIManager, "acquire_client", mock_acquire_client)

    # 3. Setup: Add fake component (simulates UI input)
    session.add_fake_component({
        "graphId": "123e4567-e89b-12d3-a456-426614174000, 123e4567-e89b-12d3-a456-426614174001",
        "question": "What is the test question?",
        "subqueries": "yes"
    }, id="fake_id_2")  
    
    # 4. Create and run the block
    block = WriterQuestionToKG("fake_id_2", runner, {})
    block.run()
    
    # 5. Verify the outcomes
    assert block.outcome == "success"
    assert isinstance(block.result, MockQuestion)
    assert block.result.answer == "This is the answer"
    assert block.result.subqueries == ["subquery1", "subquery2"] 


def test_question_to_kg_multiple_graph_ids_no_subqueries(monkeypatch, session, runner):
    monkeypatch.setattr(writer.ai.WriterAIManager, "acquire_client", mock_acquire_client)

    # 3. Setup: Add fake component (simulates UI input)
    session.add_fake_component({
        "graphId": "123e4567-e89b-12d3-a456-426614174000, 123e4567-e89b-12d3-a456-426614174001",
        "question": "What is the test question?",
        "subqueries": "no" 
    })
    
    # 4. Create and run the block
    block = WriterQuestionToKG("fake_id", runner, {})
    block.run()
    
    # 5. Verify the outcomes
    assert block.outcome == "success"
    assert isinstance(block.result, MockQuestion)
    assert block.result.answer == "This is the answer"
    assert block.result.subqueries == [] 


def test_question_to_kg_missing_graph_id(monkeypatch, session, runner):
    monkeypatch.setattr(writer.ai.WriterAIManager, "acquire_client", mock_acquire_client)

    # 3. Setup: Add fake component (simulates UI input)
    session.add_fake_component({
        "graphId": "",
        "question": "What is the test question?",
        "subqueries": "yes"
    })
    
    # 4. Create and run the block
    block = WriterQuestionToKG("fake_id", runner, {})
    with pytest.raises(WriterConfigurationError):
        block.run()
    
def test_question_to_kg_missing_required_fields(session, runner):
    # Test missing graphId
    session.add_fake_component({
        "question": "What is the test question?"
    }, id="fake_id_3")  
    
    block = WriterQuestionToKG("fake_id_3", runner, {})
    with pytest.raises(WriterConfigurationError):
        block.run()

    # Test missing question
    session.add_fake_component({
        "graphId": "123e4567-e89b-12d3-a456-426614174000"
    }, id="fake_id_4")  
    block = WriterQuestionToKG("fake_id_4", runner, {})
    with pytest.raises(WriterConfigurationError):
        block.run()

def test_question_to_kg_empty_fields(session, runner):
    session.add_fake_component({
        "graphId": "",
        "question": "What is the test question?",
    }, id="fake_id_5")  
    
    block = WriterQuestionToKG("fake_id_5", runner, {})
    with pytest.raises(WriterConfigurationError):
        block.run()

    session.add_fake_component({
        "graphId": "123e4567-e89b-12d3-a456-426614174000",
        "question": "",
    }, id="fake_id_6")  
    
    block = WriterQuestionToKG("fake_id_6", runner, {})
    with pytest.raises(WriterConfigurationError):
        block.run()