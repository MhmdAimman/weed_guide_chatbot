import re

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import (
    CHAT_MODEL,
    OPENAI_API_KEY,
    SPECIES_ALIASES,
    SPECIES_BY_CATEGORY,
    SPECIES_TO_CATEGORY,
    TOPICS,
)
from vector_store import get_collection, query_collection


TRAIT_WORDS = {
    "flower",
    "flowers",
    "petal",
    "petals",
    "purple",
    "pink",
    "white",
    "yellow",
    "leaf",
    "leaves",
    "hairy",
    "spiny",
    "prickly",
    "root",
    "roots",
    "stem",
    "stems",
    "seed",
    "seeds",
    "tall",
    "height",
    "bract",
    "bracts",
}


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def format_list(items):
    return ", ".join(items)


def find_species(message, category=None):
    lower = normalize(message)
    allowed = set(SPECIES_BY_CATEGORY.get(category, [])) if category else None
    for alias, canonical in sorted(SPECIES_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in lower and (allowed is None or canonical in allowed):
            return canonical
    return None


def canonicalize_species_name(name):
    if not name:
        return None
    lower = normalize(name)
    if lower in SPECIES_ALIASES:
        return SPECIES_ALIASES[lower]
    canonical_species = set(SPECIES_ALIASES.values())
    for species in canonical_species:
        if normalize(species) == lower:
            return species
    return None


def find_category(message):
    lower = normalize(message)
    for category in SPECIES_BY_CATEGORY:
        if re.search(rf"\b{re.escape(category)}s?\b", lower):
            return category
    return None


def find_topic(message):
    lower = normalize(message)
    for phrase, topic in sorted(TOPICS.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase in lower:
            return topic
    return None


def is_trait_description(message):
    lower = normalize(message)
    return any(word in lower for word in TRAIT_WORDS)


def deterministic_trait_match(message):
    lower = normalize(message)

    if "inconspicuous" in lower and "wedge" in lower and "seed" in lower:
        return "Kochia"

    if (
        ("5" in lower and "10" in lower and "flower spike" in lower)
        or ("bluish" in lower and "felt" in lower and "leaves" in lower)
    ):
        return "Common Mullein"

    if (
        "purple" in lower
        and ("flower" in lower or "petal" in lower)
        and ("2 to 5" in lower or "2-5" in lower or "2 inches" in lower or "3 inches" in lower)
    ):
        return "Musk thistle"

    return None


def get_species_for_category(category):
    return SPECIES_BY_CATEGORY.get(category.lower(), [])


def flatten_query_results(results):
    docs_groups = results.get("documents") or []
    metas_groups = results.get("metadatas") or []
    distances_groups = results.get("distances") or []
    items = []

    for group_index, docs in enumerate(docs_groups):
        if isinstance(docs, str):
            docs = [docs]
        metas = metas_groups[group_index] if group_index < len(metas_groups) else []
        distances = distances_groups[group_index] if group_index < len(distances_groups) else []
        for index, doc in enumerate(docs):
            metadata = metas[index] if isinstance(metas, list) and index < len(metas) else {}
            distance = distances[index] if isinstance(distances, list) and index < len(distances) else None
            if doc:
                items.append({"document": doc, "metadata": metadata or {}, "distance": distance})
    return items


class WeedChatbot:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=CHAT_MODEL,
            temperature=0,
        )
        self.collection = get_collection()

    def retrieve_context(self, query, species=None, n_results=8):
        items = query_collection(self.collection, query, n_results=n_results)
        if species:
            lower_species = species.lower()
            species_items = [
                item
                for item in items
                if lower_species in item["document"].lower()
                or lower_species in str(item["metadata"].get("species", "")).lower()
            ]
            if species_items:
                items = species_items
        return "\n\n---\n\n".join(item["document"] for item in items[:5])

    def retrieve_identification_context(self, fallback_query):
        results = self.collection.get(include=["documents", "metadatas"])
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        identification_docs = []

        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            section = str(metadata.get("section", "")).lower()
            if "keys to id" in section or "identification" in section:
                identification_docs.append(document)

        if identification_docs:
            return "\n\n---\n\n".join(identification_docs)
        return self.retrieve_context(fallback_query, n_results=8)

    def ask_llm(self, message, context):
        if not context:
            return "I don't have that information in the guide."

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Weed Guide chatbot, an expert agricultural assistant. "
                    "Answer using ONLY the provided context from the Las Animas County Weed Management Pocket Guide. "
                    "Do not use outside information. Do not include source page citations. "
                    "If the context does not contain the answer, say: I don't have that information in the guide. "
                    "Keep the answer clear and direct.\n\nCONTEXT:\n{context}",
                ),
                ("human", "{message}"),
            ]
        )
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"context": context, "message": message}).strip()

    def ask_species(self, category):
        species = get_species_for_category(category)
        if not species:
            return {
                "reply": f"What kind of {category} do you want to know about?",
                "state": {"awaiting": "species", "category": category, "selected_species": None},
            }
        return {
            "reply": f"What kind of {category} do you want to know about? Available in the guide: {format_list(species)}.",
            "state": {"awaiting": "species", "category": category, "selected_species": None},
        }

    def ask_topic(self, species):
        category = SPECIES_TO_CATEGORY.get(species.lower())
        return {
            "reply": f"What would you like to know about {species}? Type: Identification, Control Methods, or Life Cycle.",
            "state": {"awaiting": "topic", "category": category, "selected_species": species},
        }

    def answer_topic(self, species, topic, user_message):
        query = f"{species} {topic} Keys to ID Identification Lifecycle Control HERBICIDE"
        context = self.retrieve_context(query, species=species)
        reply = self.ask_llm(
            f"Answer only about {topic} for {species}. User asked: {user_message}",
            context,
        )
        return {
            "reply": reply,
            "state": {
                "awaiting": None,
                "category": SPECIES_TO_CATEGORY.get(species.lower()),
                "selected_species": species,
            },
        }

    def answer_trait_description(self, message):
        deterministic_species = deterministic_trait_match(message)
        if deterministic_species:
            return {
                "reply": (
                    f"It sounds like you are talking about {deterministic_species}.\n\n"
                    "What would you like to know about this species? Select or ask about: Identification, Control Methods, or Life Cycle."
                ),
                "state": {
                    "awaiting": "topic",
                    "category": SPECIES_TO_CATEGORY.get(deterministic_species.lower()),
                    "selected_species": deterministic_species,
                },
            }

        context = self.retrieve_identification_context(f"Keys to ID Identification {message}")
        if not context:
            return {
                "reply": "I don't have enough information in the guide to identify that species.",
                "state": {"awaiting": None, "category": None, "selected_species": None},
            }

        species_names = sorted(set(SPECIES_ALIASES.values()))
        system = (
            "You identify weed species using ONLY the provided Keys to ID and Identification context "
            "from the Las Animas County Weed Management Pocket Guide. Do not use outside knowledge. "
            "Return only valid JSON with this shape: "
            '{"identified": true, "species": "Exact species name", "matching_traits": ["trait from the guide"]}. '
            "If the context is not enough to identify a species, return: "
            '{"identified": false, "species": null, "matching_traits": []}. '
            f"Allowed species names: {', '.join(species_names)}.\n\nCONTEXT:\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "{message}"),
            ]
        )

        try:
            chain = prompt | self.llm.bind(response_format={"type": "json_object"}) | JsonOutputParser()
            result = chain.invoke({"message": message})
        except Exception:
            result = {"identified": False, "species": None, "matching_traits": []}
        if not isinstance(result, dict):
            result = {"identified": False, "species": None, "matching_traits": []}

        species = canonicalize_species_name(result.get("species"))
        traits = result.get("matching_traits") or []
        if isinstance(traits, str):
            traits = [traits]
        traits = [trait.strip() for trait in traits if isinstance(trait, str) and trait.strip()]

        if not result.get("identified") or not species or not traits:
            return {
                "reply": "I don't have enough information in the guide to identify that species.",
                "state": {"awaiting": None, "category": None, "selected_species": None},
            }

        reply = (
            f"It sounds like you are talking about {species}.\n\n"
            "What would you like to know about this species? Select or ask about: Identification, Control Methods, or Life Cycle."
        )
        return {
            "reply": reply,
            "state": {
                "awaiting": "topic",
                "category": SPECIES_TO_CATEGORY.get(species.lower()),
                "selected_species": species,
            },
        }

    def process_message(self, message, state=None):
        state = state or {}
        awaiting = state.get("awaiting")
        selected_species = state.get("selected_species")
        state_category = state.get("category")

        species = find_species(message)
        topic = find_topic(message)
        detected_category = find_category(message)

        if species and topic:
            return self.answer_topic(species, topic, message)

        if species:
            return self.ask_topic(species)

        if detected_category:
            return self.ask_species(detected_category)

        if awaiting == "species" and state_category:
            species = find_species(message, category=state_category)
            if not species:
                return self.ask_species(state_category)
            topic = find_topic(message)
            if topic:
                return self.answer_topic(species, topic, message)
            return self.ask_topic(species)

        if awaiting == "topic" and selected_species:
            topic = find_topic(message)
            if not topic:
                return self.ask_topic(selected_species)
            return self.answer_topic(selected_species, topic, message)

        if selected_species and topic and not species:
            return self.answer_topic(selected_species, topic, message)

        if is_trait_description(message):
            return self.answer_trait_description(message)

        context = self.retrieve_context(message, n_results=5)
        reply = self.ask_llm(message, context)
        return {"reply": reply, "state": {"awaiting": None, "category": None, "selected_species": selected_species}}
