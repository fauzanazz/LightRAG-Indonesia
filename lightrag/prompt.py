from __future__ import annotations
from typing import Any


PROMPTS: dict[str, Any] = {}

# ============================================================================
# PROMPTS_ID — Indonesian prompts for fact-checking domain
# Activated via USE_INDONESIAN_PROMPTS flag in addon_params
# When flag is OFF, original PROMPTS (English) are used — no behavioral change
# ============================================================================
PROMPTS_ID: dict[str, Any] = {}

# All delimiters must be formatted as "<|UPPER_CASE_STRING|>"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|#|>"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["entity_extraction_system_prompt"] = """---Role---
You are a Knowledge Graph Specialist responsible for extracting entities and relationships from the input text.

---Instructions---
1.  **Entity Extraction & Output:**
    *   **Identification:** Identify clearly defined and meaningful entities in the input text.
    *   **Entity Details:** For each identified entity, extract the following information:
        *   `entity_name`: The name of the entity. If the entity name is case-insensitive, capitalize the first letter of each significant word (title case). Ensure **consistent naming** across the entire extraction process.
        *   `entity_type`: Categorize the entity using one of the following types: `{entity_types}`. If none of the provided entity types apply, do not add new entity type and classify it as `Other`.
        *   `entity_description`: Provide a concise yet comprehensive description of the entity's attributes and activities, based *solely* on the information present in the input text.
    *   **Output Format - Entities:** Output a total of 4 fields for each entity, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `entity`.
        *   Format: `entity{tuple_delimiter}entity_name{tuple_delimiter}entity_type{tuple_delimiter}entity_description`

2.  **Relationship Extraction & Output:**
    *   **Identification:** Identify direct, clearly stated, and meaningful relationships between previously extracted entities.
    *   **N-ary Relationship Decomposition:** If a single statement describes a relationship involving more than two entities (an N-ary relationship), decompose it into multiple binary (two-entity) relationship pairs for separate description.
        *   **Example:** For "Alice, Bob, and Carol collaborated on Project X," extract binary relationships such as "Alice collaborated with Project X," "Bob collaborated with Project X," and "Carol collaborated with Project X," or "Alice collaborated with Bob," based on the most reasonable binary interpretations.
    *   **Relationship Details:** For each binary relationship, extract the following fields:
        *   `source_entity`: The name of the source entity. Ensure **consistent naming** with entity extraction. Capitalize the first letter of each significant word (title case) if the name is case-insensitive.
        *   `target_entity`: The name of the target entity. Ensure **consistent naming** with entity extraction. Capitalize the first letter of each significant word (title case) if the name is case-insensitive.
        *   `relationship_keywords`: One or more high-level keywords summarizing the overarching nature, concepts, or themes of the relationship. Multiple keywords within this field must be separated by a comma `,`. **DO NOT use `{tuple_delimiter}` for separating multiple keywords within this field.**
        *   `relationship_description`: A concise explanation of the nature of the relationship between the source and target entities, providing a clear rationale for their connection.
    *   **Output Format - Relationships:** Output a total of 5 fields for each relationship, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `relation`.
        *   Format: `relation{tuple_delimiter}source_entity{tuple_delimiter}target_entity{tuple_delimiter}relationship_keywords{tuple_delimiter}relationship_description`

3.  **Delimiter Usage Protocol:**
    *   The `{tuple_delimiter}` is a complete, atomic marker and **must not be filled with content**. It serves strictly as a field separator.
    *   **Incorrect Example:** `entity{tuple_delimiter}Tokyo<|location|>Tokyo is the capital of Japan.`
    *   **Correct Example:** `entity{tuple_delimiter}Tokyo{tuple_delimiter}location{tuple_delimiter}Tokyo is the capital of Japan.`

4.  **Relationship Direction & Duplication:**
    *   Treat all relationships as **undirected** unless explicitly stated otherwise. Swapping the source and target entities for an undirected relationship does not constitute a new relationship.
    *   Avoid outputting duplicate relationships.

5.  **Output Order & Prioritization:**
    *   Output all extracted entities first, followed by all extracted relationships.
    *   Within the list of relationships, prioritize and output those relationships that are **most significant** to the core meaning of the input text first.

6.  **Context & Objectivity:**
    *   Ensure all entity names and descriptions are written in the **third person**.
    *   Explicitly name the subject or object; **avoid using pronouns** such as `this article`, `this paper`, `our company`, `I`, `you`, and `he/she`.

7.  **Language & Proper Nouns:**
    *   The entire output (entity names, keywords, and descriptions) must be written in `{language}`.
    *   Proper nouns (e.g., personal names, place names, organization names) should be retained in their original language if a proper, widely accepted translation is not available or would cause ambiguity.

8.  **Completion Signal:** Output the literal string `{completion_delimiter}` only after all entities and relationships, following all criteria, have been completely extracted and outputted.

---Examples---
{examples}
"""

PROMPTS["entity_extraction_user_prompt"] = """---Task---
Extract entities and relationships from the input text in Data to be Processed below.

---Instructions---
1.  **Strict Adherence to Format:** Strictly adhere to all format requirements for entity and relationship lists, including output order, field delimiters, and proper noun handling, as specified in the system prompt.
2.  **Output Content Only:** Output *only* the extracted list of entities and relationships. Do not include any introductory or concluding remarks, explanations, or additional text before or after the list.
3.  **Completion Signal:** Output `{completion_delimiter}` as the final line after all relevant entities and relationships have been extracted and presented.
4.  **Output Language:** Ensure the output language is {language}. Proper nouns (e.g., personal names, place names, organization names) must be kept in their original language and not translated.

---Data to be Processed---
<Entity_types>
[{entity_types}]

<Input Text>
```
{input_text}
```

<Output>
"""

PROMPTS["entity_continue_extraction_user_prompt"] = """---Task---
Based on the last extraction task, identify and extract any **missed or incorrectly formatted** entities and relationships from the input text.

---Instructions---
1.  **Strict Adherence to System Format:** Strictly adhere to all format requirements for entity and relationship lists, including output order, field delimiters, and proper noun handling, as specified in the system instructions.
2.  **Focus on Corrections/Additions:**
    *   **Do NOT** re-output entities and relationships that were **correctly and fully** extracted in the last task.
    *   If an entity or relationship was **missed** in the last task, extract and output it now according to the system format.
    *   If an entity or relationship was **truncated, had missing fields, or was otherwise incorrectly formatted** in the last task, re-output the *corrected and complete* version in the specified format.
3.  **Output Format - Entities:** Output a total of 4 fields for each entity, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `entity`.
4.  **Output Format - Relationships:** Output a total of 5 fields for each relationship, delimited by `{tuple_delimiter}`, on a single line. The first field *must* be the literal string `relation`.
5.  **Output Content Only:** Output *only* the extracted list of entities and relationships. Do not include any introductory or concluding remarks, explanations, or additional text before or after the list.
6.  **Completion Signal:** Output `{completion_delimiter}` as the final line after all relevant missing or corrected entities and relationships have been extracted and presented.
7.  **Output Language:** Ensure the output language is {language}. Proper nouns (e.g., personal names, place names, organization names) must be kept in their original language and not translated.

<Output>
"""

PROMPTS["entity_extraction_examples"] = [
    """<Entity_types>
["Person","Creature","Organization","Location","Event","Concept","Method","Content","Data","Artifact","NaturalObject"]

<Input Text>
```
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. "If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us."

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
```

<Output>
entity{tuple_delimiter}Alex{tuple_delimiter}person{tuple_delimiter}Alex is a character who experiences frustration and is observant of the dynamics among other characters.
entity{tuple_delimiter}Taylor{tuple_delimiter}person{tuple_delimiter}Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective.
entity{tuple_delimiter}Jordan{tuple_delimiter}person{tuple_delimiter}Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device.
entity{tuple_delimiter}Cruz{tuple_delimiter}person{tuple_delimiter}Cruz is associated with a vision of control and order, influencing the dynamics among other characters.
entity{tuple_delimiter}The Device{tuple_delimiter}equipment{tuple_delimiter}The Device is central to the story, with potential game-changing implications, and is revered by Taylor.
relation{tuple_delimiter}Alex{tuple_delimiter}Taylor{tuple_delimiter}power dynamics, observation{tuple_delimiter}Alex observes Taylor's authoritarian behavior and notes changes in Taylor's attitude toward the device.
relation{tuple_delimiter}Alex{tuple_delimiter}Jordan{tuple_delimiter}shared goals, rebellion{tuple_delimiter}Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.)
relation{tuple_delimiter}Taylor{tuple_delimiter}Jordan{tuple_delimiter}conflict resolution, mutual respect{tuple_delimiter}Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce.
relation{tuple_delimiter}Jordan{tuple_delimiter}Cruz{tuple_delimiter}ideological conflict, rebellion{tuple_delimiter}Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order.
relation{tuple_delimiter}Taylor{tuple_delimiter}The Device{tuple_delimiter}reverence, technological significance{tuple_delimiter}Taylor shows reverence towards the device, indicating its importance and potential impact.
{completion_delimiter}

""",
    """<Entity_types>
["Person","Creature","Organization","Location","Event","Concept","Method","Content","Data","Artifact","NaturalObject"]

<Input Text>
```
Stock markets faced a sharp downturn today as tech giants saw significant declines, with the global tech index dropping by 3.4% in midday trading. Analysts attribute the selloff to investor concerns over rising interest rates and regulatory uncertainty.

Among the hardest hit, nexon technologies saw its stock plummet by 7.8% after reporting lower-than-expected quarterly earnings. In contrast, Omega Energy posted a modest 2.1% gain, driven by rising oil prices.

Meanwhile, commodity markets reflected a mixed sentiment. Gold futures rose by 1.5%, reaching $2,080 per ounce, as investors sought safe-haven assets. Crude oil prices continued their rally, climbing to $87.60 per barrel, supported by supply constraints and strong demand.

Financial experts are closely watching the Federal Reserve's next move, as speculation grows over potential rate hikes. The upcoming policy announcement is expected to influence investor confidence and overall market stability.
```

<Output>
entity{tuple_delimiter}Global Tech Index{tuple_delimiter}category{tuple_delimiter}The Global Tech Index tracks the performance of major technology stocks and experienced a 3.4% decline today.
entity{tuple_delimiter}Nexon Technologies{tuple_delimiter}organization{tuple_delimiter}Nexon Technologies is a tech company that saw its stock decline by 7.8% after disappointing earnings.
entity{tuple_delimiter}Omega Energy{tuple_delimiter}organization{tuple_delimiter}Omega Energy is an energy company that gained 2.1% in stock value due to rising oil prices.
entity{tuple_delimiter}Gold Futures{tuple_delimiter}product{tuple_delimiter}Gold futures rose by 1.5%, indicating increased investor interest in safe-haven assets.
entity{tuple_delimiter}Crude Oil{tuple_delimiter}product{tuple_delimiter}Crude oil prices rose to $87.60 per barrel due to supply constraints and strong demand.
entity{tuple_delimiter}Market Selloff{tuple_delimiter}category{tuple_delimiter}Market selloff refers to the significant decline in stock values due to investor concerns over interest rates and regulations.
entity{tuple_delimiter}Federal Reserve Policy Announcement{tuple_delimiter}category{tuple_delimiter}The Federal Reserve's upcoming policy announcement is expected to impact investor confidence and market stability.
entity{tuple_delimiter}3.4% Decline{tuple_delimiter}category{tuple_delimiter}The Global Tech Index experienced a 3.4% decline in midday trading.
relation{tuple_delimiter}Global Tech Index{tuple_delimiter}Market Selloff{tuple_delimiter}market performance, investor sentiment{tuple_delimiter}The decline in the Global Tech Index is part of the broader market selloff driven by investor concerns.
relation{tuple_delimiter}Nexon Technologies{tuple_delimiter}Global Tech Index{tuple_delimiter}company impact, index movement{tuple_delimiter}Nexon Technologies' stock decline contributed to the overall drop in the Global Tech Index.
relation{tuple_delimiter}Gold Futures{tuple_delimiter}Market Selloff{tuple_delimiter}market reaction, safe-haven investment{tuple_delimiter}Gold prices rose as investors sought safe-haven assets during the market selloff.
relation{tuple_delimiter}Federal Reserve Policy Announcement{tuple_delimiter}Market Selloff{tuple_delimiter}interest rate impact, financial regulation{tuple_delimiter}Speculation over Federal Reserve policy changes contributed to market volatility and investor selloff.
{completion_delimiter}

""",
    """<Entity_types>
["Person","Creature","Organization","Location","Event","Concept","Method","Content","Data","Artifact","NaturalObject"]

<Input Text>
```
At the World Athletics Championship in Tokyo, Noah Carter broke the 100m sprint record using cutting-edge carbon-fiber spikes.
```

<Output>
entity{tuple_delimiter}World Athletics Championship{tuple_delimiter}event{tuple_delimiter}The World Athletics Championship is a global sports competition featuring top athletes in track and field.
entity{tuple_delimiter}Tokyo{tuple_delimiter}location{tuple_delimiter}Tokyo is the host city of the World Athletics Championship.
entity{tuple_delimiter}Noah Carter{tuple_delimiter}person{tuple_delimiter}Noah Carter is a sprinter who set a new record in the 100m sprint at the World Athletics Championship.
entity{tuple_delimiter}100m Sprint Record{tuple_delimiter}category{tuple_delimiter}The 100m sprint record is a benchmark in athletics, recently broken by Noah Carter.
entity{tuple_delimiter}Carbon-Fiber Spikes{tuple_delimiter}equipment{tuple_delimiter}Carbon-fiber spikes are advanced sprinting shoes that provide enhanced speed and traction.
entity{tuple_delimiter}World Athletics Federation{tuple_delimiter}organization{tuple_delimiter}The World Athletics Federation is the governing body overseeing the World Athletics Championship and record validations.
relation{tuple_delimiter}World Athletics Championship{tuple_delimiter}Tokyo{tuple_delimiter}event location, international competition{tuple_delimiter}The World Athletics Championship is being hosted in Tokyo.
relation{tuple_delimiter}Noah Carter{tuple_delimiter}100m Sprint Record{tuple_delimiter}athlete achievement, record-breaking{tuple_delimiter}Noah Carter set a new 100m sprint record at the championship.
relation{tuple_delimiter}Noah Carter{tuple_delimiter}Carbon-Fiber Spikes{tuple_delimiter}athletic equipment, performance boost{tuple_delimiter}Noah Carter used carbon-fiber spikes to enhance performance during the race.
relation{tuple_delimiter}Noah Carter{tuple_delimiter}World Athletics Championship{tuple_delimiter}athlete participation, competition{tuple_delimiter}Noah Carter is competing at the World Athletics Championship.
{completion_delimiter}

""",
]

PROMPTS["summarize_entity_descriptions"] = """---Role---
You are a Knowledge Graph Specialist, proficient in data curation and synthesis.

---Task---
Your task is to synthesize a list of descriptions of a given entity or relation into a single, comprehensive, and cohesive summary.

---Instructions---
1. Input Format: The description list is provided in JSON format. Each JSON object (representing a single description) appears on a new line within the `Description List` section.
2. Output Format: The merged description will be returned as plain text, presented in multiple paragraphs, without any additional formatting or extraneous comments before or after the summary.
3. Comprehensiveness: The summary must integrate all key information from *every* provided description. Do not omit any important facts or details.
4. Context: Ensure the summary is written from an objective, third-person perspective; explicitly mention the name of the entity or relation for full clarity and context.
5. Context & Objectivity:
  - Write the summary from an objective, third-person perspective.
  - Explicitly mention the full name of the entity or relation at the beginning of the summary to ensure immediate clarity and context.
6. Conflict Handling:
  - In cases of conflicting or inconsistent descriptions, first determine if these conflicts arise from multiple, distinct entities or relationships that share the same name.
  - If distinct entities/relations are identified, summarize each one *separately* within the overall output.
  - If conflicts within a single entity/relation (e.g., historical discrepancies) exist, attempt to reconcile them or present both viewpoints with noted uncertainty.
7. Length Constraint:The summary's total length must not exceed {summary_length} tokens, while still maintaining depth and completeness.
8. Language: The entire output must be written in {language}. Proper nouns (e.g., personal names, place names, organization names) may in their original language if proper translation is not available.
  - The entire output must be written in {language}.
  - Proper nouns (e.g., personal names, place names, organization names) should be retained in their original language if a proper, widely accepted translation is not available or would cause ambiguity.

---Input---
{description_type} Name: {description_name}

Description List:

```
{description_list}
```

---Output---
"""

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

PROMPTS["rag_response"] = """---Role---

You are an expert AI assistant specializing in synthesizing information from a provided knowledge base. Your primary function is to answer user queries accurately by ONLY using the information within the provided **Context**.

---Goal---

Generate a comprehensive, well-structured answer to the user query.
The answer must integrate relevant facts from the Knowledge Graph and Document Chunks found in the **Context**.
Consider the conversation history if provided to maintain conversational flow and avoid repeating information.

---Instructions---

1. Step-by-Step Instruction:
  - Carefully determine the user's query intent in the context of the conversation history to fully understand the user's information need.
  - Scrutinize both `Knowledge Graph Data` and `Document Chunks` in the **Context**. Identify and extract all pieces of information that are directly relevant to answering the user query.
  - Weave the extracted facts into a coherent and logical response. Your own knowledge must ONLY be used to formulate fluent sentences and connect ideas, NOT to introduce any external information.
  - Track the reference_id of the document chunk which directly support the facts presented in the response. Correlate reference_id with the entries in the `Reference Document List` to generate the appropriate citations.
  - Generate a references section at the end of the response. Each reference document must directly support the facts presented in the response.
  - Do not generate anything after the reference section.

2. Content & Grounding:
  - Strictly adhere to the provided context from the **Context**; DO NOT invent, assume, or infer any information not explicitly stated.
  - If the answer cannot be found in the **Context**, state that you do not have enough information to answer. Do not attempt to guess.

3. Formatting & Language:
  - The response MUST be in the same language as the user query.
  - The response MUST utilize Markdown formatting for enhanced clarity and structure (e.g., headings, bold text, bullet points).
  - The response should be presented in {response_type}.

4. References Section Format:
  - The References section should be under heading: `### References`
  - Reference list entries should adhere to the format: `* [n] Document Title`. Do not include a caret (`^`) after opening square bracket (`[`).
  - The Document Title in the citation must retain its original language.
  - Output each citation on an individual line
  - Provide maximum of 5 most relevant citations.
  - Do not generate footnotes section or any comment, summary, or explanation after the references.

5. Reference Section Example:
```
### References

- [1] Document Title One
- [2] Document Title Two
- [3] Document Title Three
```

6. Additional Instructions: {user_prompt}


---Context---

{context_data}
"""

PROMPTS["naive_rag_response"] = """---Role---

You are an expert AI assistant specializing in synthesizing information from a provided knowledge base. Your primary function is to answer user queries accurately by ONLY using the information within the provided **Context**.

---Goal---

Generate a comprehensive, well-structured answer to the user query.
The answer must integrate relevant facts from the Document Chunks found in the **Context**.
Consider the conversation history if provided to maintain conversational flow and avoid repeating information.

---Instructions---

1. Step-by-Step Instruction:
  - Carefully determine the user's query intent in the context of the conversation history to fully understand the user's information need.
  - Scrutinize `Document Chunks` in the **Context**. Identify and extract all pieces of information that are directly relevant to answering the user query.
  - Weave the extracted facts into a coherent and logical response. Your own knowledge must ONLY be used to formulate fluent sentences and connect ideas, NOT to introduce any external information.
  - Track the reference_id of the document chunk which directly support the facts presented in the response. Correlate reference_id with the entries in the `Reference Document List` to generate the appropriate citations.
  - Generate a **References** section at the end of the response. Each reference document must directly support the facts presented in the response.
  - Do not generate anything after the reference section.

2. Content & Grounding:
  - Strictly adhere to the provided context from the **Context**; DO NOT invent, assume, or infer any information not explicitly stated.
  - If the answer cannot be found in the **Context**, state that you do not have enough information to answer. Do not attempt to guess.

3. Formatting & Language:
  - The response MUST be in the same language as the user query.
  - The response MUST utilize Markdown formatting for enhanced clarity and structure (e.g., headings, bold text, bullet points).
  - The response should be presented in {response_type}.

4. References Section Format:
  - The References section should be under heading: `### References`
  - Reference list entries should adhere to the format: `* [n] Document Title`. Do not include a caret (`^`) after opening square bracket (`[`).
  - The Document Title in the citation must retain its original language.
  - Output each citation on an individual line
  - Provide maximum of 5 most relevant citations.
  - Do not generate footnotes section or any comment, summary, or explanation after the references.

5. Reference Section Example:
```
### References

- [1] Document Title One
- [2] Document Title Two
- [3] Document Title Three
```

6. Additional Instructions: {user_prompt}


---Context---

{content_data}
"""

PROMPTS["kg_query_context"] = """
Knowledge Graph Data (Entity):

```json
{entities_str}
```

Knowledge Graph Data (Relationship):

```json
{relations_str}
```

Document Chunks (Each entry has a reference_id refer to the `Reference Document List`):

```json
{text_chunks_str}
```

Reference Document List (Each entry starts with a [reference_id] that corresponds to entries in the Document Chunks):

```
{reference_list_str}
```

"""

PROMPTS["naive_query_context"] = """
Document Chunks (Each entry has a reference_id refer to the `Reference Document List`):

```json
{text_chunks_str}
```

Reference Document List (Each entry starts with a [reference_id] that corresponds to entries in the Document Chunks):

```
{reference_list_str}
```

"""

PROMPTS["keywords_extraction"] = """---Role---
You are an expert keyword extractor, specializing in analyzing user queries for a Retrieval-Augmented Generation (RAG) system. Your purpose is to identify both high-level and low-level keywords in the user's query that will be used for effective document retrieval.

---Goal---
Given a user query, your task is to extract two distinct types of keywords:
1. **high_level_keywords**: for overarching concepts or themes, capturing user's core intent, the subject area, or the type of question being asked.
2. **low_level_keywords**: for specific entities or details, identifying the specific entities, proper nouns, technical jargon, product names, or concrete items.

---Instructions & Constraints---
1. **Output Format**: Your output MUST be a valid JSON object and nothing else. Do not include any explanatory text, markdown code fences (like ```json), or any other text before or after the JSON. It will be parsed directly by a JSON parser.
2. **Source of Truth**: All keywords must be explicitly derived from the user query, with both high-level and low-level keyword categories are required to contain content.
3. **Concise & Meaningful**: Keywords should be concise words or meaningful phrases. Prioritize multi-word phrases when they represent a single concept. For example, from "latest financial report of Apple Inc.", you should extract "latest financial report" and "Apple Inc." rather than "latest", "financial", "report", and "Apple".
4. **Handle Edge Cases**: For queries that are too simple, vague, or nonsensical (e.g., "hello", "ok", "asdfghjkl"), you must return a JSON object with empty lists for both keyword types.
5. **Language**: All extracted keywords MUST be in {language}. Proper nouns (e.g., personal names, place names, organization names) should be kept in their original language.

---Examples---
{examples}

---Real Data---
User Query: {query}

---Output---
Output:"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"

Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}

""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"

Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}

""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"

Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}

""",
]

# ============================================================================
# PROMPTS_ID — Indonesian translations
# Delimiters reuse the same values as English prompts
# ============================================================================

PROMPTS_ID["DEFAULT_TUPLE_DELIMITER"] = PROMPTS["DEFAULT_TUPLE_DELIMITER"]
PROMPTS_ID["DEFAULT_COMPLETION_DELIMITER"] = PROMPTS["DEFAULT_COMPLETION_DELIMITER"]

PROMPTS_ID["entity_extraction_system_prompt"] = """---Peran---
Anda adalah Spesialis Knowledge Graph yang bertanggung jawab mengekstraksi entitas dan relasi dari teks masukan.

---Instruksi---
1.  **Ekstraksi & Output Entitas:**
    *   **Identifikasi:** Identifikasi entitas yang jelas dan bermakna dalam teks masukan.
    *   **Detail Entitas:** Untuk setiap entitas yang teridentifikasi, ekstrak informasi berikut:
        *   `entity_name`: Nama entitas. Jika nama entitas tidak peka huruf besar-kecil, gunakan huruf kapital di awal setiap kata penting (title case). Pastikan **penamaan konsisten** di seluruh proses ekstraksi.
        *   `entity_type`: Kategorikan entitas menggunakan salah satu tipe berikut: `{entity_types}`. Jika tidak ada tipe yang sesuai, jangan menambah tipe baru dan klasifikasikan sebagai `Other`.
        *   `entity_description`: Berikan deskripsi singkat namun komprehensif tentang atribut dan aktivitas entitas, berdasarkan *hanya* informasi yang ada dalam teks masukan.
    *   **Format Output - Entitas:** Keluarkan total 4 field untuk setiap entitas, dipisahkan oleh `{tuple_delimiter}`, dalam satu baris. Field pertama *harus* berupa string literal `entity`.
        *   Format: `entity{tuple_delimiter}entity_name{tuple_delimiter}entity_type{tuple_delimiter}entity_description`

2.  **Ekstraksi & Output Relasi:**
    *   **Identifikasi:** Identifikasi relasi langsung, yang dinyatakan secara jelas, dan bermakna antara entitas yang telah diekstraksi sebelumnya.
    *   **Dekomposisi Relasi N-ary:** Jika satu pernyataan menggambarkan relasi yang melibatkan lebih dari dua entitas (relasi N-ary), dekomposisi menjadi beberapa pasangan relasi biner (dua entitas) untuk deskripsi terpisah.
        *   **Contoh:** Untuk "Jokowi, Prabowo, dan Megawati menghadiri KTT G20," ekstrak relasi biner seperti "Jokowi menghadiri KTT G20," "Prabowo menghadiri KTT G20," dan "Megawati menghadiri KTT G20."
    *   **Detail Relasi:** Untuk setiap relasi biner, ekstrak field berikut:
        *   `source_entity`: Nama entitas sumber. Pastikan **penamaan konsisten** dengan ekstraksi entitas. Gunakan huruf kapital di awal setiap kata penting (title case) jika nama tidak peka huruf besar-kecil.
        *   `target_entity`: Nama entitas target. Pastikan **penamaan konsisten** dengan ekstraksi entitas. Gunakan huruf kapital di awal setiap kata penting (title case) jika nama tidak peka huruf besar-kecil.
        *   `relationship_keywords`: Satu atau lebih kata kunci tingkat tinggi yang merangkum sifat, konsep, atau tema keseluruhan dari relasi. Beberapa kata kunci dalam field ini harus dipisahkan oleh koma `,`. **JANGAN gunakan `{tuple_delimiter}` untuk memisahkan beberapa kata kunci dalam field ini.**
        *   `relationship_description`: Penjelasan singkat tentang sifat relasi antara entitas sumber dan target, memberikan alasan yang jelas untuk hubungan mereka.
    *   **Format Output - Relasi:** Keluarkan total 5 field untuk setiap relasi, dipisahkan oleh `{tuple_delimiter}`, dalam satu baris. Field pertama *harus* berupa string literal `relation`.
        *   Format: `relation{tuple_delimiter}source_entity{tuple_delimiter}target_entity{tuple_delimiter}relationship_keywords{tuple_delimiter}relationship_description`

3.  **Protokol Penggunaan Delimiter:**
    *   `{tuple_delimiter}` adalah penanda atomik lengkap dan **tidak boleh diisi dengan konten**. Berfungsi secara ketat sebagai pemisah field.
    *   **Contoh Salah:** `entity{tuple_delimiter}Jakarta<|lokasi|>Jakarta adalah ibu kota Indonesia.`
    *   **Contoh Benar:** `entity{tuple_delimiter}Jakarta{tuple_delimiter}lokasi{tuple_delimiter}Jakarta adalah ibu kota Indonesia.`

4.  **Arah & Duplikasi Relasi:**
    *   Perlakukan semua relasi sebagai **tidak berarah** kecuali dinyatakan sebaliknya secara eksplisit. Menukar entitas sumber dan target untuk relasi tidak berarah bukan merupakan relasi baru.
    *   Hindari mengeluarkan relasi duplikat.

5.  **Urutan Output & Prioritas:**
    *   Keluarkan semua entitas yang diekstraksi terlebih dahulu, diikuti oleh semua relasi yang diekstraksi.
    *   Dalam daftar relasi, prioritaskan dan keluarkan relasi yang **paling signifikan** terhadap makna inti teks masukan terlebih dahulu.

6.  **Konteks & Objektivitas:**
    *   Pastikan semua nama entitas dan deskripsi ditulis dalam **orang ketiga**.
    *   Sebutkan subjek atau objek secara eksplisit; **hindari penggunaan kata ganti** seperti `artikel ini`, `makalah ini`, `perusahaan kami`, `saya`, `Anda`, dan `dia`.

7.  **Bahasa & Nama Diri:**
    *   Seluruh output (nama entitas, kata kunci, dan deskripsi) harus ditulis dalam `{language}`.
    *   Nama diri (misalnya, nama orang, nama tempat, nama organisasi) harus dipertahankan dalam bahasa aslinya jika terjemahan yang tepat dan diterima secara luas tidak tersedia atau akan menimbulkan ambiguitas.

8.  **Sinyal Penyelesaian:** Keluarkan string literal `{completion_delimiter}` hanya setelah semua entitas dan relasi, mengikuti semua kriteria, telah sepenuhnya diekstraksi dan dikeluarkan.

---Contoh---
{examples}
"""

PROMPTS_ID["entity_extraction_user_prompt"] = """---Tugas---
Ekstrak entitas dan relasi dari teks masukan pada bagian Data yang Akan Diproses di bawah ini.

---Instruksi---
1.  **Kepatuhan Ketat terhadap Format:** Patuhi secara ketat semua persyaratan format untuk daftar entitas dan relasi, termasuk urutan output, pemisah field, dan penanganan nama diri, sebagaimana ditentukan dalam system prompt.
2.  **Hanya Output Konten:** Keluarkan *hanya* daftar entitas dan relasi yang diekstraksi. Jangan sertakan komentar pembuka atau penutup, penjelasan, atau teks tambahan sebelum atau sesudah daftar.
3.  **Sinyal Penyelesaian:** Keluarkan `{completion_delimiter}` sebagai baris terakhir setelah semua entitas dan relasi yang relevan telah diekstraksi dan disajikan.
4.  **Bahasa Output:** Pastikan bahasa output adalah {language}. Nama diri (misalnya, nama orang, nama tempat, nama organisasi) harus dipertahankan dalam bahasa aslinya dan tidak diterjemahkan.

---Data yang Akan Diproses---
<Entity_types>
[{entity_types}]

<Input Text>
```
{input_text}
```

<Output>
"""

PROMPTS_ID["entity_continue_extraction_user_prompt"] = """---Tugas---
Berdasarkan tugas ekstraksi terakhir, identifikasi dan ekstrak entitas dan relasi yang **terlewat atau salah format** dari teks masukan.

---Instruksi---
1.  **Kepatuhan Ketat terhadap Format Sistem:** Patuhi secara ketat semua persyaratan format untuk daftar entitas dan relasi, termasuk urutan output, pemisah field, dan penanganan nama diri, sebagaimana ditentukan dalam instruksi sistem.
2.  **Fokus pada Koreksi/Penambahan:**
    *   **JANGAN** mengeluarkan kembali entitas dan relasi yang telah diekstraksi **dengan benar dan lengkap** dalam tugas terakhir.
    *   Jika entitas atau relasi **terlewat** dalam tugas terakhir, ekstrak dan keluarkan sekarang sesuai format sistem.
    *   Jika entitas atau relasi **terpotong, memiliki field yang hilang, atau salah format** dalam tugas terakhir, keluarkan kembali versi yang *diperbaiki dan lengkap* dalam format yang ditentukan.
3.  **Format Output - Entitas:** Keluarkan total 4 field untuk setiap entitas, dipisahkan oleh `{tuple_delimiter}`, dalam satu baris. Field pertama *harus* berupa string literal `entity`.
4.  **Format Output - Relasi:** Keluarkan total 5 field untuk setiap relasi, dipisahkan oleh `{tuple_delimiter}`, dalam satu baris. Field pertama *harus* berupa string literal `relation`.
5.  **Hanya Output Konten:** Keluarkan *hanya* daftar entitas dan relasi yang diekstraksi. Jangan sertakan komentar pembuka atau penutup, penjelasan, atau teks tambahan sebelum atau sesudah daftar.
6.  **Sinyal Penyelesaian:** Keluarkan `{completion_delimiter}` sebagai baris terakhir setelah semua entitas dan relasi yang terlewat atau dikoreksi telah diekstraksi dan disajikan.
7.  **Bahasa Output:** Pastikan bahasa output adalah {language}. Nama diri (misalnya, nama orang, nama tempat, nama organisasi) harus dipertahankan dalam bahasa aslinya dan tidak diterjemahkan.

<Output>
"""

PROMPTS_ID["entity_extraction_examples"] = [
    """<Entity_types>
["Orang","Organisasi","Lokasi","Peristiwa","Klaim","Sumber_Bukti","Pernyataan","Waktu","Kuantitas","Regulasi","Media"]

<Input Text>
```
Kementerian Kesehatan membantah klaim yang beredar di media sosial bahwa vaksin COVID-19 Sinovac mengandung microchip. Juru bicara Kemenkes, dr. Siti Nadia Tarmizi, menegaskan pada konferensi pers tanggal 15 Januari 2024 bahwa vaksin telah melalui uji klinis ketat oleh BPOM dan WHO. Klaim tersebut pertama kali muncul dari akun Facebook bernama "Berita Rakyat" yang memiliki lebih dari 50.000 pengikut.
```

<Output>
entity{tuple_delimiter}Kementerian Kesehatan{tuple_delimiter}organisasi{tuple_delimiter}Kementerian Kesehatan adalah lembaga pemerintah Indonesia yang bertanggung jawab atas kebijakan kesehatan dan membantah klaim misinformasi tentang vaksin COVID-19.
entity{tuple_delimiter}Vaksin COVID-19 Sinovac{tuple_delimiter}klaim{tuple_delimiter}Vaksin COVID-19 Sinovac menjadi subjek klaim palsu yang menyatakan bahwa vaksin tersebut mengandung microchip.
entity{tuple_delimiter}Dr. Siti Nadia Tarmizi{tuple_delimiter}orang{tuple_delimiter}Dr. Siti Nadia Tarmizi adalah juru bicara Kementerian Kesehatan yang menegaskan keamanan vaksin pada konferensi pers.
entity{tuple_delimiter}BPOM{tuple_delimiter}organisasi{tuple_delimiter}BPOM (Badan Pengawas Obat dan Makanan) adalah lembaga yang melakukan uji klinis terhadap vaksin COVID-19.
entity{tuple_delimiter}WHO{tuple_delimiter}organisasi{tuple_delimiter}WHO (World Health Organization) adalah organisasi kesehatan dunia yang turut menguji vaksin COVID-19.
entity{tuple_delimiter}Berita Rakyat{tuple_delimiter}media{tuple_delimiter}Berita Rakyat adalah akun Facebook dengan lebih dari 50.000 pengikut yang menjadi sumber awal klaim palsu tentang vaksin.
entity{tuple_delimiter}15 Januari 2024{tuple_delimiter}waktu{tuple_delimiter}15 Januari 2024 adalah tanggal konferensi pers Kementerian Kesehatan yang membantah klaim vaksin microchip.
relation{tuple_delimiter}Kementerian Kesehatan{tuple_delimiter}Vaksin COVID-19 Sinovac{tuple_delimiter}bantahan klaim, verifikasi fakta{tuple_delimiter}Kementerian Kesehatan secara resmi membantah klaim palsu bahwa vaksin COVID-19 Sinovac mengandung microchip.
relation{tuple_delimiter}Dr. Siti Nadia Tarmizi{tuple_delimiter}Kementerian Kesehatan{tuple_delimiter}juru bicara, representasi resmi{tuple_delimiter}Dr. Siti Nadia Tarmizi menyampaikan pernyataan resmi sebagai juru bicara Kementerian Kesehatan.
relation{tuple_delimiter}BPOM{tuple_delimiter}Vaksin COVID-19 Sinovac{tuple_delimiter}uji klinis, sertifikasi{tuple_delimiter}BPOM melakukan uji klinis ketat terhadap vaksin COVID-19 Sinovac sebelum disetujui penggunaannya.
relation{tuple_delimiter}Berita Rakyat{tuple_delimiter}Vaksin COVID-19 Sinovac{tuple_delimiter}sumber misinformasi, klaim palsu{tuple_delimiter}Akun Facebook Berita Rakyat menjadi sumber awal penyebaran klaim palsu tentang vaksin mengandung microchip.
{completion_delimiter}

""",
    """<Entity_types>
["Orang","Organisasi","Lokasi","Peristiwa","Klaim","Sumber_Bukti","Pernyataan","Waktu","Kuantitas","Regulasi","Media"]

<Input Text>
```
Beredar narasi di WhatsApp bahwa Presiden Joko Widodo menandatangani Perpres tentang penghapusan mata pelajaran agama di sekolah negeri. Setelah ditelusuri oleh tim Cek Fakta Tempo, narasi tersebut dinyatakan hoaks. Perpres yang dimaksud sebenarnya adalah Perpres Nomor 87 Tahun 2017 tentang Penguatan Pendidikan Karakter yang justru memperkuat pendidikan agama dan budi pekerti.
```

<Output>
entity{tuple_delimiter}Joko Widodo{tuple_delimiter}orang{tuple_delimiter}Joko Widodo adalah Presiden Republik Indonesia yang namanya dikaitkan dengan klaim palsu tentang penghapusan mata pelajaran agama.
entity{tuple_delimiter}Perpres Penghapusan Agama{tuple_delimiter}klaim{tuple_delimiter}Klaim palsu yang menyatakan bahwa Presiden menandatangani Perpres tentang penghapusan mata pelajaran agama di sekolah negeri.
entity{tuple_delimiter}Cek Fakta Tempo{tuple_delimiter}sumber_bukti{tuple_delimiter}Tim Cek Fakta Tempo adalah unit verifikasi fakta dari media Tempo yang meneliti dan membantah narasi hoaks tersebut.
entity{tuple_delimiter}Perpres Nomor 87 Tahun 2017{tuple_delimiter}regulasi{tuple_delimiter}Perpres Nomor 87 Tahun 2017 tentang Penguatan Pendidikan Karakter adalah regulasi yang justru memperkuat pendidikan agama dan budi pekerti.
entity{tuple_delimiter}WhatsApp{tuple_delimiter}media{tuple_delimiter}WhatsApp adalah platform pesan instan tempat narasi hoaks tentang penghapusan mata pelajaran agama beredar.
relation{tuple_delimiter}Cek Fakta Tempo{tuple_delimiter}Perpres Penghapusan Agama{tuple_delimiter}verifikasi fakta, debunk hoaks{tuple_delimiter}Tim Cek Fakta Tempo menelusuri dan menyatakan bahwa narasi tentang Perpres penghapusan agama adalah hoaks.
relation{tuple_delimiter}Perpres Nomor 87 Tahun 2017{tuple_delimiter}Perpres Penghapusan Agama{tuple_delimiter}klarifikasi, konteks asli{tuple_delimiter}Perpres Nomor 87 Tahun 2017 adalah regulasi yang sebenarnya dirujuk dalam klaim palsu, dan justru memperkuat pendidikan agama.
relation{tuple_delimiter}Joko Widodo{tuple_delimiter}Perpres Penghapusan Agama{tuple_delimiter}atribusi palsu, misinformasi{tuple_delimiter}Nama Joko Widodo secara tidak benar dikaitkan dengan penandatanganan Perpres penghapusan mata pelajaran agama.
{completion_delimiter}

""",
    """<Entity_types>
["Orang","Organisasi","Lokasi","Peristiwa","Klaim","Sumber_Bukti","Pernyataan","Waktu","Kuantitas","Regulasi","Media"]

<Input Text>
```
Badan Nasional Penanggulangan Bencana (BNPB) melaporkan bahwa gempa bumi berkekuatan 6,2 SR mengguncang Sulawesi Barat pada 15 Januari 2021, menyebabkan 105 korban jiwa dan kerusakan lebih dari 27.000 rumah di Kabupaten Mamuju dan Majene.
```

<Output>
entity{tuple_delimiter}BNPB{tuple_delimiter}organisasi{tuple_delimiter}Badan Nasional Penanggulangan Bencana (BNPB) adalah lembaga pemerintah yang melaporkan data dampak gempa bumi di Sulawesi Barat.
entity{tuple_delimiter}Gempa Sulawesi Barat 2021{tuple_delimiter}peristiwa{tuple_delimiter}Gempa bumi berkekuatan 6,2 SR yang mengguncang Sulawesi Barat pada 15 Januari 2021, menyebabkan 105 korban jiwa.
entity{tuple_delimiter}Sulawesi Barat{tuple_delimiter}lokasi{tuple_delimiter}Sulawesi Barat adalah provinsi di Indonesia yang terdampak gempa bumi pada Januari 2021.
entity{tuple_delimiter}Kabupaten Mamuju{tuple_delimiter}lokasi{tuple_delimiter}Kabupaten Mamuju adalah salah satu wilayah di Sulawesi Barat yang mengalami kerusakan akibat gempa.
entity{tuple_delimiter}Kabupaten Majene{tuple_delimiter}lokasi{tuple_delimiter}Kabupaten Majene adalah salah satu wilayah di Sulawesi Barat yang mengalami kerusakan akibat gempa.
entity{tuple_delimiter}15 Januari 2021{tuple_delimiter}waktu{tuple_delimiter}15 Januari 2021 adalah tanggal terjadinya gempa bumi di Sulawesi Barat.
entity{tuple_delimiter}105 Korban Jiwa{tuple_delimiter}kuantitas{tuple_delimiter}Jumlah korban jiwa akibat gempa bumi Sulawesi Barat adalah 105 orang.
entity{tuple_delimiter}27.000 Rumah Rusak{tuple_delimiter}kuantitas{tuple_delimiter}Lebih dari 27.000 rumah mengalami kerusakan akibat gempa bumi Sulawesi Barat.
relation{tuple_delimiter}BNPB{tuple_delimiter}Gempa Sulawesi Barat 2021{tuple_delimiter}pelaporan resmi, data bencana{tuple_delimiter}BNPB melaporkan data dampak dan korban gempa bumi Sulawesi Barat 2021.
relation{tuple_delimiter}Gempa Sulawesi Barat 2021{tuple_delimiter}Sulawesi Barat{tuple_delimiter}lokasi bencana, dampak gempa{tuple_delimiter}Gempa bumi berkekuatan 6,2 SR mengguncang wilayah Sulawesi Barat.
relation{tuple_delimiter}Gempa Sulawesi Barat 2021{tuple_delimiter}Kabupaten Mamuju{tuple_delimiter}kerusakan infrastruktur, dampak lokal{tuple_delimiter}Kabupaten Mamuju mengalami kerusakan signifikan akibat gempa.
relation{tuple_delimiter}Gempa Sulawesi Barat 2021{tuple_delimiter}Kabupaten Majene{tuple_delimiter}kerusakan infrastruktur, dampak lokal{tuple_delimiter}Kabupaten Majene mengalami kerusakan signifikan akibat gempa.
{completion_delimiter}

""",
]

PROMPTS_ID["summarize_entity_descriptions"] = """---Peran---
Anda adalah Spesialis Knowledge Graph, ahli dalam kurasi dan sintesis data.

---Tugas---
Tugas Anda adalah mensintesis daftar deskripsi dari suatu entitas atau relasi menjadi satu ringkasan yang komprehensif dan kohesif.

---Instruksi---
1. Format Masukan: Daftar deskripsi disediakan dalam format JSON. Setiap objek JSON (mewakili satu deskripsi) muncul pada baris baru dalam bagian `Description List`.
2. Format Output: Deskripsi yang digabung akan dikembalikan sebagai teks biasa, disajikan dalam beberapa paragraf, tanpa format tambahan atau komentar berlebihan sebelum atau sesudah ringkasan.
3. Kelengkapan: Ringkasan harus mengintegrasikan semua informasi kunci dari *setiap* deskripsi yang diberikan. Jangan menghilangkan fakta atau detail penting.
4. Konteks: Pastikan ringkasan ditulis dari perspektif orang ketiga yang objektif; sebutkan nama entitas atau relasi secara eksplisit untuk kejelasan dan konteks penuh.
5. Konteks & Objektivitas:
  - Tulis ringkasan dari perspektif orang ketiga yang objektif.
  - Sebutkan nama lengkap entitas atau relasi di awal ringkasan untuk memastikan kejelasan dan konteks langsung.
6. Penanganan Konflik:
  - Dalam kasus deskripsi yang bertentangan atau tidak konsisten, pertama tentukan apakah konflik ini muncul dari beberapa entitas atau relasi yang berbeda yang memiliki nama sama.
  - Jika entitas/relasi yang berbeda teridentifikasi, ringkas masing-masing *secara terpisah* dalam output keseluruhan.
  - Jika konflik dalam satu entitas/relasi (misalnya, perbedaan historis) ada, coba rekonsiliasi atau sajikan kedua sudut pandang dengan catatan ketidakpastian.
7. Batasan Panjang: Total panjang ringkasan tidak boleh melebihi {summary_length} token, sambil tetap menjaga kedalaman dan kelengkapan.
8. Bahasa:
  - Seluruh output harus ditulis dalam {language}.
  - Nama diri (misalnya, nama orang, nama tempat, nama organisasi) harus dipertahankan dalam bahasa aslinya jika terjemahan yang tepat dan diterima secara luas tidak tersedia atau akan menimbulkan ambiguitas.

---Masukan---
Nama {description_type}: {description_name}

Daftar Deskripsi:

```
{description_list}
```

---Output---
"""

PROMPTS_ID["fail_response"] = (
    "Maaf, saya tidak dapat memberikan jawaban untuk pertanyaan tersebut.[no-context]"
)

PROMPTS_ID["rag_response"] = """---Peran---

Anda adalah asisten AI ahli yang mengkhususkan diri dalam mensintesis informasi dari basis pengetahuan yang disediakan. Fungsi utama Anda adalah menjawab pertanyaan pengguna secara akurat dengan HANYA menggunakan informasi dalam **Konteks** yang disediakan.

---Tujuan---

Hasilkan jawaban yang komprehensif dan terstruktur dengan baik untuk pertanyaan pengguna.
Jawaban harus mengintegrasikan fakta-fakta relevan dari Knowledge Graph dan Potongan Dokumen yang ditemukan dalam **Konteks**.
Pertimbangkan riwayat percakapan jika tersedia untuk menjaga alur percakapan dan menghindari pengulangan informasi.

---Instruksi---

1. Instruksi Langkah demi Langkah:
  - Tentukan dengan cermat maksud pertanyaan pengguna dalam konteks riwayat percakapan untuk memahami kebutuhan informasi pengguna sepenuhnya.
  - Periksa dengan teliti `Knowledge Graph Data` dan `Document Chunks` dalam **Konteks**. Identifikasi dan ekstrak semua informasi yang berkaitan langsung dengan jawaban pertanyaan pengguna.
  - Rangkai fakta-fakta yang diekstrak menjadi respons yang koheren dan logis. Pengetahuan Anda sendiri HANYA boleh digunakan untuk merumuskan kalimat yang lancar dan menghubungkan ide, BUKAN untuk memperkenalkan informasi eksternal.
  - Lacak reference_id dari potongan dokumen yang secara langsung mendukung fakta yang disajikan dalam respons. Korelasikan reference_id dengan entri dalam `Reference Document List` untuk menghasilkan sitasi yang tepat.
  - Hasilkan bagian referensi di akhir respons. Setiap dokumen referensi harus secara langsung mendukung fakta yang disajikan dalam respons.
  - Jangan menghasilkan apa pun setelah bagian referensi.

2. Konten & Landasan:
  - Patuhi secara ketat konteks yang disediakan dari **Konteks**; JANGAN mengarang, mengasumsikan, atau menyimpulkan informasi yang tidak dinyatakan secara eksplisit.
  - Jika jawaban tidak dapat ditemukan dalam **Konteks**, nyatakan bahwa Anda tidak memiliki cukup informasi untuk menjawab. Jangan mencoba menebak.

3. Format & Bahasa:
  - Respons HARUS dalam bahasa yang sama dengan pertanyaan pengguna.
  - Respons HARUS menggunakan format Markdown untuk kejelasan dan struktur yang lebih baik (misalnya, judul, teks tebal, poin-poin).
  - Respons harus disajikan dalam {response_type}.

4. Format Bagian Referensi:
  - Bagian Referensi harus di bawah judul: `### Referensi`
  - Entri daftar referensi harus mengikuti format: `* [n] Judul Dokumen`. Jangan sertakan tanda sisipan (`^`) setelah kurung siku pembuka (`[`).
  - Judul Dokumen dalam sitasi harus mempertahankan bahasa aslinya.
  - Keluarkan setiap sitasi pada baris individual
  - Berikan maksimal 5 sitasi yang paling relevan.
  - Jangan menghasilkan bagian catatan kaki atau komentar, ringkasan, atau penjelasan apa pun setelah referensi.

5. Contoh Bagian Referensi:
```
### Referensi

- [1] Judul Dokumen Satu
- [2] Judul Dokumen Dua
- [3] Judul Dokumen Tiga
```

6. Instruksi Tambahan: {user_prompt}


---Konteks---

{context_data}
"""

PROMPTS_ID["naive_rag_response"] = """---Peran---

Anda adalah asisten AI ahli yang mengkhususkan diri dalam mensintesis informasi dari basis pengetahuan yang disediakan. Fungsi utama Anda adalah menjawab pertanyaan pengguna secara akurat dengan HANYA menggunakan informasi dalam **Konteks** yang disediakan.

---Tujuan---

Hasilkan jawaban yang komprehensif dan terstruktur dengan baik untuk pertanyaan pengguna.
Jawaban harus mengintegrasikan fakta-fakta relevan dari Potongan Dokumen yang ditemukan dalam **Konteks**.
Pertimbangkan riwayat percakapan jika tersedia untuk menjaga alur percakapan dan menghindari pengulangan informasi.

---Instruksi---

1. Instruksi Langkah demi Langkah:
  - Tentukan dengan cermat maksud pertanyaan pengguna dalam konteks riwayat percakapan untuk memahami kebutuhan informasi pengguna sepenuhnya.
  - Periksa dengan teliti `Document Chunks` dalam **Konteks**. Identifikasi dan ekstrak semua informasi yang berkaitan langsung dengan jawaban pertanyaan pengguna.
  - Rangkai fakta-fakta yang diekstrak menjadi respons yang koheren dan logis. Pengetahuan Anda sendiri HANYA boleh digunakan untuk merumuskan kalimat yang lancar dan menghubungkan ide, BUKAN untuk memperkenalkan informasi eksternal.
  - Lacak reference_id dari potongan dokumen yang secara langsung mendukung fakta yang disajikan dalam respons. Korelasikan reference_id dengan entri dalam `Reference Document List` untuk menghasilkan sitasi yang tepat.
  - Hasilkan bagian **Referensi** di akhir respons. Setiap dokumen referensi harus secara langsung mendukung fakta yang disajikan dalam respons.
  - Jangan menghasilkan apa pun setelah bagian referensi.

2. Konten & Landasan:
  - Patuhi secara ketat konteks yang disediakan dari **Konteks**; JANGAN mengarang, mengasumsikan, atau menyimpulkan informasi yang tidak dinyatakan secara eksplisit.
  - Jika jawaban tidak dapat ditemukan dalam **Konteks**, nyatakan bahwa Anda tidak memiliki cukup informasi untuk menjawab. Jangan mencoba menebak.

3. Format & Bahasa:
  - Respons HARUS dalam bahasa yang sama dengan pertanyaan pengguna.
  - Respons HARUS menggunakan format Markdown untuk kejelasan dan struktur yang lebih baik (misalnya, judul, teks tebal, poin-poin).
  - Respons harus disajikan dalam {response_type}.

4. Format Bagian Referensi:
  - Bagian Referensi harus di bawah judul: `### Referensi`
  - Entri daftar referensi harus mengikuti format: `* [n] Judul Dokumen`. Jangan sertakan tanda sisipan (`^`) setelah kurung siku pembuka (`[`).
  - Judul Dokumen dalam sitasi harus mempertahankan bahasa aslinya.
  - Keluarkan setiap sitasi pada baris individual
  - Berikan maksimal 5 sitasi yang paling relevan.
  - Jangan menghasilkan bagian catatan kaki atau komentar, ringkasan, atau penjelasan apa pun setelah referensi.

5. Contoh Bagian Referensi:
```
### Referensi

- [1] Judul Dokumen Satu
- [2] Judul Dokumen Dua
- [3] Judul Dokumen Tiga
```

6. Instruksi Tambahan: {user_prompt}


---Konteks---

{content_data}
"""

PROMPTS_ID["kg_query_context"] = """
Data Knowledge Graph (Entitas):

```json
{entities_str}
```

Data Knowledge Graph (Relasi):

```json
{relations_str}
```

Potongan Dokumen (Setiap entri memiliki reference_id yang merujuk ke `Daftar Dokumen Referensi`):

```json
{text_chunks_str}
```

Daftar Dokumen Referensi (Setiap entri dimulai dengan [reference_id] yang sesuai dengan entri di Potongan Dokumen):

```
{reference_list_str}
```

"""

PROMPTS_ID["naive_query_context"] = """
Potongan Dokumen (Setiap entri memiliki reference_id yang merujuk ke `Daftar Dokumen Referensi`):

```json
{text_chunks_str}
```

Daftar Dokumen Referensi (Setiap entri dimulai dengan [reference_id] yang sesuai dengan entri di Potongan Dokumen):

```
{reference_list_str}
```

"""

PROMPTS_ID["keywords_extraction"] = """---Peran---
Anda adalah pengekstrak kata kunci ahli, mengkhususkan diri dalam menganalisis pertanyaan pengguna untuk sistem Retrieval-Augmented Generation (RAG). Tujuan Anda adalah mengidentifikasi kata kunci tingkat tinggi dan tingkat rendah dalam pertanyaan pengguna yang akan digunakan untuk pengambilan dokumen yang efektif.

---Tujuan---
Diberikan pertanyaan pengguna, tugas Anda adalah mengekstrak dua jenis kata kunci yang berbeda:
1. **high_level_keywords**: untuk konsep atau tema menyeluruh, menangkap maksud inti pengguna, bidang subjek, atau jenis pertanyaan yang diajukan.
2. **low_level_keywords**: untuk entitas atau detail spesifik, mengidentifikasi entitas spesifik, nama diri, istilah teknis, nama produk, atau item konkret.

---Instruksi & Batasan---
1. **Format Output**: Output Anda HARUS berupa objek JSON yang valid dan tidak ada yang lain. Jangan sertakan teks penjelasan, pagar kode markdown (seperti ```json), atau teks lain sebelum atau sesudah JSON. Output akan di-parse langsung oleh parser JSON.
2. **Sumber Kebenaran**: Semua kata kunci harus secara eksplisit berasal dari pertanyaan pengguna, dengan kedua kategori kata kunci tingkat tinggi dan tingkat rendah wajib berisi konten.
3. **Ringkas & Bermakna**: Kata kunci harus berupa kata ringkas atau frasa bermakna. Prioritaskan frasa multi-kata jika merepresentasikan satu konsep. Misalnya, dari "laporan keuangan terbaru PT Bank Mandiri", Anda harus mengekstrak "laporan keuangan terbaru" dan "PT Bank Mandiri" daripada "laporan", "keuangan", "terbaru", dan "Bank".
4. **Penanganan Kasus Tepi**: Untuk pertanyaan yang terlalu sederhana, samar, atau tidak bermakna (misalnya, "halo", "ok", "asdfghjkl"), Anda harus mengembalikan objek JSON dengan daftar kosong untuk kedua jenis kata kunci.
5. **Bahasa**: Semua kata kunci yang diekstrak HARUS dalam {language}. Nama diri (misalnya, nama orang, nama tempat, nama organisasi) harus dipertahankan dalam bahasa aslinya.

---Contoh---
{examples}

---Data Sebenarnya---
Pertanyaan Pengguna: {query}

---Output---
Output:"""

PROMPTS_ID["keywords_extraction_examples"] = [
    """Contoh 1:

Pertanyaan: "Bagaimana dampak vaksinasi COVID-19 terhadap tingkat kematian di Indonesia?"

Output:
{
  "high_level_keywords": ["Dampak vaksinasi COVID-19", "Tingkat kematian", "Kesehatan masyarakat Indonesia"],
  "low_level_keywords": ["Vaksin Sinovac", "Vaksin AstraZeneca", "Kementerian Kesehatan", "Data kematian", "Pandemi"]
}

""",
    """Contoh 2:

Pertanyaan: "Apa saja bukti yang membantah klaim penghapusan pendidikan agama di sekolah negeri?"

Output:
{
  "high_level_keywords": ["Verifikasi fakta", "Kebijakan pendidikan agama", "Klaim hoaks"],
  "low_level_keywords": ["Sekolah negeri", "Kurikulum nasional", "Kementerian Pendidikan", "Perpres", "Mata pelajaran agama"]
}

""",
    """Contoh 3:

Pertanyaan: "Siapa saja pejabat yang terlibat dalam kasus korupsi bantuan sosial 2020?"

Output:
{
  "high_level_keywords": ["Korupsi bantuan sosial", "Keterlibatan pejabat", "Kasus hukum"],
  "low_level_keywords": ["Bansos COVID-19", "KPK", "Kementerian Sosial", "Juliari Batubara", "Tahun 2020"]
}

""",
]
