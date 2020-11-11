CALL n10s.graphconfig.init({
  handleVocabUris: 'MAP', 
  handleMultival: 'ARRAY', 
  keepLangTag: true, 
  keepCustomDataTypes: true, 
  applyNeo4jNaming: true 
})

# for each configuration
# Setting handleVocabUris to MAP instructs neosemantics to apply mappings to schema elements as they are added to the graph using the n10s.nsprefixes.add and n10s.mapping.add procedures
# This setting ensures that multiple values are stored in Neo4j as an array, in this case we’re interested in the rdf:label of the element in multiple languages.
# Keeping the language tag will mean that each translated property will be suffixed, eg: United Kingdom@en or Regno Unito@it
# This setting ensures that any custom (user defined non- XML Schema) data types are also saved in Neo4j as a string, followed by their data type URI.
# Apply Neo4j recommended naming to Graph Elements - All capital letters for relationship types, Upper Camel Case for labels, etc.