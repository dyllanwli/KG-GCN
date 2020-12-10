# cluster
helm install mygraph RELEASE_URL --set acceptLicenseAgreement=yes --set neo4jPassword=dp8cz8SEnfU7

# standalone
$ helm install mygraph RELEASE_URL --set core.standalone=true --set acceptLicenseAgreement=yes --set neo4jPassword=dp8cz8SEnfU7
