class AnalyzerFactory:
    def __init__(self):
        self._analyzers = {}

    def register_analyzer(self, event_type, analyzer):
        self._analyzers[event_type] = analyzer

    def get_analyzer(self, event_type):
        return self._analyzers.get(event_type)

class ResolverFactory:
    def __init__(self):
        self._resolvers = {}

    def register_resolver(self, issue_type, resolver):
        self._resolvers[issue_type] = resolver

    def get_resolver(self, issue_type):
        return self._resolvers.get(issue_type)
