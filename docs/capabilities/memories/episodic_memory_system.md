## Episodic Memory System

Think of episodic memory as a personal diary for each user. When someone shares significant moments of their life with Casey - like "I graduated last week" or "I've been struggling with anxiety since my mother passed away" - Casey stores these important personal experiences. This isn't just data storage; it's contextual memory that helps Casey understand the user's personal journey. For example, in future conversations, Casey can reference these experiences ("When you mentioned graduating last week...") or understand the context of current emotions ("I remember you sharing about your loss..."), making interactions more personalized and meaningful.

### Purpose
Records significant personal experiences and interactions, enabling:
- Personal context awareness
- Empathetic responses
- Relationship building
- Experience-based learning

### Technical Implementation

#### Components
1. **EpisodicEventProcessor**
   - Event detection engine
   - Memory qualification system
   - Temporal context handler

2. **Vectara Service**
   - Vector storage for experiences
   - Context-aware retrieval
   - Temporal relationship mapping

3. **Groq LLM**
   - Experience analysis
   - Significance detection
   - Context extraction

### Workflow

1. **Trigger Points**
```
InteractionManager -> EpisodicEventProcessor
```

2. **Processing Steps**
   ```python
   # 1. Event Detection
   EpisodicEventProcessor.__detect_episodic_memory_parameters():
     - Analyzes conversation
     - Identifies significant events
     - Extracts temporal context
   
   # 2. Qualification
   EpisodicEventProcessor.__process_content():
     - Validates significance
     - Ensures personal relevance
     - Checks for temporal/location context
   
   # 3. Storage
   VectaraService.add_document_to_corpus():
     - Stores qualified memory
     - Creates temporal links
     - Maintains context
   ```

3. **Data Structure**
   ```xml
   <episodic_memories>
     <memory>
       <event>Significant personal experience</event>
       <context>
         <temporal>2024-03-21 14:30:00</temporal>
         <location>Optional location data</location>
         <significance>Personal relevance marker</significance>
       </context>
     </memory>
   </episodic_memories>
   ```

### Unique Features
- Temporal context preservation
- Personal significance detection
- Experience qualification
- Relationship-based storage