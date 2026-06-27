from ncc.memory import MemoryStore, build_memory_record
from ncc.schemas import MemoryRecord

def test_memory_store_insertion_and_search():
    store = MemoryStore()
    
    rec1 = build_memory_record(
        source_step=1,
        event_type="user_input",
        content="Construire NCC pour Mac",
        salience=0.9
    )
    store.add(rec1)
    
    rec2 = build_memory_record(
        source_step=2,
        event_type="user_input",
        content="Ajoute des tests unitaires",
        salience=0.5
    )
    store.add(rec2)
    
    # Search for Mac
    results = store.search("Mac")
    assert len(results) > 0
    assert results[0].content == "Construire NCC pour Mac"
