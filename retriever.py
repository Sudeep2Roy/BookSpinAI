class IntelligentRetriever:
    def __init__(self, version_manager):
        self.vm = version_manager
    
    def retrieve_content(self, query, n_results=1):
        results = self.vm.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results