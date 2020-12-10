# cluster
helm install mygraph https://github.com/neo4j-contrib/neo4j-helm/releases/download/4.2.0-1/neo4j-4.2.0-1.tgz --set acceptLicenseAgreement=yes --set neo4jPassword=dp8cz8SEnfU7

# standalone
$ helm install mygraph https://github.com/neo4j-contrib/neo4j-helm/releases/download/4.2.0-1/neo4j-4.2.0-1.tgz --set core.standalone=true --set acceptLicenseAgreement=yes --set neo4jPassword=dp8cz8SEnfU7
