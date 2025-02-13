from typing import List

import dspy
import nltk
from llm.models import anthropic_llm, llm
from llm.tool.vectordb import ChromaDBTool
# from neo4j import GraphDatabase
from logger.log import get_logger

logger = get_logger(__name__)

class VietnameseTerms:
    """Manager for Vietnamese terms and their meanings"""
    def __init__(self):
        self.db = ChromaDBTool("vietnamese_terms")
        # Initialize with some default terms if the collection is empty
        if self.db.collection.count() == 0:
            self._initialize_default_terms()

    def _initialize_default_terms(self):
        default_terms = [
            {"category":"term","phrase": "Đại ca", "meaning": "big brother", "added_by": "auto"},
            {"category":"term","phrase": "Đại hoàng huynh", "meaning": "eldest royal brother", "added_by": "auto"},
            {"category":"term","phrase": "Tiểu đệ", "meaning": "younger brother", "added_by": "auto"},
            # Add more default terms as needed
        ]
        # Add terms to the database
        for term_data in default_terms:
            self.db.add_documents(
                documents=[term_data["term"]],
                metadatas=[{"meaning": term_data["meaning"]}],
                ids=[term_data["term"]]
            )
    def query(self, query_text: str, n_results: int = 3):
        result = self.db.query(query_text, n_results)
        context = []
        for term, metadata in zip(result["documents"][0], result["metadatas"][0]):
            context.append(f"{term}: {metadata['meaning']} ({metadata['category']})")
        return "\n".join(context)

    def add_terms(self, term: str, meaning: str, added_by: str):
        self.db.add_documents(
            documents=[term],
            metadatas=[{"meaning": meaning, "added_by": added_by}],
            ids=[term]
        )

class PharseInterpolate(dspy.Signature):
    """Interpolate text with Vietnamese term in English"""
    term: str = dspy.InputField(desc="Retrieved relevant Vietnamese terms and meanings")
    interpolated_text: str = dspy.OutputField(desc="Meaning of the term in English text")

class ExtractSignature(dspy.Signature):
    """Extract information from text with multiple knowledge support"""
    viet_terms_context: str = dspy.InputField(desc="Retrieved relevant Vietnamese terms and meanings")
    knowledge_context: str = dspy.InputField(desc="Retrieved relevant background knowledge")
    sentence: str = dspy.InputField(desc="Text chunk to be processed")
    new_characters: List[str] = dspy.OutputField(desc="Extracted character names with proper honorifics if any")
    new_terms: List[str] = dspy.OutputField(desc="Extracted new guessed terms if any")
    # time: str = dspy.OutputField(desc="Extracted time if any else indentify the subsequent moment of the input text versus the added context")
    # location: str = dspy.OutputField(desc="Extracted location if any")
    # context_summary: str = dspy.OutputField(desc="Summary of the context from the input text")

class TranslationSignature(dspy.Signature):
    """Translate text from source language to target language with multiple knowledge support"""
    text: str = dspy.InputField(desc="Text to be translated")
    terms:str = dspy.InputField(desc="Retrieved relevant source language terms and meanings")
    relevant_data:str = dspy.InputField(desc="Relevant context from the previous translation chunk")
    translation: str = dspy.OutputField(desc="Translated text")

class RetouchSignature(dspy.Signature):
    """Retouch the translation with multiple knowledge support"""
    text: str = dspy.InputField(desc="Text to be retouched")
    relevant_data:str = dspy.InputField(desc="Relevant context from the previous translation chunk")
    retouched_text: str = dspy.OutputField(desc="Retouched text")

class Translator(dspy.Module):
    def __init__(self, lm: dspy.LM):
        super().__init__()
        # self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        self.storage_db = ChromaDBTool("novel1")  # For storing results
        self.viet_terms_db = VietnameseTerms()

        # Initialize multi-retriever
        # self.retriever = MultiRetriever(self.viet_terms_db, self.knowledge_db)

        # Initialize predictor
        if lm is None:
            self.lm = llm
        else:
            self.lm = lm
        self.predictor = dspy.Predict(ExtractSignature)
        self.predictor.set_lm(self.lm)
        self.translator = dspy.Predict(TranslationSignature)
        self.translator.set_lm(self.lm)
        self.pharse_interpolator = dspy.Predict(PharseInterpolate)
        self.pharse_interpolator.set_lm(self.lm)

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def forward(self, **input_args):
        text = input_args.get('text', '')
        tmp_memory = input_args.get('tmp_memory', None)
        chunks = self.chunk_text(text)

        total_chunks = len(chunks)
        i = 0

        for chunk in chunks:
            # Get relevant context from both databases
            relevant_terms = self.viet_terms_db.query(chunk)
            relevant_context = self.storage_db.query(chunk)["documents"][0]

            # Extract information with both contexts
            extracted_info = self.extract_information(
                chunk,
                relevant_terms,
                relevant_context
            )

            # Store in storage database
            # self._store_extraction(chunk, extracted_info)
            # extracted_results.append(extracted_info)

            tmp_memory.new_terms.append(extracted_info['character'])

            result_text = self.translator(
                text=chunk,
                terms=relevant_terms,
                relevant_data=relevant_context
            ).toDict()
            logger.info(f"Prompt: {dspy.inspect_history(n=1)}")
            tmp_memory.progress = float((i+1) / total_chunks * 100)
            tmp_memory.memory.append(result_text)
            i += 1
        tmp_memory.progress = 100

    def extract_information(self, chunk: str, terms_context: str, knowledge_context: str):
        """Extract information using both retrieved contexts"""
        predictor = self.predictor(
            viet_terms_context=terms_context,
            knowledge_context=knowledge_context,
            sentence=chunk
        )
        result = predictor.toDict()
        logger.info(f"Prompt: {dspy.inspect_history(n=1)}")

        return {
            "character": result['new_characters'],
            "new_terms": result['new_terms'],
            "chunk": chunk,
            "used_terms": terms_context,
            "used_knowledge": knowledge_context
        }

    def _store_extraction(self, chunk: str, extracted_info: dict):
        """Store the chunk and its extracted information"""
        metadata = {
            "character": extracted_info['character'],
            "time": extracted_info['time'],
            "location": extracted_info['location'],
            "action": extracted_info['action'],
            "used_terms": extracted_info['used_terms'],
            "used_knowledge": extracted_info['used_knowledge']
        }

        self.storage_db.add_documents(
            documents=[chunk],
            metadatas=[metadata],
            ids=[f"chunk_{hash(chunk)}"]
        )

    def chunk_text(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """
        Split text into manageable chunks while preserving sentence boundaries.

        Args:
            text (str): Input text to be chunked
            max_chunk_size (int): Maximum size of each chunk in characters

        Returns:
            List[str]: List of text chunks
        """
        # Split text into sentences
        sentences = nltk.sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length <= max_chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                # If current chunk is not empty, add it to chunks
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                # Start new chunk with current sentence
                current_chunk = [sentence]
                current_length = sentence_length

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks


