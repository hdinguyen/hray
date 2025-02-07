from dspy import InputField, OutputField, Signature


class Translator(Signature):
    text: str = InputField(desc="Raw paragraph input")
    character_info: dict = OutputField(desc="Extracted character information including name, age, and personal details")
    actions: list[str] = OutputField(desc="List of actions performed by characters")
    relationships: list[dict] = OutputField(desc="List of relationships between characters")
    cypher_script: str = OutputField(desc="Neo4j Cypher script to add the extracted information to database")
    translated_text: dict = OutputField(desc="Text translated to different languages")

