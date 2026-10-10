import hashlib

from langchain_chroma import Chroma
from lfx.components.chroma import ChromaVectorStoreComponent
from lfx.schema.data import Data


class ProjectChromaComponent(ChromaVectorStoreComponent):
    display_name = "Project Chroma DB"
    description = "Chroma retrieval with stable source/text IDs to avoid re-ingesting unchanged project passages."
    name = "ProjectChroma"

    def _add_documents_to_vector_store(self, vector_store: Chroma) -> None:
        chunks = self._prepare_ingest_data()
        if not chunks:
            return

        documents = {}
        for chunk in chunks:
            if not isinstance(chunk, Data):
                raise TypeError("Project Chroma inputs must be Data objects.")
            document = chunk.to_lc_document()
            source = document.metadata.get("file_path")
            if not isinstance(source, str) or not source:
                raise ValueError("Project passages must retain a nonempty file_path for source attribution.")
            if not document.page_content.strip():
                raise ValueError(f"Project passage from {source} is empty.")
            identifier = hashlib.sha256(
                (source + "\0" + document.page_content).encode("utf-8")
            ).hexdigest()
            document.metadata = {"file_path": source}
            documents[identifier] = document

        existing = set(vector_store.get(ids=list(documents), include=[])["ids"])
        new_ids = [identifier for identifier in documents if identifier not in existing]
        if new_ids:
            vector_store.add_documents([documents[identifier] for identifier in new_ids], ids=new_ids)
        self.log(f"Project index: {len(new_ids)} new passages, {len(existing)} already present.")
